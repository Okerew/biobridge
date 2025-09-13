import random

import numpy as np
from scipy import ndimage
from skimage import measure, morphology
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from biobridge.blocks.cell import Cell
from biobridge.definitions.tissues.bone import BoneTissue


class CTScanAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer
        # Hounsfield Unit ranges for different tissues
        self.hu_ranges = {
            "air": (-1000, -950),
            "lung": (-950, -500),
            "fat": (-200, -50),
            "water": (-50, 50),
            "soft_tissue": (50, 300),
            "bone": (300, 3000),
        }

    def analyze_ct_scan(self, image_stack, slice_thickness=1.0):
        """
        Analyze a CT scan volume using advanced 3D techniques.

        :param image_stack: Input CT scan volume (3D array or list of 2D slices)
        :param slice_thickness: Thickness of each slice in mm
        :return: Dictionary containing comprehensive analysis results
        """
        # Convert to 3D numpy array if needed
        if isinstance(image_stack, list):
            volume = np.stack(
                [self.image_analyzer.ij.py.from_java(img) for img in image_stack]
            )
        else:
            volume = self.image_analyzer.ij.py.from_java(image_stack)

        # Ensure proper dimensions (Z, Y, X)
        if len(volume.shape) == 4:
            volume = np.mean(volume, axis=-1)  # Convert to grayscale if needed

        # Convert to Hounsfield Units if needed
        hu_volume = self.convert_to_hounsfield_units(volume)

        # Enhance the volume
        enhanced_volume = self.enhance_ct_volume(hu_volume)

        # Segment different tissue types
        tissue_segmentation = self.segment_tissues(hu_volume)

        # Detect 3D edges
        edges_3d = self.detect_3d_edges(enhanced_volume)

        # Detect anomalies in 3D
        anomalies_3d = self.detect_3d_anomalies(hu_volume, tissue_segmentation)

        # Calculate volume measurements
        volume_measurements = self.calculate_volume_measurements(
            tissue_segmentation, slice_thickness
        )

        # Analyze bone structure
        bone_analysis = self.analyze_bone_structure(hu_volume, tissue_segmentation)

        # Detect nodules/masses
        nodules = self.detect_nodules(hu_volume, tissue_segmentation)

        return {
            "original_volume": volume,
            "hounsfield_volume": hu_volume,
            "enhanced_volume": enhanced_volume,
            "tissue_segmentation": tissue_segmentation,
            "edges_3d": edges_3d,
            "anomalies_3d": anomalies_3d,
            "volume_measurements": volume_measurements,
            "bone_analysis": bone_analysis,
            "nodules": nodules,
            "slice_count": volume.shape[0],
            "slice_thickness": slice_thickness,
        }

    def convert_to_hounsfield_units(self, volume):
        """
        Convert CT values to Hounsfield Units (HU).

        :param volume: Input CT volume
        :return: Volume in Hounsfield Units
        """
        # This is a simplified conversion - in practice, you'd use DICOM metadata
        # Assuming the volume is already in HU or needs basic linear transformation
        if np.min(volume) >= 0 and np.max(volume) <= 4095:
            # Convert from typical CT range to HU
            hu_volume = volume.astype(np.float32) - 1024
        else:
            hu_volume = volume.astype(np.float32)

        return hu_volume

    def enhance_ct_volume(self, hu_volume):
        """
        Enhance CT volume using 3D filtering techniques.

        :param hu_volume: Input volume in Hounsfield Units
        :return: Enhanced volume
        """
        # Apply 3D Gaussian filter for noise reduction
        enhanced = ndimage.gaussian_filter(hu_volume, sigma=0.8)

        # Apply anisotropic diffusion-like filtering
        for i in range(3):  # Multiple iterations
            enhanced = ndimage.median_filter(enhanced, size=3)

        return enhanced

    def segment_tissues(self, hu_volume):
        """
        Segment different tissue types based on Hounsfield Unit values.

        :param hu_volume: Volume in Hounsfield Units
        :return: Dictionary of tissue masks
        """
        segmentation = {}

        for tissue, (min_hu, max_hu) in self.hu_ranges.items():
            mask = (hu_volume >= min_hu) & (hu_volume <= max_hu)
            # Clean up small artifacts
            mask = morphology.remove_small_objects(mask, min_size=50)
            mask = morphology.remove_small_holes(mask, area_threshold=30)
            segmentation[tissue] = mask

        return segmentation

    def detect_3d_edges(self, volume):
        """
        Detect edges in 3D using gradient magnitude.

        :param volume: Input 3D volume
        :return: 3D edge volume
        """
        # Calculate gradients in all three directions
        grad_z, grad_y, grad_x = np.gradient(volume.astype(np.float32))

        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

        # Apply threshold to get edges
        threshold = np.percentile(gradient_magnitude, 95)
        edges = gradient_magnitude > threshold

        return edges.astype(np.uint8)

    def detect_3d_anomalies(self, hu_volume, tissue_segmentation):
        """
        Detect anomalies in 3D CT data using machine learning.

        :param hu_volume: Volume in Hounsfield Units
        :param tissue_segmentation: Tissue segmentation masks
        :return: List of 3D anomaly locations and scores
        """
        # Sample points for analysis (to reduce computational load)
        z_coords, y_coords, x_coords = np.meshgrid(
            np.arange(0, hu_volume.shape[0], 2),
            np.arange(0, hu_volume.shape[1], 4),
            np.arange(0, hu_volume.shape[2], 4),
            indexing="ij",
        )

        coords = np.column_stack(
            [z_coords.flatten(), y_coords.flatten(), x_coords.flatten()]
        )

        # Extract features for each point
        features = []
        for z, y, x in coords:
            if (
                z < hu_volume.shape[0]
                and y < hu_volume.shape[1]
                and x < hu_volume.shape[2]
            ):
                # HU value
                hu_val = hu_volume[z, y, x]

                # Local statistics (3x3x3 neighborhood)
                z_min, z_max = max(0, z - 1), min(hu_volume.shape[0], z + 2)
                y_min, y_max = max(0, y - 1), min(hu_volume.shape[1], y + 2)
                x_min, x_max = max(0, x - 1), min(hu_volume.shape[2], x + 2)

                neighborhood = hu_volume[z_min:z_max, y_min:y_max, x_min:x_max]
                local_mean = np.mean(neighborhood)
                local_std = np.std(neighborhood)

                # Tissue type encoding
                tissue_encoding = 0
                for i, (tissue, mask) in enumerate(tissue_segmentation.items()):
                    if mask[z, y, x]:
                        tissue_encoding = i + 1
                        break

                features.append(
                    [hu_val, local_mean, local_std, tissue_encoding, z, y, x]
                )

        features = np.array(features)

        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Apply Isolation Forest
        clf = IsolationForest(contamination=0.005, random_state=42)
        anomaly_labels = clf.fit_predict(features_normalized)
        anomaly_scores = -clf.score_samples(features_normalized)

        # Extract anomaly coordinates and scores
        anomaly_indices = np.where(anomaly_labels == -1)[0]
        anomalies = []

        for idx in anomaly_indices:
            coord = coords[idx]
            score = anomaly_scores[idx]
            anomalies.append(
                {"coord": coord, "score": score, "hu_value": features[idx][0]}
            )

        return anomalies

    def calculate_volume_measurements(self, tissue_segmentation, slice_thickness):
        """
        Calculate volume measurements for different tissues.

        :param tissue_segmentation: Tissue segmentation masks
        :param slice_thickness: Thickness of each slice in mm
        :return: Dictionary of volume measurements
        """
        measurements = {}

        for tissue, mask in tissue_segmentation.items():
            # Calculate volume in cubic mm
            voxel_count = np.sum(mask)
            volume_mm3 = voxel_count * slice_thickness  # Assuming 1mm x 1mm pixel size

            # Calculate surface area using marching cubes
            try:
                if voxel_count > 0:
                    verts, faces, _, _ = measure.marching_cubes(
                        mask.astype(np.float32), level=0.5
                    )
                    surface_area = measure.mesh_surface_area(verts, faces)
                else:
                    surface_area = 0
            except:
                surface_area = 0

            measurements[tissue] = {
                "volume_mm3": volume_mm3,
                "voxel_count": voxel_count,
                "surface_area": surface_area,
            }

        return measurements

    def analyze_bone_structure(self, hu_volume, tissue_segmentation):
        """
        Analyze bone structure and density.

        :param hu_volume: Volume in Hounsfield Units
        :param tissue_segmentation: Tissue segmentation masks
        :return: Bone analysis results
        """
        bone_mask = tissue_segmentation.get(
            "bone", np.zeros_like(hu_volume, dtype=bool)
        )

        if not np.any(bone_mask):
            return {"error": "No bone tissue detected"}

        # Extract bone HU values
        bone_hu_values = hu_volume[bone_mask]

        # Calculate bone density statistics
        bone_density_stats = {
            "mean_hu": np.mean(bone_hu_values),
            "std_hu": np.std(bone_hu_values),
            "min_hu": np.min(bone_hu_values),
            "max_hu": np.max(bone_hu_values),
            "median_hu": np.median(bone_hu_values),
        }

        # Trabecular vs cortical bone classification
        cortical_threshold = 1000  # HU
        trabecular_mask = bone_mask & (hu_volume < cortical_threshold)
        cortical_mask = bone_mask & (hu_volume >= cortical_threshold)

        trabecular_volume = np.sum(trabecular_mask)
        cortical_volume = np.sum(cortical_mask)

        return {
            "density_stats": bone_density_stats,
            "trabecular_volume": trabecular_volume,
            "cortical_volume": cortical_volume,
            "trabecular_cortical_ratio": trabecular_volume / max(cortical_volume, 1),
        }

    def detect_nodules(self, hu_volume, tissue_segmentation):
        """
        Detect potential nodules or masses in the CT scan.

        :param hu_volume: Volume in Hounsfield Units
        :param tissue_segmentation: Tissue segmentation masks
        :return: List of detected nodules
        """
        lung_mask = tissue_segmentation.get(
            "lung", np.zeros_like(hu_volume, dtype=bool)
        )

        nodules = []

        # Detect nodules in lungs (typically higher HU than surrounding lung tissue)
        if np.any(lung_mask):
            lung_hu = hu_volume[lung_mask]
            lung_mean = np.mean(lung_hu)
            lung_std = np.std(lung_hu)

            # Find regions significantly brighter than lung tissue
            nodule_candidates = lung_mask & (hu_volume > lung_mean + 2 * lung_std)

            # Label connected components
            labeled_nodules = measure.label(nodule_candidates)

            for region in measure.regionprops(labeled_nodules):
                if region.area > 10:  # Minimum size filter
                    centroid = region.centroid
                    nodules.append(
                        {
                            "location": centroid,
                            "volume": region.area,
                            "type": "lung_nodule",
                            "mean_hu": np.mean(
                                hu_volume[labeled_nodules == region.label]
                            ),
                        }
                    )

        return nodules

    def visualize_ct_analysis(self, analysis_results, slice_index=None):
        """
        Visualize CT analysis results for a specific slice or middle slice.

        :param analysis_results: Results from analyze_ct_scan method
        :param slice_index: Index of slice to visualize (None for middle slice)
        """
        import matplotlib.pyplot as plt

        if slice_index is None:
            slice_index = analysis_results["original_volume"].shape[0] // 2

        fig, axs = plt.subplots(2, 4, figsize=(20, 10))

        # Original slice
        axs[0, 0].imshow(analysis_results["original_volume"][slice_index], cmap="gray")
        axs[0, 0].set_title(f"Original CT Slice {slice_index}")

        # Hounsfield Units
        axs[0, 1].imshow(
            analysis_results["hounsfield_volume"][slice_index], cmap="gray"
        )
        axs[0, 1].set_title("Hounsfield Units")

        # Enhanced slice
        axs[0, 2].imshow(analysis_results["enhanced_volume"][slice_index], cmap="gray")
        axs[0, 2].set_title("Enhanced CT")

        # Tissue segmentation overlay
        original_slice = analysis_results["original_volume"][slice_index]
        tissue_overlay = np.zeros((*original_slice.shape, 3))
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]

        for i, (tissue, mask) in enumerate(
            analysis_results["tissue_segmentation"].items()
        ):
            if i < len(colors):
                tissue_slice = mask[slice_index]
                for c in range(3):
                    tissue_overlay[:, :, c] += tissue_slice * colors[i][c]

        axs[0, 3].imshow(tissue_overlay)
        axs[0, 3].set_title("Tissue Segmentation")

        # 3D edges
        axs[1, 0].imshow(analysis_results["edges_3d"][slice_index], cmap="gray")
        axs[1, 0].set_title("3D Edge Detection")

        # Anomalies
        anomaly_slice = original_slice.copy()
        for anomaly in analysis_results["anomalies_3d"]:
            z, y, x = anomaly["coord"]
            if z == slice_index:
                anomaly_slice[int(y), int(x)] = np.max(anomaly_slice)
        axs[1, 1].imshow(anomaly_slice, cmap="hot")
        axs[1, 1].set_title("Anomaly Detection")

        # Volume measurements bar chart
        tissues = list(analysis_results["volume_measurements"].keys())
        volumes = [
            analysis_results["volume_measurements"][t]["volume_mm3"] for t in tissues
        ]
        axs[1, 2].bar(range(len(tissues)), volumes)
        axs[1, 2].set_xticks(range(len(tissues)))
        axs[1, 2].set_xticklabels(tissues, rotation=45)
        axs[1, 2].set_title("Tissue Volumes (mm³)")
        axs[1, 2].set_ylabel("Volume (mm³)")

        # Bone analysis
        if "error" not in analysis_results["bone_analysis"]:
            bone_stats = analysis_results["bone_analysis"]["density_stats"]
            hu_values = list(bone_stats.values())
            hu_labels = list(bone_stats.keys())
            axs[1, 3].bar(range(len(hu_labels)), hu_values)
            axs[1, 3].set_xticks(range(len(hu_labels)))
            axs[1, 3].set_xticklabels(hu_labels, rotation=45)
            axs[1, 3].set_title("Bone Density Statistics (HU)")
        else:
            axs[1, 3].text(0.5, 0.5, "No bone detected", ha="center", va="center")
            axs[1, 3].set_title("Bone Analysis")

        for ax in axs.flat[:-2]:  # All except the last two which are bar charts
            ax.axis("off")

        plt.tight_layout()
        plt.show()

    def create_bone_tissue_from_ct(
        self, hu_volume, tissue_segmentation, tissue_name: str
    ) -> BoneTissue:
        """
        Create a BoneTissue object from CT scan analysis results.

        :param hu_volume: Volume in Hounsfield Units
        :param tissue_segmentation: Tissue segmentation masks
        :param tissue_name: Name for the new BoneTissue object
        :return: BoneTissue object
        """
        bone_mask = tissue_segmentation.get(
            "bone", np.zeros_like(hu_volume, dtype=bool)
        )

        if not np.any(bone_mask):
            # Create minimal bone tissue if no bone detected
            cells = [Cell(f"BoneCell_0", "90.0")]
            return BoneTissue(
                name=tissue_name, cells=cells, cancer_risk=0.01, mineral_density=0.5
            )

        # Extract bone HU values for density calculation
        bone_hu_values = hu_volume[bone_mask]
        avg_bone_hu = np.mean(bone_hu_values)

        # Convert HU to mineral density (0-2 scale)
        # Normal bone: 300-3000 HU, map to 0.5-2.0 density
        mineral_density = max(0.1, min(2.0, (avg_bone_hu - 200) / 1400))

        # Calculate cancer risk based on HU variability and anomalies
        bone_hu_std = np.std(bone_hu_values)
        # Higher variability might indicate pathology
        cancer_risk = min(0.1, bone_hu_std / 1000)

        # Create cells based on bone volume
        bone_volume = np.sum(bone_mask)
        num_cells = max(1, int(bone_volume / 10000))  # One cell per 10k voxels

        cells = []
        for i in range(num_cells):
            # Health based on HU values - normal bone around 1000 HU
            if 800 <= avg_bone_hu <= 1200:
                health = random.uniform(90, 100)
            elif 600 <= avg_bone_hu <= 800 or 1200 <= avg_bone_hu <= 1500:
                health = random.uniform(80, 95)
            else:
                health = random.uniform(70, 90)

            cells.append(Cell(f"BoneCell_{i}", str(health)))

        # Create bone tissue
        bone_tissue = BoneTissue(
            name=tissue_name,
            cells=cells,
            cancer_risk=cancer_risk,
            mineral_density=mineral_density,
        )

        # Set activity levels based on HU distribution
        cortical_volume = np.sum(bone_mask & (hu_volume >= 1000))
        trabecular_volume = np.sum(bone_mask & (hu_volume < 1000))

        if cortical_volume + trabecular_volume > 0:
            trabecular_ratio = trabecular_volume / (cortical_volume + trabecular_volume)
            # Higher trabecular ratio suggests more active remodeling
            bone_tissue.osteoclast_activity = 0.01 + (trabecular_ratio * 0.04)
            bone_tissue.osteoblast_activity = 0.02 + (trabecular_ratio * 0.03)

        return bone_tissue
