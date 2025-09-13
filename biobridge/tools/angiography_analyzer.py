import cv2
import numpy as np
from scipy import ndimage
from skimage import filters, measure, morphology
from sklearn.cluster import DBSCAN

from biobridge.blocks.cell import Cell
from biobridge.definitions.tissues.vascular import VascularTissue


class AngiographyAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer

    def analyze_angiogram(self, image):
        """
        Analyze an angiography image using advanced vessel detection techniques.

        :param image: Input angiography image (ImageJ DataArray)
        :return: Dictionary containing analysis results
        """
        # Convert ImageJ image to numpy array
        img_array = self.image_analyzer.ij.py.from_java(image)

        # Ensure the image is grayscale
        if len(img_array.shape) > 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Enhance vessel contrast
        enhanced_img = self.enhance_vessel_contrast(img_array)

        # Detect vessel centerlines
        vessel_centerlines = self.detect_vessel_centerlines(enhanced_img)

        # Segment vessels
        vessel_mask = self.segment_vessels(enhanced_img)

        # Measure vessel parameters
        vessel_measurements = self.measure_vessel_parameters(
            vessel_mask, vessel_centerlines
        )

        # Detect stenosis and occlusions
        stenosis_analysis = self.detect_stenosis(vessel_measurements)

        # Detect aneurysms
        aneurysm_analysis = self.detect_aneurysms(vessel_mask)

        # Calculate vascular density
        vascular_density = self.calculate_vascular_density(vessel_mask)

        # Detect collateral circulation
        collateral_vessels = self.detect_collateral_circulation(vessel_centerlines)

        return {
            "enhanced_image": enhanced_img,
            "vessel_centerlines": vessel_centerlines,
            "vessel_mask": vessel_mask,
            "vessel_measurements": vessel_measurements,
            "stenosis_analysis": stenosis_analysis,
            "aneurysm_analysis": aneurysm_analysis,
            "vascular_density": vascular_density,
            "collateral_vessels": collateral_vessels,
        }

    def enhance_vessel_contrast(self, image):
        """
        Enhance vessel contrast using multi-scale vessel enhancement filter.

        :param image: Input grayscale image
        :return: Vessel-enhanced image
        """
        # Apply Frangi vesselness filter at multiple scales
        scales = [1, 2, 4, 8]
        enhanced = np.zeros_like(image, dtype=np.float64)

        for scale in scales:
            # Apply Gaussian smoothing
            smoothed = filters.gaussian(image, sigma=scale)

            # Compute Hessian matrix eigenvalues
            hxx = ndimage.gaussian_filter(smoothed, sigma=scale, order=(2, 0))
            hxy = ndimage.gaussian_filter(smoothed, sigma=scale, order=(1, 1))
            hyy = ndimage.gaussian_filter(smoothed, sigma=scale, order=(0, 2))

            # Calculate eigenvalues
            trace = hxx + hyy
            det = hxx * hyy - hxy**2

            # Eigenvalues
            sqrt_discriminant = np.sqrt(np.maximum(0, trace**2 - 4 * det))
            l1 = 0.5 * (trace + sqrt_discriminant)
            l2 = 0.5 * (trace - sqrt_discriminant)

            # Frangi vesselness measure
            beta = 0.5
            c = 0.5 * np.max(image)

            rb = np.abs(l1) / (np.abs(l2) + 1e-10)
            s = np.sqrt(l1**2 + l2**2)

            vesselness = np.exp(-(rb**2) / (2 * beta**2)) * (
                1 - np.exp(-(s**2) / (2 * c**2))
            )
            vesselness[l2 > 0] = 0  # Only dark vessels on bright background

            enhanced = np.maximum(enhanced, vesselness)

        return (enhanced * 255).astype(np.uint8)

    def detect_vessel_centerlines(self, image):
        """
        Detect vessel centerlines using morphological thinning.

        :param image: Enhanced vessel image
        :return: Binary image with vessel centerlines
        """
        # Threshold the image
        thresh = filters.threshold_otsu(image)
        binary = image > thresh

        # Apply morphological operations to clean up
        binary = morphology.remove_small_objects(binary, min_size=50)
        binary = morphology.binary_closing(binary, morphology.disk(2))

        # Apply skeletonization to get centerlines
        skeleton = morphology.skeletonize(binary)

        return skeleton.astype(np.uint8) * 255

    def segment_vessels(self, image):
        """
        Segment blood vessels using adaptive thresholding and morphological operations.

        :param image: Enhanced vessel image
        :return: Binary vessel mask
        """
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Morphological operations to connect vessel segments
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Remove small objects
        binary = morphology.remove_small_objects(binary > 0, min_size=100)

        return binary.astype(np.uint8) * 255

    def measure_vessel_parameters(self, vessel_mask, centerlines):
        """
        Measure vessel parameters including diameter, length, and tortuosity.

        :param vessel_mask: Binary vessel mask
        :param centerlines: Binary centerline image
        :return: Dictionary with vessel measurements
        """
        # Label connected components
        labeled_vessels = measure.label(vessel_mask > 0)

        measurements = {
            "vessel_count": np.max(labeled_vessels),
            "total_vessel_length": np.sum(centerlines > 0),
            "vessel_segments": [],
        }

        # Analyze each vessel segment
        for region in measure.regionprops(labeled_vessels):
            if region.area > 100:  # Filter small vessels
                # Calculate approximate diameter using area and perimeter
                diameter = 2 * np.sqrt(region.area / np.pi)

                # Calculate vessel length from centerline
                vessel_roi = labeled_vessels == region.label
                centerline_roi = centerlines * vessel_roi
                vessel_length = np.sum(centerline_roi > 0)

                # Calculate tortuosity (actual length / straight-line distance)
                coords = region.coords
                if len(coords) > 1:
                    start_point = coords[0]
                    end_point = coords[-1]
                    straight_distance = np.linalg.norm(end_point - start_point)
                    tortuosity = vessel_length / (straight_distance + 1e-10)
                else:
                    tortuosity = 1.0

                measurements["vessel_segments"].append(
                    {
                        "area": region.area,
                        "diameter": diameter,
                        "length": vessel_length,
                        "tortuosity": tortuosity,
                        "centroid": region.centroid,
                    }
                )

        return measurements

    def detect_stenosis(self, vessel_measurements):
        """
        Detect potential stenosis (vessel narrowing) locations.

        :param centerlines: Binary centerline image
        :param vessel_measurements: Vessel measurement data
        :return: List of potential stenosis locations
        """
        stenosis_locations = []

        for segment in vessel_measurements["vessel_segments"]:
            # High tortuosity might indicate stenosis compensation
            if segment["tortuosity"] > 1.5:
                stenosis_locations.append(
                    {
                        "location": segment["centroid"],
                        "severity": min((segment["tortuosity"] - 1.0) * 0.5, 0.9),
                        "type": "high_tortuosity",
                    }
                )

            # Very small diameter might indicate stenosis
            avg_diameter = np.mean(
                [s["diameter"] for s in vessel_measurements["vessel_segments"]]
            )
            if segment["diameter"] < avg_diameter * 0.5:
                stenosis_locations.append(
                    {
                        "location": segment["centroid"],
                        "severity": 1.0 - (segment["diameter"] / avg_diameter),
                        "type": "diameter_reduction",
                    }
                )

        return stenosis_locations

    def detect_aneurysms(self, vessel_mask):
        """
        Detect potential aneurysms using morphological analysis.

        :param vessel_mask: Binary vessel mask
        :param original_image: Original grayscale image
        :return: List of potential aneurysm locations
        """
        # Find vessel dilations using morphological opening
        kernel = morphology.disk(5)
        opened = morphology.opening(vessel_mask > 0, kernel)
        dilations = vessel_mask - opened.astype(np.uint8) * 255

        # Label potential aneurysm regions
        labeled_dilations = measure.label(dilations > 0)
        aneurysms = []

        for region in measure.regionprops(labeled_dilations):
            if region.area > 50:  # Filter small artifacts
                # Calculate circularity (closer to 1 = more circular = more likely aneurysm)
                perimeter = region.perimeter
                circularity = (
                    4 * np.pi * region.area / (perimeter**2) if perimeter > 0 else 0
                )

                if circularity > 0.7:  # Relatively circular
                    aneurysms.append(
                        {
                            "location": region.centroid,
                            "area": region.area,
                            "circularity": circularity,
                            "risk_score": circularity * (region.area / 1000),
                        }
                    )

        return aneurysms

    def calculate_vascular_density(self, vessel_mask):
        """
        Calculate vascular density metrics.

        :param vessel_mask: Binary vessel mask
        :return: Dictionary with density measurements
        """
        total_pixels = vessel_mask.size
        vessel_pixels = np.sum(vessel_mask > 0)

        return {
            "vessel_density_ratio": vessel_pixels / total_pixels,
            "vessel_pixel_count": vessel_pixels,
            "total_pixel_count": total_pixels,
        }

    def detect_collateral_circulation(self, centerlines):
        """
        Detect potential collateral circulation patterns.

        :param centerlines: Binary centerline image
        :param vessel_mask: Binary vessel mask
        :return: Information about collateral vessels
        """
        # Use DBSCAN clustering to find vessel network patterns
        vessel_coords = np.column_stack(np.where(centerlines > 0))

        if len(vessel_coords) > 100:
            clustering = DBSCAN(eps=10, min_samples=5).fit(vessel_coords)

            # Count clusters (potential vessel networks)
            n_clusters = len(set(clustering.labels_)) - (
                1 if -1 in clustering.labels_ else 0
            )

            return {
                "network_clusters": n_clusters,
                "potential_collaterals": n_clusters
                > 3,  # More clusters might indicate collaterals
                "clustering_labels": clustering.labels_,
            }

        return {
            "network_clusters": 0,
            "potential_collaterals": False,
            "clustering_labels": [],
        }

    def visualize_angiogram_analysis(self, original_image, analysis_results):
        """
        Visualize the results of angiography analysis.

        :param original_image: Original angiogram image
        :param analysis_results: Results from analyze_angiogram method
        """
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(3, 3, figsize=(18, 15))

        # Original image
        axs[0, 0].imshow(original_image, cmap="gray")
        axs[0, 0].set_title("Original Angiogram")

        # Enhanced image
        axs[0, 1].imshow(analysis_results["enhanced_image"], cmap="hot")
        axs[0, 1].set_title("Vessel Enhancement")

        # Vessel centerlines
        axs[0, 2].imshow(analysis_results["vessel_centerlines"], cmap="gray")
        axs[0, 2].set_title("Vessel Centerlines")

        # Vessel mask
        axs[1, 0].imshow(analysis_results["vessel_mask"], cmap="gray")
        axs[1, 0].set_title("Vessel Segmentation")

        # Stenosis overlay
        stenosis_img = original_image.copy()
        for stenosis in analysis_results["stenosis_analysis"]:
            y, x = int(stenosis["location"][0]), int(stenosis["location"][1])
            cv2.circle(stenosis_img, (x, y), 5, (255,), 2)
        axs[1, 1].imshow(stenosis_img, cmap="gray")
        axs[1, 1].set_title(
            f"Stenosis Detection ({len(analysis_results['stenosis_analysis'])} found)"
        )

        # Aneurysm overlay
        aneurysm_img = original_image.copy()
        for aneurysm in analysis_results["aneurysm_analysis"]:
            y, x = int(aneurysm["location"][0]), int(aneurysm["location"][1])
            cv2.circle(stenosis_img, (x, y), 8, (255,), 2)
        axs[1, 2].imshow(aneurysm_img, cmap="gray")
        axs[1, 2].set_title(
            f"Aneurysm Detection ({len(analysis_results['aneurysm_analysis'])} found)"
        )

        # Vascular density visualization
        density = analysis_results["vascular_density"]
        axs[2, 0].bar(
            ["Vessel", "Background"],
            [
                density["vessel_pixel_count"],
                density["total_pixel_count"] - density["vessel_pixel_count"],
            ],
        )
        axs[2, 0].set_title(f"Vascular Density: {density['vessel_density_ratio']:.3f}")
        axs[2, 0].set_ylabel("Pixel Count")

        # Vessel diameter distribution
        diameters = [
            s["diameter"]
            for s in analysis_results["vessel_measurements"]["vessel_segments"]
        ]
        if diameters:
            axs[2, 1].hist(diameters, bins=20, alpha=0.7, color="blue")
            axs[2, 1].set_title("Vessel Diameter Distribution")
            axs[2, 1].set_xlabel("Diameter (pixels)")
            axs[2, 1].set_ylabel("Frequency")
        else:
            axs[2, 1].text(0.5, 0.5, "No vessels detected", ha="center", va="center")
            axs[2, 1].set_title("Vessel Diameter Distribution")

        # Tortuosity analysis
        tortuosities = [
            s["tortuosity"]
            for s in analysis_results["vessel_measurements"]["vessel_segments"]
        ]
        if tortuosities:
            axs[2, 2].hist(tortuosities, bins=20, alpha=0.7, color="red")
            axs[2, 2].set_title("Vessel Tortuosity Distribution")
            axs[2, 2].set_xlabel("Tortuosity Index")
            axs[2, 2].set_ylabel("Frequency")
        else:
            axs[2, 2].text(0.5, 0.5, "No vessels detected", ha="center", va="center")
            axs[2, 2].set_title("Vessel Tortuosity Distribution")

        for ax in axs.flat:
            if ax != axs[2, 0] and ax != axs[2, 1] and ax != axs[2, 2]:
                ax.axis("off")

        plt.tight_layout()
        plt.show()

    def create_vascular_tissue_from_angiogram(
        self, image, tissue_name: str
    ) -> VascularTissue:
        """
        Create a VascularTissue object from angiography analysis results.

        :param image: Input grayscale image
        :param tissue_name: Name for the new VascularTissue object
        :return: VascularTissue object
        """
        # Analyze the angiogram
        analysis = self.analyze_angiogram(image)

        # Calculate vessel health metrics
        vessel_measurements = analysis["vessel_measurements"]
        stenosis_count = len(analysis["stenosis_analysis"])
        aneurysm_count = len(analysis["aneurysm_analysis"])
        vascular_density = analysis["vascular_density"]["vessel_density_ratio"]

        # Calculate overall vessel health (0-100 scale)
        base_health = 90.0
        stenosis_penalty = min(stenosis_count * 10, 30)  # Max 30 point penalty
        aneurysm_penalty = min(aneurysm_count * 15, 40)  # Max 40 point penalty
        density_bonus = min(vascular_density * 20, 10)  # Max 10 point bonus

        vessel_health = max(
            0, base_health - stenosis_penalty - aneurysm_penalty + density_bonus
        )

        # Create endothelial cells based on vessel measurements
        cells = []
        for i, segment in enumerate(vessel_measurements["vessel_segments"]):
            # Create cells proportional to vessel area
            cell_count = max(1, int(segment["area"] / 100))  # One cell per 100 pixels

            for j in range(cell_count):
                cell_name = f"EndothelialCell_{i}_{j}"
                # Cell health varies based on vessel tortuosity and diameter
                cell_health_factor = 100 - (segment["tortuosity"] - 1.0) * 10
                cell_health = str(max(60, min(100, cell_health_factor)))
                cells.append(Cell(cell_name, cell_health))

        # If no vessels detected, create some default cells
        if not cells:
            for i in range(10):
                cells.append(Cell(f"EndothelialCell_{i}", "75"))

        # Calculate blood flow estimate (normalized to reasonable range)
        blood_flow = max(0.1, min(3.0, vascular_density * (vessel_health / 100) * 2.0))

        # Estimate oxygen delivery based on vessel health and density
        oxygen_delivery = max(
            0.1, min(1.0, (vessel_health / 100) * vascular_density * 1.2)
        )

        # Calculate cardiovascular risk based on pathologies found
        risk_factors = stenosis_count + aneurysm_count * 2
        cardiovascular_risk = min(risk_factors * 0.05, 0.3)  # Cap at 30%

        # Create VascularTissue object
        vascular_tissue = VascularTissue(
            name=tissue_name,
            cells=cells,
            cardiovascular_risk=cardiovascular_risk,
            blood_flow=blood_flow,
            oxygen_delivery=oxygen_delivery,
        )

        vascular_tissue.endothelial_function = max(0.1, min(1.0, vessel_health / 100))
        # Calculate atherosclerotic burden from stenosis and vessel health
        atherosclerotic_factor = max(
            0, (90 - vessel_health) / 90
        )  # Higher when health is lower
        vascular_tissue.atherosclerotic_burden = min(1.0, atherosclerotic_factor * 0.8)

        # Set vasodilation/vasoconstriction capacity based on vessel health
        health_factor = vessel_health / 100
        vascular_tissue.vasodilation_capacity = max(0.2, min(1.0, health_factor * 1.1))
        vascular_tissue.vasoconstriction_capacity = max(
            0.2, min(1.0, health_factor * 1.0)
        )

        # Set nitric oxide production based on endothelial function
        vascular_tissue.nitric_oxide_production = max(
            0.1, min(1.0, vascular_tissue.endothelial_function * 0.9)
        )

        # Set platelet aggregation inversely related to vessel health
        vascular_tissue.platelet_aggregation = max(
            0.05, min(1.0, (100 - vessel_health) / 200)
        )

        # Calculate and apply tortuosity effects
        if vessel_measurements["vessel_segments"]:
            avg_tortuosity = np.mean(
                [s["tortuosity"] for s in vessel_measurements["vessel_segments"]]
            )
            if avg_tortuosity > 1.3:  # High tortuosity indicates potential issues
                # Reduce vascular function slightly
                vascular_tissue.endothelial_function *= 0.95
                vascular_tissue.blood_flow *= 0.9

        return vascular_tissue
