import imagej
import numpy as np
from scipy import ndimage
from skimage import filters, measure, segmentation, morphology
from skimage.measure import regionprops
import cv2
from biobridge.blocks.cell import Cell, Dict, List, Optional, json, Organelle, Mitochondrion
from biobridge.definitions.cells.stem_cell import StemCell
from biobridge.definitions.cells.epithelial_cell import EpithelialCell
from biobridge.definitions.cells.somatic_cell import SomaticCell
from biobridge.blocks.tissue import Tissue
import matplotlib.pyplot as plt
from pyrosetta import pose_from_pdb
from pyrosetta.toolbox import cleanATOM
from pyrosetta.rosetta.protocols.rosetta_scripts import XmlObjects
from pyrosetta.rosetta.core.scoring import get_score_function
from biobridge.tools.xray_analyzer import XrayAnalyzer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
from biobridge.blocks.protein import Protein
from biobridge.definitions.tissues.neural import NeuralTissue, Neuron


class ImageAnalyzer:
    def __init__(self):
        """Initialize the ImageAnalyzer with ImageJ."""
        self.ij = imagej.init()
        self.labeled_tissue = ""
        self.xray_analyzer = XrayAnalyzer(self)
        self.protein_classifier = None
        self.scaler = StandardScaler()

    def load_image(self, image_path: str):
        """Load an image using ImageJ."""
        return self.ij.io().open(image_path)

    def segment_image(self, imagej_dataset):
        """Segment the image to identify individual cells or regions."""

        # Convert ImageJ dataset to a NumPy array
        image_np = self.ij.py.from_java(imagej_dataset)

        # Ensure the image is in grayscale and uint8
        if len(image_np.shape) == 3:  # If the image is colored (3 channels)
            image_gray = self.grayscale_image(image_np)
        elif len(image_np.shape) == 2:  # If the image is already grayscale
            image_gray = image_np
        else:
            raise ValueError("Input image has an unexpected number of dimensions.")

        # Ensure the image is in the right format (uint8)
        if image_gray.dtype != np.uint8:
            image_gray = self.grayscale_image(image_np)

        image_gray_np = image_gray.values
        # Apply Otsu's thresholding
        _, binary = cv2.threshold(image_gray_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Perform morphological operations to clean up the binary image
        kernel = np.ones((3, 3), np.uint8)
        clean_binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)  # Close gaps
        clean_binary = cv2.morphologyEx(clean_binary, cv2.MORPH_OPEN, kernel)  # Remove small noise

        # Label connected components
        labeled_img, num_labels = measure.label(clean_binary, connectivity=2, return_num=True)

        return labeled_img, num_labels

    def measure_fluorescence(self, image):
        """Measure fluorescence intensity in the image."""
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # Measure mean and max intensity
        mean_intensity = np.mean(img_array)
        max_intensity = np.max(img_array)

        return {
            "mean_intensity": mean_intensity,
            "max_intensity": max_intensity
        }

    def track_cell_movement(self, image_sequence):
        """Track cell movement across a sequence of images."""
        tracked_cells = []

        for i, image in enumerate(image_sequence):
            # Segment the image to identify cells
            segmented = self.segment_image(image)

            # Check the type and structure of the segmented result
            segmented_array = np.array(segmented[0])

            # Ensure segmented_array is a 2D or 3D array
            if segmented_array.ndim not in [2, 3]:
                raise ValueError(f"Expected a 2D or 3D array, but got an array with {segmented_array.ndim} dimensions.")

            # Apply label function
            labeled = measure.label(segmented_array)

            # Get properties of labeled regions
            props = measure.regionprops(labeled)

            # If this is the first image, initialize tracked cells
            if i == 0:
                tracked_cells = [{'centroid': prop.centroid, 'trajectory': [prop.centroid]} for prop in props]
            else:
                # For subsequent images, match cells to existing trajectories
                distances = np.zeros((len(tracked_cells), len(props)))
                for j, cell in enumerate(tracked_cells):
                    last_position = cell['trajectory'][-1]
                    for k, prop in enumerate(props):
                        distances[j, k] = np.linalg.norm(np.array(last_position) - np.array(prop.centroid))

                # Use the Hungarian algorithm to match cells to existing trajectories
                from scipy.optimize import linear_sum_assignment
                row_ind, col_ind = linear_sum_assignment(distances)

                # Add the new position to the trajectory
                for j, k in zip(row_ind, col_ind):
                    tracked_cells[j]['trajectory'].append(props[k].centroid)

                # Handle the case where a cell disappears or a new cell appears
                for j, cell in enumerate(tracked_cells):
                    if j not in row_ind:
                        # Cell disappeared
                        cell['trajectory'].append(None)
                    else:
                        # Cell was matched
                        pass
                for k, prop in enumerate(props):
                    if k not in col_ind:
                        # New cell appeared
                        tracked_cells.append({'centroid': prop.centroid, 'trajectory': [prop.centroid]})

        return tracked_cells

    def grayscale_image(self, image):
        """Convert the image to grayscale."""
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # If the image is already grayscale, return it as is
        if len(img_array.shape) == 2:
            return image

        # If the image is RGB, convert to grayscale
        grayscale = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140])

        # Convert back to ImageJ image
        return self.ij.py.to_java(grayscale)

    def analyze_nuclei(self, image):
        """Analyze nuclei in the image."""
        # Apply the threshold to the image
        binary = self.ij.op().threshold().otsu(image)
        binary_np = self.ij.py.from_java(binary)

        # Convert to boolean type (important for further processing)
        binary_np = binary_np.astype(bool)

        # Label nuclei
        labeled_nuclei = measure.label(binary_np)

        # Measure properties of each nucleus
        img_array = self.ij.py.from_java(image)  # Convert the original image to a numpy array
        props = measure.regionprops(labeled_nuclei, img_array)

        nuclei_data = []
        for prop in props:
            nucleus = {
                'area': prop.area,
                'perimeter': prop.perimeter,
                'eccentricity': prop.eccentricity,
                'mean_intensity': np.mean(prop.intensity_image),
                'centroid': (prop.centroid[1], prop.centroid[0])  # Note the swap of coordinates
            }
            nuclei_data.append(nucleus)

        return nuclei_data

    def analyze_mitochondria(self, image):
        """Analyze mitochondria in the image."""
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # Enhance mitochondria visibility (assuming they're brighter)
        enhanced = filters.meijering(img_array)

        # Threshold the enhanced image
        thresh = filters.threshold_otsu(enhanced)
        binary = enhanced > thresh

        # Label mitochondria
        labeled_mito = measure.label(binary)

        # Measure properties of each mitochondrion
        props = measure.regionprops(labeled_mito, img_array)

        mito_data = []
        for prop in props:
            mito = {
                'area': prop.area,
                'perimeter': prop.perimeter,
                'mean_intensity': np.mean(prop.intensity_image),
                'centroid': (prop.centroid[1], prop.centroid[0])  # Note the swap of coordinates
            }
            mito_data.append(mito)

        return mito_data

    def detect_potential_cancer(self, image, nuclei_data):
        """Detect potential cancer based on nuclear characteristics."""
        potential_cancer_cells = []

        for nucleus in nuclei_data:
            # Check for characteristics associated with cancer cells
            if (nucleus['area'] > 1.5 * np.mean([n['area'] for n in nuclei_data]) or
                    nucleus['eccentricity'] > 0.8 or
                    nucleus['mean_intensity'] > 1.5 * np.mean([n['mean_intensity'] for n in nuclei_data])):
                potential_cancer_cells.append({
                    'centroid': nucleus['centroid'],
                    'area': nucleus['area'],
                    'eccentricity': nucleus['eccentricity'],
                    'mean_intensity': nucleus['mean_intensity']
                })

        return potential_cancer_cells

    def identify_primary_objects(self, image, min_diameter=10, max_diameter=100):
        """
        Identify primary objects (e.g., nuclei) in the image.

        :param image: Input image (ImageJ DataArray)
        :param min_diameter: Minimum diameter of objects to consider
        :param max_diameter: Maximum diameter of objects to consider
        :return: Labeled image of primary objects
        """

        # Apply Otsu thresholding using ImageJ and convert the result to a NumPy array
        binary = self.ij.op().threshold().otsu(image)
        binary_np = self.ij.py.from_java(binary)

        # Convert to boolean type (important for further processing)
        binary_np = binary_np.astype(bool)

        # Remove small objects and fill holes
        cleaned = morphology.remove_small_objects(binary_np, min_size=min_diameter ** 2)
        filled = ndimage.binary_fill_holes(cleaned)

        # Label objects
        labeled = measure.label(filled)

        # Filter objects by size
        sizes = np.bincount(labeled.ravel())
        mask_sizes = (sizes > (np.pi * (min_diameter / 2) ** 2)) & (sizes < (np.pi * (max_diameter / 2) ** 2))
        mask_sizes[0] = 0
        labeled = mask_sizes[labeled]

        return labeled

    def identify_secondary_objects(self, primary_objects, distance=5):
        """
        Identify secondary objects (e.g., cell bodies) based on primary objects.

        :param primary_objects: Labeled image of primary objects
        :param distance: Maximum distance to expand from primary objects
        :return: Labeled image of secondary objects
        """
        # Convert primary_objects to a binary mask in NumPy
        primary_mask = primary_objects > 0

        # Dilate the mask using skimage morphology
        dilated = morphology.binary_dilation(primary_mask, morphology.disk(distance))

        # Compute the distance transform on the dilated mask
        distance_transform = ndimage.distance_transform_edt(dilated)

        # Identify markers for watershed using local maxima
        local_maxi = morphology.local_maxima(distance_transform)

        # Convert local_maxi to integer labels (required for watershed)
        markers = measure.label(local_maxi)

        # Apply watershed algorithm
        labels = segmentation.watershed(-distance_transform, markers, mask=dilated)

        return labels

    def identify_tertiary_objects(self, secondary_objects, primary_objects):
        """
        Identify tertiary objects (e.g., cytoplasm) as the difference between secondary and primary objects.

        :param secondary_objects: Labeled image of secondary objects
        :param primary_objects: Labeled image of primary objects
        :return: Labeled image of tertiary objects
        """
        tertiary_objects = np.zeros_like(secondary_objects)
        for i in range(1, np.max(secondary_objects) + 1):
            secondary_mask = secondary_objects == i
            primary_mask = primary_objects > 0
            tertiary_objects[secondary_mask & ~primary_mask] = i

        return tertiary_objects

    def measure_object_properties(self, labeled_image, intensity_image):
        """
        Measure properties of labeled objects.

        :param labeled_image: Labeled image of objects
        :param intensity_image: Original intensity image (ImageJ DataArray)
        :return: List of dictionaries containing object properties
        """
        # Ensure labeled_image is of integer type
        if not np.issubdtype(labeled_image.dtype, np.integer):
            labeled_image = labeled_image.astype(np.int32)

        # Convert intensity_image to numpy array
        intensity_np = self.ij.py.from_java(intensity_image)

        # Measure region properties
        intensity_np = np.array(intensity_np)
        intensity_np = intensity_np.reshape(labeled_image.shape)

        object_properties = []
        for prop in regionprops(labeled_image, intensity_image=intensity_np):
            properties = {
                'label': prop.label,
                'area': prop.area,
                'perimeter': prop.perimeter,
                'centroid': prop.centroid,
                'mean_intensity': prop.mean_intensity,
                'max_intensity': prop.max_intensity,
                'min_intensity': prop.min_intensity,
                'eccentricity': prop.eccentricity,
                'solidity': prop.solidity,
                'major_axis_length': prop.major_axis_length,
                'minor_axis_length': prop.minor_axis_length,
                'orientation': prop.orientation
            }
            object_properties.append(properties)

        return object_properties

    def analyze_cellular_objects(self, image):
        """
        Perform a complete analysis of cellular objects in the image.

        :param image: Input image
        :return: Dictionary containing analysis results
        """
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # Identify objects
        primary_objects = self.identify_primary_objects(image)
        secondary_objects = self.identify_secondary_objects(primary_objects)
        tertiary_objects = self.identify_tertiary_objects(secondary_objects, primary_objects)

        # Measure properties
        primary_properties = self.measure_object_properties(primary_objects, img_array)
        secondary_properties = self.measure_object_properties(secondary_objects, img_array)
        tertiary_properties = self.measure_object_properties(tertiary_objects, img_array)

        return {
            'primary_objects': primary_properties,
            'secondary_objects': secondary_properties,
            'tertiary_objects': tertiary_properties
        }

    def analyze_network_image(self, image_path):
        """
        Analyze a network image to detect nodes, edges, and arrows.

        :param image_path: Path to the network image
        :return: Dictionary containing nodes, edges, and their properties
        """
        # Load the image
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect nodes (assuming nodes are circular)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=50, param2=30, minRadius=15, maxRadius=40)

        nodes = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                nodes.append({
                    'center': (i[0], i[1]),
                    'radius': i[2],
                    'color': image[i[1], i[0]].tolist()  # Get color of the node
                })

        # Detect edges and arrows
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

        edge_list = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                edge_list.append({
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'weight': np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2]))  # Use length as weight
                })

        arrow_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
        arrow_points = cv2.dilate(edges, arrow_kernel, iterations=1)
        arrow_points = cv2.findNonZero(arrow_points)

        arrows = []
        if arrow_points is not None:
            for point in arrow_points:
                x, y = point[0]
                arrows.append((x, y))

        return {
            'nodes': nodes,
            'edges': edge_list,
            'arrows': arrows
        }

    def analyze_neuron_morphology(
            self, image, nucleus_props: Dict, cell_props: Dict,
    ) -> Dict[str, float]:
        soma_diameter = 2 * np.sqrt(nucleus_props['area'] / np.pi)

        soma_perimeter = nucleus_props['perimeter']
        soma_circularity = (
            4 * np.pi * nucleus_props['area'] / (soma_perimeter ** 2)
            if soma_perimeter > 0 else 0
        )

        nucleus_labeled = self.identify_primary_objects(image)
        cell_bodies_labeled = self.identify_secondary_objects(nucleus_labeled)

        nucleus_mask = nucleus_labeled == nucleus_props['label']
        cell_mask = cell_bodies_labeled == cell_props['label']

        skeleton = morphology.skeletonize(cell_mask)
        distance_transform = ndimage.distance_transform_edt(cell_mask)

        process_pixels = skeleton & ~nucleus_mask
        process_lengths = np.sum(process_pixels)

        labeled_processes = measure.label(process_pixels)
        process_count = np.max(labeled_processes)

        branch_points = self._detect_branch_points(skeleton)
        branch_density = (
            np.sum(branch_points) / process_lengths
            if process_lengths > 0 else 0
        )

        process_diameters = distance_transform[process_pixels] * 2
        avg_process_diameter = (
            np.mean(process_diameters) if len(process_diameters) > 0 else 0
        )

        max_distance = np.max(
            distance_transform[nucleus_mask]
        ) if np.any(nucleus_mask) else 0
        estimated_axon_length = max_distance * 2

        return {
            "soma_diameter": soma_diameter,
            "soma_circularity": soma_circularity,
            "process_count": int(process_count),
            "total_process_length": float(process_lengths),
            "branch_density": branch_density,
            "average_process_diameter": avg_process_diameter,
            "estimated_axon_length": estimated_axon_length,
            "arbor_complexity": process_count * branch_density
        }

    def _detect_branch_points(self, skeleton):
        kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
        neighbor_count = ndimage.convolve(
            skeleton.astype(np.uint8), kernel, mode='constant'
        )
        return (neighbor_count > 2) & skeleton

    def estimate_myelination(
            self, image, cell_props: Dict
    ) -> Dict[str, float]:
        img_array = self.ij.py.from_java(image)
        if hasattr(img_array, 'values'):
            img_array = img_array.values

        nucleus_labeled = self.identify_primary_objects(image)
        cell_bodies_labeled = self.identify_secondary_objects(nucleus_labeled)
        cell_mask = cell_bodies_labeled == cell_props['label']

        nucleus_mask = nucleus_labeled > 0

        process_mask = cell_mask & ~nucleus_mask

        process_intensities = img_array[process_mask]

        if len(process_intensities) == 0:
            return {
                "myelin_thickness": 0.0,
                "myelination_index": 0.0,
                "is_myelinated": False
            }

        intensity_std = np.std(process_intensities)
        intensity_mean = np.mean(process_intensities)

        peripheral_ring = morphology.binary_dilation(
            process_mask, morphology.disk(2)
        ) & ~process_mask
        peripheral_intensity = (
            np.mean(img_array[peripheral_ring])
            if np.any(peripheral_ring) else intensity_mean
        )

        intensity_contrast = (
            peripheral_intensity / intensity_mean
            if intensity_mean > 0 else 1.0
        )

        is_myelinated = intensity_contrast > 1.2 and intensity_std > 15

        myelin_thickness = 0.0
        if is_myelinated:
            distance_transform = ndimage.distance_transform_edt(process_mask)
            avg_process_radius = np.mean(distance_transform[process_mask])
            myelin_thickness = max(0, avg_process_radius * 0.3)

        myelination_index = (
            intensity_contrast * (intensity_std / 50)
            if is_myelinated else 0.0
        )

        return {
            "myelin_thickness": myelin_thickness,
            "myelination_index": min(1.0, myelination_index),
            "is_myelinated": is_myelinated,
            "intensity_contrast": intensity_contrast
        }

    def analyze_synaptic_markers(
            self, image, cell_props: Dict
    ) -> Dict[str, any]:
        img_array = self.ij.py.from_java(image)
        if hasattr(img_array, 'values'):
            img_array = img_array.values

        nucleus_labeled = self.identify_primary_objects(image)
        cell_bodies_labeled = self.identify_secondary_objects(nucleus_labeled)
        cell_mask = cell_bodies_labeled == cell_props['label']

        nucleus_mask = nucleus_labeled > 0
        process_mask = cell_mask & ~nucleus_mask

        if not np.any(process_mask):
            return {
                "estimated_synapse_count": 0,
                "synaptic_density": 0.0,
                "puncta_locations": []
            }

        process_img = img_array * process_mask

        local_maxima = morphology.local_maxima(
            filters.gaussian(process_img, sigma=1.5)
        )

        threshold = filters.threshold_otsu(process_img[process_mask])
        bright_puncta = (process_img > threshold * 1.3) & process_mask

        labeled_puncta = measure.label(bright_puncta & local_maxima)
        puncta_props = measure.regionprops(labeled_puncta)

        valid_puncta = [
            p for p in puncta_props
            if 2 <= p.area <= 50 and p.mean_intensity > threshold
        ]

        puncta_locations = [
            {"centroid": p.centroid, "intensity": p.mean_intensity}
            for p in valid_puncta
        ]

        process_area = np.sum(process_mask)
        synaptic_density = (
            len(valid_puncta) / process_area * 1000
            if process_area > 0 else 0
        )

        estimated_synapse_count = int(len(valid_puncta) * 5)

        return {
            "estimated_synapse_count": estimated_synapse_count,
            "synaptic_density": synaptic_density,
            "puncta_count": len(valid_puncta),
            "puncta_locations": puncta_locations
        }

    def classify_neuron_type(
            self, morphology_data: Dict, synapse_data: Dict,
            myelination_data: Dict
    ) -> str:
        process_count = morphology_data.get('process_count', 0)
        arbor_complexity = morphology_data.get('arbor_complexity', 0)
        is_myelinated = myelination_data.get('is_myelinated', False)
        synaptic_density = synapse_data.get('synaptic_density', 0)

        if process_count == 1 and is_myelinated:
            return "unipolar_neuron"
        elif process_count == 2:
            return "bipolar_neuron"
        elif process_count >= 3:
            if arbor_complexity > 5 and synaptic_density > 0.1:
                return "multipolar_pyramidal_neuron"
            elif arbor_complexity > 3:
                return "multipolar_stellate_neuron"
            else:
                return "multipolar_neuron"
        else:
            return "unclassified_neuron"

    def estimate_neurotransmitter_type(
            self, image, cell_props: Dict
    ) -> List[str]:
        img_array = self.ij.py.from_java(image)
        if hasattr(img_array, 'values'):
            img_array = img_array.values

        nucleus_labeled = self.identify_primary_objects(image)
        cell_bodies_labeled = self.identify_secondary_objects(nucleus_labeled)
        cell_mask = cell_bodies_labeled == cell_props['label']

        cell_intensity = np.mean(img_array[cell_mask])
        cell_area = cell_props['area']
        eccentricity = cell_props.get('eccentricity', 0.5)

        neurotransmitters = []

        if cell_intensity > 120:
            neurotransmitters.append("glutamate")

        if 80 <= cell_intensity <= 120 and cell_area > 1000:
            neurotransmitters.append("GABA")

        if cell_intensity < 100 and eccentricity > 0.7:
            neurotransmitters.append("dopamine")

        if cell_area > 1500 and cell_intensity > 100:
            neurotransmitters.append("acetylcholine")

        if len(neurotransmitters) == 0:
            neurotransmitters.append("glutamate")

        return neurotransmitters

    def analyze_mitochondrial_distribution_neuron(
            self, image, cell_props: Dict
    ) -> Dict[str, float]:
        img_array = self.ij.py.from_java(image)
        if hasattr(img_array, 'values'):
            img_array = img_array.values

        enhanced = filters.meijering(img_array)
        thresh = filters.threshold_otsu(enhanced)
        binary = enhanced > thresh

        nucleus_labeled = self.identify_primary_objects(image)
        cell_bodies_labeled = self.identify_secondary_objects(nucleus_labeled)
        cell_mask = cell_bodies_labeled == cell_props['label']

        nucleus_mask = nucleus_labeled > 0

        soma_mask = cell_mask & nucleus_mask
        process_mask = cell_mask & ~nucleus_mask

        mito_in_cell = binary & cell_mask
        mito_in_soma = binary & soma_mask
        mito_in_processes = binary & process_mask

        soma_area = np.sum(soma_mask)
        process_area = np.sum(process_mask)

        soma_density = (
            np.sum(mito_in_soma) / soma_area if soma_area > 0 else 0
        )
        process_density = (
            np.sum(mito_in_processes) / process_area
            if process_area > 0 else 0
        )

        labeled_mito = measure.label(mito_in_cell)
        mito_count = np.max(labeled_mito)

        return {
            "total_mitochondria": int(mito_count),
            "soma_mitochondrial_density": soma_density,
            "process_mitochondrial_density": process_density,
            "density_ratio": (
                soma_density / process_density
                if process_density > 0 else 1.0
            )
        }

    def create_neuron_object(
            self, index: int, cell_props: Dict, 
            nucleus_props: Dict, image, dna: Optional[str] = None
    ) -> Neuron:
        morphology = self.analyze_neuron_morphology(
            image, nucleus_props, cell_props
        )

        myelination = self.estimate_myelination(image, cell_props)

        synapse_data = self.analyze_synaptic_markers(image, cell_props)

        neuron_type = self.classify_neuron_type(
            morphology, synapse_data, myelination
        )

        neurotransmitters = self.estimate_neurotransmitter_type(
            image, cell_props
        )

        mito_distribution = self.analyze_mitochondrial_distribution_neuron(
            image, cell_props
        )

        common_props = {
            "name": f"Neuron_{index}",
            "cell_type": "neuron",
            "dna": dna,
            "health": int(100 * (cell_props['mean_intensity'] / 255))
        }

        neuron = Neuron(
            **common_props,
            cell_type=neuron_type,
            soma_diameter=morphology['soma_diameter'],
            axon_length=morphology['estimated_axon_length'],
            axon_diameter=morphology['average_process_diameter'],
            dendrite_count=int(max(1, morphology['process_count'] - 1)),
            dendrite_branch_density=min(1.0, morphology['branch_density'] * 10),
            myelin_thickness=myelination['myelin_thickness'],
            synapse_count=synapse_data['estimated_synapse_count'],
            neurotransmitter_types=neurotransmitters
        )

        neuron_receptors = [
            "NMDA Receptors",
            "AMPA Receptors",
            "GABA_A Receptors",
            "Voltage-gated Na+ Channels",
            "Voltage-gated K+ Channels",
            "Voltage-gated Ca2+ Channels"
        ]

        neuron_surface_proteins = [
            "Neural Cell Adhesion Molecule (NCAM)",
            "L1CAM",
            "Synaptophysin",
            "PSD-95",
            "Neuroligin",
            "Neurexin"
        ]

        neuron.receptors = np.random.choice(
            neuron_receptors, size=np.random.randint(3, 5), replace=False
        ).tolist()
        neuron.surface_proteins = np.random.choice(
            neuron_surface_proteins,
            size=np.random.randint(2, 4),
            replace=False
        ).tolist()

        neuron.add_organelle(Organelle("nucleus", 1))

        num_mitochondria = mito_distribution['total_mitochondria']
        for _ in range(num_mitochondria):
            neuron.add_mitochondrion(
                efficiency=np.random.uniform(0.85, 1.0), health=100
            )

        neuron.metabolism_rate = 1.2 + (
                synapse_data['synaptic_density'] * 0.5
        )

        return neuron

    def create_neural_tissue_object(
            self, index: int, tissue_type: str, tissue_props: Dict,
            neurons: List[Neuron]
    ) -> NeuralTissue:
        tissue_name = f"NeuralTissue_{index}"

        if not neurons:
            return NeuralTissue(
                name=tissue_name,
                tissue_type="nervous",
                cells=neurons,
                cancer_risk=0.0001
            )

        avg_synapse_count = np.mean([n.synapse_count for n in neurons])

        myelinated_count = sum(
            1 for n in neurons if n.myelin_thickness > 0
        )
        myelination_pct = myelinated_count / len(neurons)

        avg_health = np.mean([n.health for n in neurons])

        neural_density = len(neurons) / tissue_props.get('area', 1000)

        synaptic_connectivity = min(1.0, avg_synapse_count / 1000 * 0.7)

        vascularization = 0.8 if avg_health > 70 else 0.6

        neural_tissue = NeuralTissue(
            name=tissue_name,
            tissue_type=tissue_type,
            cells=neurons,
            cancer_risk=0.0001,
            neural_density=neural_density,
            synaptic_connectivity=synaptic_connectivity,
            myelination_percentage=myelination_pct,
            vascularization=vascularization
        )

        neural_tissue.growth_rate = 0.01
        neural_tissue.healing_rate = 0.05 * (avg_health / 100)

        if avg_health < 50:
            neural_tissue.blood_brain_barrier_integrity = 70.0

        neural_tissue.neurotrophic_factor_concentration = avg_health / 100

        return neural_tissue

    def analyze_neural_connectivity_patterns(
            self, neurons_props: List[Dict]
    ) -> Dict[str, any]:
        if len(neurons_props) < 2:
            return {"connectivity_matrix": [], "network_metrics": {}}

        connectivity_matrix = np.zeros(
            (len(neurons_props), len(neurons_props))
        )

        for i, neuron_i in enumerate(neurons_props):
            for j, neuron_j in enumerate(neurons_props):
                if i == j:
                    continue

                centroid_i = np.array(neuron_i['centroid'])
                centroid_j = np.array(neuron_j['centroid'])

                distance = np.linalg.norm(centroid_i - centroid_j)

                max_distance = 500
                if distance < max_distance:
                    connection_strength = 1 - (distance / max_distance)
                    connectivity_matrix[i, j] = connection_strength

        avg_connectivity = np.mean(connectivity_matrix[connectivity_matrix > 0])

        node_degrees = np.sum(connectivity_matrix > 0.3, axis=1)
        avg_degree = np.mean(node_degrees)

        hub_neurons = np.where(node_degrees > avg_degree * 1.5)[0]

        return {
            "connectivity_matrix": connectivity_matrix.tolist(),
            "network_metrics": {
                "average_connectivity": float(avg_connectivity),
                "average_node_degree": float(avg_degree),
                "hub_neuron_indices": hub_neurons.tolist(),
                "network_density": float(
                    np.sum(connectivity_matrix > 0) /
                    (len(neurons_props) * (len(neurons_props) - 1))
                )
            }
        }

    def assess_neural_health_markers(
            self,neurons: List[Neuron]
    ) -> Dict[str, float]:
        if not neurons:
            return {}

        avg_health = np.mean([n.health for n in neurons])

        avg_synapse_count = np.mean([n.synapse_count for n in neurons])
        synapse_health = min(1.0, avg_synapse_count / 1000)

        avg_mito_density = np.mean([n.mitochondria_density for n in neurons])
        metabolic_health = avg_mito_density / 0.15

        myelination_quality = np.mean([
            n.myelination_index() for n in neurons
        ])

        structural_integrity = np.mean([
            n.structural_integrity for n in neurons
        ])

        overall_health_index = (
                                       avg_health * 0.3 +
                                       synapse_health * 100 * 0.25 +
                                       metabolic_health * 100 * 0.2 +
                                       myelination_quality * 100 * 0.15 +
                                       structural_integrity * 0.1
                               ) / 100

        return {
            "average_neuron_health": avg_health,
            "synaptic_health_index": synapse_health,
            "metabolic_health_index": metabolic_health,
            "myelination_quality": myelination_quality,
            "structural_integrity": structural_integrity / 100,
            "overall_neural_health": overall_health_index,
            "degeneration_risk": 1 - overall_health_index
        }

    def analyze_cells(self, image, dna: Optional[str] = None):
        """
        Analyze cells in the image and create Cell objects.

        :param image: Input image (ImageJ DataArray)
        :return: List of Cell objects
        """
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # Identify primary objects (nuclei)
        nuclei = self.identify_primary_objects(image)

        # Identify secondary objects (cell bodies)
        cell_bodies = self.identify_secondary_objects(nuclei)

        # Identify tertiary objects (cytoplasm)
        cytoplasm = self.identify_tertiary_objects(cell_bodies, nuclei)

        # Measure properties
        nuclei_props = self.measure_object_properties(nuclei, img_array)
        cell_props = self.measure_object_properties(cell_bodies, img_array)
        cytoplasm_props = self.measure_object_properties(
            cytoplasm, img_array
        )

        # Create Cell objects
        cells = []
        for i, (nucleus, cell, cyto) in enumerate(
                zip(nuclei_props, cell_props, cytoplasm_props)
        ):
            cell_type = self.determine_cell_type(nucleus, cell, cyto)

            if cell_type == "neuron":
                new_cell = self.create_neuron_object(
                    i, cell, cyto, nucleus, image, dna
                )
            else:
                new_cell = self.create_cell_object(
                    i, cell_type, cell, cyto, dna
                )

            # Detect if the cell is drugged
            if self.detect_drugged_cell(image, cell):
                new_cell.drugged = True
            else:
                new_cell.drugged = False

            cells.append(new_cell)

        return cells

    def determine_cell_type(
            self, nucleus_props: Dict, cell_props: Dict,
            cytoplasm_props: Dict
    ) -> str:
        """
        Determine the cell type based on measured properties.

        :param nucleus_props: Properties of the nucleus
        :param cell_props: Properties of the cell body
        :param cytoplasm_props: Properties of the cytoplasm
        :return: Determined cell type
        """
        nucleus_size = nucleus_props['area']
        cell_size = cell_props['area']
        cytoplasm_size = cytoplasm_props['area']
        nucleus_intensity = nucleus_props['mean_intensity']

        nucleus_to_cell_ratio = nucleus_size / cell_size
        cytoplasm_to_cell_ratio = cytoplasm_size / cell_size

        eccentricity = cell_props.get('eccentricity', 0.5)
        major_axis = cell_props.get('major_axis_length', 0)
        minor_axis = cell_props.get('minor_axis_length', 0)

        is_elongated = eccentricity > 0.8 and major_axis > 3 * minor_axis
        has_processes = cell_size > nucleus_size * 5 and is_elongated

        is_neuronal = (
                has_processes and
                nucleus_to_cell_ratio < 0.3 and
                nucleus_intensity > 80
        )

        if is_neuronal:
            return "neuron"
        elif nucleus_to_cell_ratio > 0.5:
            return "stem cell"
        elif cytoplasm_to_cell_ratio > 0.7:
            return "epithelial cell"
        elif nucleus_intensity > 100:
            return "fibroblast"
        else:
            return "somatic cell"

    def create_cell_object(
            self, index: int, cell_type: str, cell_props: Dict,
            cytoplasm_props: Dict, dna: Optional[str] = None
    ) -> Cell:
        """
        Create a Cell object based on measured properties.

        :param index: Index of the cell
        :param cell_type: Determined cell type
        :param cell_props: Properties of the cell body
        :param cytoplasm_props: Properties of the cytoplasm
        :param dna: DNA sequence
        :return: Cell object
        """
        # Generate DNA sequence based on cell type and image properties
        # Estimate number of mitochondria based on cytoplasm size
        num_mitochondria = max(1, int(cytoplasm_props['area'] / 100))

        # Common properties for both Cell
        common_props = {
            "name": f"Cell_{index}",
            "cell_type": cell_type,
            "dna": dna,
            "health": int(100 * (cell_props['mean_intensity'] / 255))
        }

        if cell_type == "stem cell":
            # Create a StemCell object
            cell = StemCell(**common_props)
            surface_proteins = [
                "CD44",
                "CD133",
                "SSEA-4",
                "CD34",
                "CD90",
                "EpCAM",
            ]

            surface_receptors = [
                "Notch Receptors",
                "Wnt Receptors (Frizzled)",
                "FGFR",
                "TGF-β Receptors",
                "LIFR",
                "EGFR",
            ]
            cell.surface_proteins = np.random.choice(
                surface_proteins,
                size=np.random.randint(1, 3),
                replace=False
            ).tolist()
            cell.receptors = np.random.choice(
                surface_receptors,
                size=np.random.randint(1, 3),
                replace=False
            ).tolist()
        elif cell_type == "epithelial cell":
            # Create an EpithelialCell object
            cell = EpithelialCell(**common_props)
            surface_proteins = [
                "E-Cadherin",
                "EpCAM",
                "Claudins",
                "Occludin",
                "Integrins",
                "Cytokeratins",
            ]

            receptors = [
                "EGFR",
                "VEGFR",
                "TGF-β Receptors",
                "Integrin Receptors",
                "Netrin Receptors",
                "Notch Receptors",
            ]

            cell.surface_proteins = np.random.choice(
                surface_proteins,
                size=np.random.randint(1, 3),
                replace=False
            ).tolist()
            cell.receptors = np.random.choice(
                receptors,
                size=np.random.randint(1, 3),
                replace=False
            ).tolist()
        elif cell_type == "somatic cell":
            # Create a SomaticCell object
            cell = SomaticCell(**common_props)
            surface_proteins = [
                "Integrins",
                "CD44",
                "CD45",
                "MHC I",
                "Glypican",
                "Cadherins",
            ]

            receptors = [
                "GPCRs",
                "EGFR",
                "FGFR",
                "TGF-β Receptors",
                "Insulin Receptors",
                "VEGFR",
            ]

            cell.surface_proteins = np.random.choice(
                surface_proteins,
                size=np.random.randint(1, 3),
                replace=False
            ).tolist()
            cell.receptors = np.random.choice(
                receptors,
                size=np.random.randint(1, 3),
                replace=False
            ).tolist()
        else:
            # Create a regular Cell object
            cell = Cell(**common_props)
            # Add some most often used proteins
            receptors = [
                "GPCR",
                "EGFR",
                "Integrin Receptors",
                "TGF-β Receptors",
                "MHC I",
            ]
            surface_proteins = [
                "CD44",
                "MHC I",
                "CD29 (Integrin β1)",
                "ICAM-1",
                "CD45",
            ]

            cell.receptors = np.random.choice(
                receptors, size=2, replace=False
            ).tolist()
            cell.surface_proteins = np.random.choice(
                surface_proteins, size=2, replace=False
            ).tolist()

        # Add cellular components
        cell.add_organelle(Organelle("nucleus", 1))
        cell.add_organelle(Mitochondrion())

        # Add mitochondria
        for _ in range(num_mitochondria):
            cell.add_mitochondrion(
                efficiency=np.random.uniform(0.8, 1.0), health=100
            )

        # Set other properties
        cell.metabolism_rate = cytoplasm_props['mean_intensity'] / 255

        return cell

    def analyze_and_create_cells(self, image_path: str) -> List[Cell]:
        """
        Analyze an image and create Cell objects based on the analysis.

        :param image_path: Path to the image file
        :return: List of Cell objects
        """
        # Load the image
        image = self.load_image(image_path)

        # Analyze cells and create Cell objects
        cells = self.analyze_cells(image)

        return cells

    def analyze_tissue(self, image):
        """
        Analyze tissue structure in the image.

        :param image: Input image (ImageJ DataArray)
        :return: Dictionary containing tissue properties
        """
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # Apply threshold to segment tissue
        binary = self.ij.op().threshold().otsu(image)
        binary_np = self.ij.py.from_java(binary)

        binary_np = binary_np.astype(bool)
        self.labeled_tissue = measure.label(binary_np)

        # Label connected regions (these will be our tissue segments)
        labeled_tissue = measure.label(binary_np)

        # Calculate properties for each tissue segment
        gray_img = self.grayscale_image(img_array)

        # Calculate properties for each tissue segment
        tissue_properties = measure.regionprops(labeled_tissue, gray_img)

        tissue_data = []
        for prop in tissue_properties:
            # Calculate mean intensity manually
            region_coords = prop.coords
            region_intensity = img_array[region_coords[:, 0], region_coords[:, 1]]
            mean_intensity = np.mean(region_intensity)

            tissue = {
                'area': prop.area,
                'perimeter': prop.perimeter,
                'mean_intensity': mean_intensity,
                'max_intensity': np.max(region_intensity),
                'min_intensity': np.min(region_intensity),
                'eccentricity': prop.eccentricity,
                'solidity': prop.solidity,
                'euler_number': prop.euler_number,  # Indicates the number of holes in the tissue
                'label': prop.label  # Store the label for each region
            }
            tissue_data.append(tissue)

        return tissue_data

    def determine_tissue_type(self, tissue_props) -> str:
        """
        Determine the tissue type based on measured properties.

        :param tissue_props: Properties of the tissue segment
        :return: Determined tissue type
        """
        if 'area' in tissue_props:
            area = tissue_props['area']
        else:
            area = 0

        if 'solidity' in tissue_props:
            solidity = tissue_props['solidity']
        else:
            solidity = 0

        if 'eccentricity' in tissue_props:
            eccentricity = tissue_props['eccentricity']
        else:
            eccentricity = 0

        if solidity > 0.9 and eccentricity < 0.3:
            return "epithelial"
        elif 0.6 < solidity < 0.9 and area > 10000:
            return "connective"
        elif eccentricity > 0.7 and area > 5000:
            return "muscle"
        elif 0.4 < solidity < 0.7 and tissue_props['euler_number'] < -5:
            return "nervous"
        else:
            return "undefined"

    def create_tissue_object(
            self, index: int, tissue_type: str, tissue_props: Dict,
            cells: List[Cell]
    ) -> Tissue:
        """
        Create a Tissue object based on measured properties.

        :param index: Index of the tissue segment
        :param tissue_type: Determined tissue type
        :param tissue_props: Properties of the tissue segment
        :param cells: List of Cell objects within this tissue
        :return: Tissue object
        """
        tissue_name = f"Tissue_{index}"
        cancer_risk = 0.001

        # Adjust tissue properties based on type
        if tissue_type == "epithelial":
            cancer_risk = 0.002
        elif tissue_type == "connective":
            cancer_risk = 0.0005
        elif tissue_type == "nervous":
            cancer_risk = 0.0001
            neurons = [c for c in cells if isinstance(c, Neuron)]
            if neurons:
                return self.create_neural_tissue_object(
                    index, tissue_type, tissue_props, neurons
                )

        tissue = Tissue(tissue_name, tissue_type, cells, cancer_risk)

        if 'mean_intensity' in tissue_props:
            tissue.growth_rate = (
                    0.05 * (tissue_props['mean_intensity'] / 255)
            )
        else:
            tissue.growth_rate = 0

        if 'solidity' in tissue_props:
            tissue.healing_rate = 0.1 * tissue_props['solidity']
        else:
            tissue.healing_rate = 0

        return tissue

    def analyze_cells_for_tissue(self, image):
        """
        Analyze cells in the image and create Cell objects.

        :param image: Input image (ImageJ DataArray)
        :return: List of Cell objects and their corresponding binary masks
        """
        # Convert ImageJ image to numpy array
        img_array = self.ij.py.from_java(image)

        # Identify primary objects (nuclei)
        nuclei_labeled = self.identify_primary_objects(image)

        # Identify secondary objects (cell bodies)
        cell_bodies_labeled = self.identify_secondary_objects(nuclei_labeled)

        # Identify tertiary objects (cytoplasm)
        cytoplasm_labeled = self.identify_tertiary_objects(cell_bodies_labeled, nuclei_labeled)

        # Measure properties
        nuclei_props = self.measure_object_properties(nuclei_labeled, img_array)
        cell_props = self.measure_object_properties(cell_bodies_labeled, img_array)
        cytoplasm_props = self.measure_object_properties(cytoplasm_labeled, img_array)

        # Create Cell objects and their corresponding binary masks
        cells = []
        cell_masks = []
        for i, (nucleus, cell, cyto) in enumerate(zip(nuclei_props, cell_props, cytoplasm_props)):
            cell_type = self.determine_cell_type(nucleus, cell, cyto)
            new_cell = self.create_cell_object(i, cell_type, cell, cyto)
            cells.append(new_cell)

            # Create a binary mask for the cell
            cell_mask = np.zeros_like(img_array, dtype=np.uint8)
            cell_mask[cell_bodies_labeled == cell['label']] = 1
            cell_masks.append(cell_mask)

        return cells, cell_masks

    def analyze_and_create_tissues(self, image_path: str) -> List[Tissue]:
        """
        Analyze an image and create Tissue objects based on the analysis.
        :param image_path: Path to the image file
        :return: List of Tissue objects
        """
        # Load the image
        image = self.load_image(image_path)

        # Analyze cells
        cells, cell_masks = self.analyze_cells_for_tissue(image)

        # Analyze tissue structure
        tissue_data = self.analyze_tissue(image)

        tissues = []
        for index, tissue_props in enumerate(tissue_data):
            # Create a binary mask for the tissue segment
            tissue_mask = np.array(self.labeled_tissue == tissue_props['label'], dtype=np.uint8)

            # Assign cells to tissues based on their location
            tissue_cells = []
            for i in range(len(cells)):
                cell = cells[i]
                cell_mask = cell_masks[i]
                # Check if the cell is within the tissue segment
                if self.cell_in_tissue(cell_mask, tissue_mask):
                    tissue_cells.append(cell)
            tissue_type = self.determine_tissue_type(tissue_props)
            tissue = self.create_tissue_object(index, tissue_type, tissue_props, tissue_cells)
            tissues.append(tissue)

        return tissues

    def cell_in_tissue(self, cell_mask, tissue_mask):
        """
        Determine if a cell is within a given tissue segment.

        :param cell_mask: Binary mask of the cell (numpy array)
        :param tissue_mask: Binary mask of the tissue segment (numpy array)
        :return: Boolean indicating if the cell is within the tissue segment
        """
        # Ensure the masks are of the same shape
        if cell_mask.shape != tissue_mask.shape:
            raise ValueError("Cell mask and tissue mask must have the same shape.")

        # Check if any pixel of the cell mask is within the tissue mask
        overlap = np.logical_and(cell_mask, tissue_mask)
        return np.any(overlap)

    def detect_drugged_cell(self, image, cell_props: Dict) -> bool:
        """
        Detect if a cell was drugged based on its properties.

        :param cell_props: Properties of the cell
        :return: Boolean indicating if the cell is drugged
        """
        # Criteria for detecting a drugged cell
        # Criteria:
        # - Mean intensity is significantly higher or lower than the average
        # - Cell area is significantly larger or smaller than the average
        # - Eccentricity is significantly different from the average

        img_array = self.ij.py.from_java(image)

        # Identify objects
        primary_objects = self.identify_primary_objects(image)
        secondary_objects = self.identify_secondary_objects(primary_objects)
        tertiary_objects = self.identify_tertiary_objects(secondary_objects, primary_objects)

        # Measure properties
        object_properties = self.measure_object_properties(tertiary_objects, img_array)

        # Calculate average properties
        avg_mean_intensity = np.mean([prop['mean_intensity'] for prop in object_properties])
        avg_area = np.mean([prop['area'] for prop in object_properties])
        avg_eccentricity = np.mean([prop['eccentricity'] for prop in object_properties])

        # Thresholds for detecting anomalies
        intensity_threshold = 0.2 * avg_mean_intensity
        area_threshold = 0.2 * avg_area
        eccentricity_threshold = 0.2 * avg_eccentricity

        # Check if the cell's properties deviate significantly from the average
        is_drugged = (
                abs(cell_props['mean_intensity'] - avg_mean_intensity) > intensity_threshold or
                abs(cell_props['area'] - avg_area) > area_threshold or
                abs(cell_props['eccentricity'] - avg_eccentricity) > eccentricity_threshold
        )

        return is_drugged

    def visualize_mitochondria(self, image, mitochondria_data):
        """
        Visualize mitochondria in the image.

        :param image: Original image (ImageJ DataArray)
        :param mitochondria_data: List of dictionaries containing mitochondria properties
        """
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)
        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')
        for mito in mitochondria_data:
            y, x = mito['centroid']
            plt.plot(x, y, 'ro', markersize=5)
        plt.title('Mitochondria Detection')
        plt.axis('off')
        plt.show()

    def visualize_nuclei(self, image, nuclei_data):
        """
        Visualize nuclei in the image.

        :param image: Original image (ImageJ DataArray)
        :param nuclei_data: List of dictionaries containing nuclei properties
        """
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)
        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')
        for nucleus in nuclei_data:
            y, x = nucleus['centroid']
            plt.plot(x, y, 'bo', markersize=5)
        plt.title('Nuclei Detection')
        plt.axis('off')
        plt.show()

    def visualize_cancer_cells(self, image, cancer_cells):
        """
        Visualize potential cancer cells in the image.

        :param image: Original image (ImageJ DataArray)
        :param cancer_cells: List of dictionaries containing potential cancer cell properties
        """
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)
        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')
        for cell in cancer_cells:
            y, x = cell['centroid']
            plt.plot(x, y, 'ro', markersize=10, markeredgecolor='yellow', markeredgewidth=2)
        plt.title('Potential Cancer Cells')
        plt.axis('off')
        plt.show()

    def visualize_grayscale_image(self, image):
        """
        Visualize the grayscale image.

        :param image: Original image (ImageJ DataArray)
        """
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)
        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')
        plt.title('Grayscale Image')
        plt.axis('off')
        plt.show()

    def visualize_network_image(self, image_path, analysis_result):
        """
        Visualize the analysis of the network image.

        :param image_path: Path to the network image
        :param analysis_result: Dictionary containing nodes, edges, and their properties
        """
        # Load the image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Plot nodes
        for node in analysis_result['nodes']:
            center = node['center']
            radius = node['radius']
            color = node['color']
            cv2.circle(image_rgb, center, radius, color, 2)

        # Plot edges
        for edge in analysis_result['edges']:
            start = edge['start']
            end = edge['end']
            cv2.line(image_rgb, start, end, (0, 255, 0), 2)

        # Plot arrows
        for arrow in analysis_result['arrows']:
            cv2.circle(image_rgb, arrow, 2, (255, 0, 0), -1)

        # Display the image
        plt.figure(figsize=(10, 10))
        plt.imshow(image_rgb)
        plt.title('Network Image Analysis')
        plt.axis('off')
        plt.show()

    def visualise_fluorescence(self, image, fluorescence_data):
        """
        Visualize the fluorescence data in the image.

        :param image: Original image (ImageJ DataArray)
        :param fluorescence_data: List of dictionaries containing fluorescence properties
        """
        # Convert the image to a Java object and then back to a Python array
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)

        # Debugging: Print the type and content of fluorescence_data
        print(f"Type of fluorescence_data: {type(fluorescence_data)}")
        print(f"Content of fluorescence_data: {fluorescence_data}")

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')

        for cell in fluorescence_data:
            # Debugging: Print the type and content of cell
            print(f"Type of cell: {type(cell)}")
            print(f"Content of cell: {cell}")

            if isinstance(cell, str):
                try:
                    # Attempt to parse the string as JSON
                    cell = json.loads(cell)
                except json.JSONDecodeError:
                    print(f"Failed to parse cell as JSON: {cell}")
                    continue

            if isinstance(cell, dict) and 'centroid' in cell:
                y, x = cell['centroid']
                plt.plot(x, y, 'bo', markersize=5)
            else:
                print(f"Invalid cell data: {cell}")

        plt.title('Fluorescence Detection')
        plt.axis('off')
        plt.show()

    def plot_trajectories(self, tracked_cells, image):
        """Plot the trajectories of tracked cells."""
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)
        image_shape = img_array.shape

        plt.figure(figsize=(10, 10))
        for cell in tracked_cells:
            trajectory = cell['trajectory']
            # Filter out None values (disappeared cells)
            trajectory = [pos for pos in trajectory if pos is not None]
            if trajectory:
                # Convert list of tuples to numpy array for plotting
                trajectory = np.array(trajectory)
                plt.plot(trajectory[:, 1], trajectory[:, 0], marker='o')

        plt.xlim(0, image_shape[1])
        plt.ylim(0, image_shape[0])
        plt.gca().invert_yaxis()  # Invert y-axis to match image coordinates
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Cell Trajectories')
        plt.show()

    def visualize_primary_objects(self, image, primary_objects):
        """Visualize the primary objects in the image."""
        # Convert the image to a Java object and then back to a Python array
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')

        for cell in primary_objects:
            if isinstance(cell, str):
                try:
                    # Attempt to parse the string as JSON
                    cell = json.loads(cell)
                except json.JSONDecodeError:
                    print(f"Failed to parse cell as JSON: {cell}")
                    continue

            if isinstance(cell, dict) and 'centroid' in cell:
                y, x = cell['centroid']
                plt.plot(x, y, 'bo', markersize=5)
            else:
                print(f"Invalid cell data: {cell}")

        plt.title('Primary Objects')
        plt.axis('off')
        plt.show()

    def visualize_secondary_objects(self, image, secondary_objects):
        """Visualize the secondary objects in the image."""
        # Convert the image to a Java object and then back to a Python array
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')

        for cell in secondary_objects:
            if isinstance(cell, str):
                try:
                    # Attempt to parse the string as JSON
                    cell = json.loads(cell)
                except json.JSONDecodeError:
                    print(f"Failed to parse cell as JSON: {cell}")
                    continue

            if isinstance(cell, dict) and 'centroid' in cell:
                y, x = cell['centroid']
                plt.plot(x, y, 'bo', markersize=5)
            else:
                print(f"Invalid cell data: {cell}")

        plt.title('Secondary Objects')
        plt.axis('off')
        plt.show()

    def visualize_tertiary_objects(self, image, tertiary_objects):
        """Visualize the tertiary objects in the image."""
        # Convert the image to a Java object and then back to a Python array
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')

        for cell in tertiary_objects:
            if isinstance(cell, str):
                try:
                    # Attempt to parse the string as JSON
                    cell = json.loads(cell)
                except json.JSONDecodeError:
                    print(f"Failed to parse cell as JSON: {cell}")
                    continue

            if isinstance(cell, dict) and 'centroid' in cell:
                y, x = cell['centroid']
                plt.plot(x, y, 'bo', markersize=5)
            else:
                print(f"Invalid cell data: {cell}")

        plt.title('Tertiary Objects')
        plt.axis('off')
        plt.show()

    def visualize_measured_properties(self, image, measured_properties):
        """Visualize the measured properties in the image."""
        # Convert the image to a Java object and then back to a Python array
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')

        for cell in measured_properties:
            if isinstance(cell, str):
                try:
                    # Attempt to parse the string as JSON
                    cell = json.loads(cell)
                except json.JSONDecodeError:
                    print(f"Failed to parse cell as JSON: {cell}")
                    continue

            if isinstance(cell, dict) and 'centroid' in cell:
                y, x = cell['centroid']
                plt.plot(x, y, 'bo', markersize=5)
            else:
                print(f"Invalid cell data: {cell}")

        plt.title('Measured Properties')

    def visualise_segmented_image(self, image, labeled_img, num_labels):
        """Visualize the segmented image."""
        # Convert the image to a Java object and then back to a Python array
        java_image = self.ij.py.to_java(image)
        img_array = self.ij.py.from_java(java_image)

        # Convert the labeled image to a Java object and then back to a Python array
        java_labeled_img = self.ij.py.to_java(labeled_img)
        labeled_img_array = self.ij.py.from_java(java_labeled_img)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')
        plt.imshow(labeled_img_array, cmap='tab20', alpha=0.5)
        plt.title(f'Segmented Image (Total number of cells: {num_labels})')

    def display_cells(self, cells):
        """
        Display cells using matplotlib.

        :param cells: List of Cell objects
        """
        # Extract relevant information from cells
        names = [cell.name for cell in cells]
        cell_types = [cell.cell_type for cell in cells]
        healths = [cell.health for cell in cells]
        drugged = [cell.drugged for cell in cells]

        # Determine the color for each bar based on the drugged status
        colors = ['red' if d else 'skyblue' for d in drugged]

        # Create a bar plot for cell health
        fig, ax = plt.subplots()
        ax.bar(names, healths, color=colors)

        # Add titles and labels
        ax.set_title('Cell Health')
        ax.set_xlabel('Cell Name')
        ax.set_ylabel('Health (%)')
        ax.set_ylim(0, 100)  # Assuming health is a percentage

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')

        # Display cell types and drugged status as text on the plot
        for i, (txt, d) in enumerate(zip(cell_types, drugged)):
            drugged_label = " *" if d else ""
            label = (txt or "Unknown") + drugged_label
            ax.text(i, healths[i] + 1, label, ha='center', fontsize=8)

        # Show the plot
        plt.tight_layout()
        plt.show()

    def load_protein_structure(self, pdb_file):
        """
        Load a protein structure from a PDB file.

        :param pdb_file: Path to the PDB file
        :return: PyRosetta Pose object
        """
        cleanATOM(pdb_file)  # Clean the PDB file
        return pose_from_pdb(pdb_file)

    def analyze_protein_structure(self, pose):
        """
        Analyze the protein structure.

        :param pose: PyRosetta Pose object
        :return: Dictionary with structure analysis results
        """
        sfxn = get_score_function()  # Get the default score function
        score = sfxn(pose)  # Calculate the score

        analysis = {
            'total_residues': pose.total_residue(),
            'score': score,
            'phi_psi': [],
            'secondary_structure': pose.secstruct()
        }

        for i in range(1, pose.total_residue() + 1):
            phi = pose.phi(i)
            psi = pose.psi(i)
            analysis['phi_psi'].append((phi, psi))

        return analysis

    def design_protein(self, pose, design_xml):
        """
        Perform protein design using RosettaScripts.

        :param pose: PyRosetta Pose object
        :param design_xml: XML string with RosettaScripts protocol
        :return: Designed PyRosetta Pose object
        """
        xml_objects = XmlObjects.create_from_string(design_xml)
        protocol = xml_objects.get_mover("DesignProtocol")
        protocol.apply(pose)
        return pose

    def dock_proteins(self, pose_receptor, pose_ligand):
        """
        Perform protein-protein docking.

        :param pose_receptor: PyRosetta Pose object of the receptor
        :param pose_ligand: PyRosetta Pose object of the ligand
        :return: Docked PyRosetta Pose object
        """
        # This is a simplified docking protocol
        docking_script = """
        <ROSETTASCRIPTS>
            <SCOREFXNS>
                <ScoreFunction name="dock_score" weights="interchain"/>
            </SCOREFXNS>
            <MOVERS>
                <DockingProtocol name="dock" scorefxn="dock_score"/>
            </MOVERS>
            <PROTOCOLS>
                <Add mover="dock"/>
            </PROTOCOLS>
        </ROSETTASCRIPTS>
        """
        xml_objects = XmlObjects.from_string(docking_script)
        protocol = xml_objects.get_mover("dock")

        # Combine receptor and ligand poses
        combined_pose = pose_receptor.clone()
        combined_pose.append_pose_by_jump(pose_ligand, 1)

        # Apply docking protocol
        protocol.apply(combined_pose)

        return combined_pose

    def train_protein_classifier(self, training_data):
        """
        Train a Random Forest classifier for protein type prediction.

        :param training_data: List of dictionaries, each containing 'features' and 'protein_type'
        """
        X = [sample['features'] for sample in training_data]
        y = [sample['protein_type'] for sample in training_data]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.protein_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.protein_classifier.fit(X_train_scaled, y_train)

        accuracy = self.protein_classifier.score(X_test_scaled, y_test)
        print(f"Protein classifier accuracy: {accuracy:.2f}")

    def extract_features(self, structure_analysis):
        """
        Extract relevant features from the structure analysis for ML model.

        :param structure_analysis: Dictionary with structure analysis results
        :return: numpy array of features
        """
        alpha_helix_count = structure_analysis['secondary_structure'].count('H')
        beta_sheet_count = structure_analysis['secondary_structure'].count('E')
        total_residues = structure_analysis['total_residues']

        features = [
            alpha_helix_count / total_residues,
            beta_sheet_count / total_residues,
            structure_analysis['score'],
            np.mean([phi for phi, _ in structure_analysis['phi_psi']]),
            np.mean([psi for _, psi in structure_analysis['phi_psi']]),
        ]
        return np.array(features).reshape(1, -1)

    def analyze_and_create_protein(self, image_path: str, pdb_file: str) -> Protein:
        """
        Analyze a protein image and create a Protein object based on the analysis.

        :param image_path: Path to the protein image file
        :param pdb_file: Path to the PDB file of the protein
        :return: Protein object
        """
        # Load the protein structure
        pose = self.load_protein_structure(pdb_file)

        # Analyze protein structure
        structure_analysis = self.analyze_protein_structure(pose)

        # Extract features for ML model
        features = self.extract_features(structure_analysis)

        # Predict protein type using ML model
        if self.protein_classifier is not None:
            scaled_features = self.scaler.transform(features)
            protein_type = self.protein_classifier.predict(scaled_features)[0]
        else:
            protein_type = self.determine_protein_type(structure_analysis)

        # Determine interactions and bindings
        interactions, bindings = self.determine_protein_characteristics(structure_analysis, protein_type)

        # Create Protein object
        protein = Protein(
            name=f"Protein_{os.path.basename(image_path)}",
            sequence=pose.sequence(),
            structure=pose,
            secondary_structure=structure_analysis['secondary_structure']
        )

        # Add interactions and bindings
        for interaction in interactions:
            protein.add_interaction(interaction['protein'], interaction['type'], interaction['strength'])

        for binding in bindings:
            protein.add_binding(binding['site'], binding['affinity'])

        return protein

    def determine_protein_type(self, structure_analysis):
        """
        Determine protein type based on structure analysis (fallback method).

        :param structure_analysis: Dictionary with structure analysis results
        :return: Predicted protein type
        """
        alpha_helix_count = structure_analysis['secondary_structure'].count('H')
        beta_sheet_count = structure_analysis['secondary_structure'].count('E')
        total_residues = structure_analysis['total_residues']

        if alpha_helix_count / total_residues > 0.6:
            return "alpha_helical"
        elif beta_sheet_count / total_residues > 0.4:
            return "beta_sheet"
        else:
            return "mixed"

    def determine_protein_characteristics(self, structure_analysis, protein_type):
        """
        Determine protein interactions and bindings based on structure analysis and protein type.

        :param structure_analysis: Dictionary with structure analysis results
        :param protein_type: Predicted protein type
        :return: Tuple of (interactions, bindings)
        """
        interactions = []
        bindings = []

        # Determine potential interactions based on protein type
        if protein_type == "alpha_helical":
            interactions.append({
                'protein': "Membrane_Protein",
                'type': "binding",
                'strength': "strong"
            })
        elif protein_type == "beta_sheet":
            interactions.append({
                'protein': "Antibody",
                'type': "recognition",
                'strength': "moderate"
            })
        elif protein_type == "mixed":
            interactions.append({
                'protein': "Enzyme",
                'type': "catalysis",
                'strength': "variable"
            })

        # Determine potential binding sites based on structure
        for i, (phi, psi) in enumerate(structure_analysis['phi_psi']):
            if -100 < phi < -50 and -75 < psi < -25:
                bindings.append({
                    'site': f"Residue_{i+1}",
                    'affinity': "high"
                })

        return interactions, bindings

    def analyze_xray(self, image_path):
        """
        Analyze an X-ray image.

        :param image_path: Path to the X-ray image file
        :return: Dictionary containing analysis results
        """
        image = self.load_image(image_path)
        return self.xray_analyzer.analyze_xray(image)

    def visualize_xray_analysis(self, image_path, analysis_results):
        """
        Visualize the results of X-ray analysis.

        :param image_path: Path to the original X-ray image file
        :param analysis_results: Results from analyze_xray method
        """
        original_image = self.load_image(image_path)
        original_image_np = self.ij.py.from_java(original_image)
        self.xray_analyzer.visualize_xray_analysis(original_image_np, analysis_results)

    def close(self):
        """Close the ImageJ instance."""
        self.ij.dispose()
