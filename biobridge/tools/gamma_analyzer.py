import numpy as np
import cv2
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import random
from biobridge.definitions.tissues.radiation_affected import RadiationAffectedTissue
from biobridge.blocks.cell import Cell
from biobridge.tools.xray_analyzer import XrayAnalyzer, BoneTissue


class GammaRayAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer

    def analyze_gamma_ray(self, image):
        """
        Analyze a gamma ray image using advanced techniques.

        :param image: Input gamma ray image (ImageJ DataArray)
        :return: Dictionary containing analysis results
        """
        # Convert ImageJ image to numpy array
        img_array = self.image_analyzer.ij.py.from_java(image)

        # Ensure the image is grayscale
        if len(img_array.shape) > 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply noise reduction
        denoised_img = self.reduce_noise(img_array)

        # Enhance contrast
        enhanced_img = self.enhance_contrast(denoised_img)

        # Detect hot spots
        hot_spots = self.detect_hot_spots(enhanced_img)

        # Segment the image
        segmented = self.segment_image(enhanced_img)

        # Detect anomalies
        anomalies = self.detect_anomalies(enhanced_img, segmented)

        # Measure radiation intensity
        radiation_intensity = self.measure_radiation_intensity(enhanced_img)

        return {
            "denoised_image": denoised_img,
            "enhanced_image": enhanced_img,
            "hot_spots": hot_spots,
            "segmented_image": segmented,
            "anomalies": anomalies,
            "radiation_intensity": radiation_intensity
        }

    def reduce_noise(self, image):
        """
        Reduce noise in the gamma ray image using Non-local Means Denoising.

        :param image: Input grayscale image
        :return: Denoised image
        """
        return cv2.fastNlMeansDenoising(image, None, h=10, searchWindowSize=21, templateWindowSize=7)

    def enhance_contrast(self, image):
        """
        Enhance the contrast of the gamma ray image using adaptive histogram equalization.

        :param image: Input grayscale image
        :return: Contrast-enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image.astype(np.uint8))

    def detect_hot_spots(self, image):
        """
        Detect hot spots in the gamma ray image using thresholding.

        :param image: Input grayscale image
        :return: Binary image with hot spots
        """
        _, hot_spots = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return hot_spots

    def segment_image(self, image):
        """
        Segment the gamma ray image using K-means clustering.

        :param image: Input grayscale image
        :return: Segmented image
        """
        # Reshape the image to a 2D array of pixels
        pixel_values = image.reshape((-1, 1))
        pixel_values = np.float32(pixel_values)

        # Define criteria and apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 5  # number of clusters (increased for more detailed segmentation)
        pixel_values = np.asarray(pixel_values)
        _, labels, centers = cv2.kmeans(pixel_values, k, np.array([]), criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Convert back to 8-bit values
        centers = np.uint8(centers)

        # Reshape labels back to the original image dimensions
        segmented_image = centers[labels.flatten()].reshape(image.shape)

        return segmented_image

    def detect_anomalies(self, image, segmented):
        """
        Detect potential anomalies in the gamma ray image using Isolation Forest.

        :param image: Original grayscale image
        :param segmented: Segmented image
        :return: List of potential anomalies (coordinates and scores)
        """
        # Prepare the data
        features = np.column_stack((
            image.flatten(),
            segmented.flatten(),
            np.indices(image.shape).reshape(2, -1).T
        ))

        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Apply Isolation Forest
        clf = IsolationForest(contamination=0.01, random_state=42)
        anomaly_labels = clf.fit_predict(features_normalized)

        # Find anomaly coordinates
        anomaly_coords = np.column_stack(np.where(anomaly_labels.reshape(image.shape) == -1))

        # Calculate anomaly scores
        anomaly_scores = -clf.score_samples(features_normalized)
        anomaly_scores = anomaly_scores.reshape(image.shape)

        return [{"coord": coord, "score": anomaly_scores[coord[0], coord[1]]}
                for coord in anomaly_coords]

    def measure_radiation_intensity(self, image):
        """
        Measure radiation intensity from the gamma ray image using histogram analysis.

        :param image: Input grayscale image
        :return: Estimated radiation intensity value and histogram
        """
        # Calculate histogram
        hist, bins = np.histogram(image.flatten(), bins=256, range=(0, 256))

        # Estimate radiation intensity as the weighted average of pixel intensities
        total_intensity = np.sum(hist * bins[:-1])
        total_pixels = np.sum(hist)
        avg_intensity = total_intensity / total_pixels if total_pixels > 0 else 0

        return {
            "average_intensity": avg_intensity,
            "histogram": hist,
            "bins": bins
        }

    def visualize_gamma_ray_analysis(self, original_image, analysis_results):
        """
        Visualize the results of gamma ray analysis.

        :param original_image: Original gamma ray image
        :param analysis_results: Results from analyze_gamma_ray method
        """
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(2, 3, figsize=(15, 10))

        # Original image
        axs[0, 0].imshow(original_image, cmap='gray')
        axs[0, 0].set_title('Original Gamma Ray Image')

        # Denoised image
        axs[0, 1].imshow(analysis_results['denoised_image'], cmap='gray')
        axs[0, 1].set_title('Denoised Image')

        # Enhanced image
        axs[0, 2].imshow(analysis_results['enhanced_image'], cmap='gray')
        axs[0, 2].set_title('Enhanced Image')

        # Hot spots
        axs[1, 0].imshow(analysis_results['hot_spots'], cmap='hot')
        axs[1, 0].set_title('Hot Spots')

        # Segmentation
        axs[1, 1].imshow(analysis_results['segmented_image'], cmap='nipy_spectral')
        axs[1, 1].set_title('Segmentation')

        # Radiation intensity histogram
        intensity_results = analysis_results['radiation_intensity']
        axs[1, 2].bar(intensity_results['bins'][:-1], intensity_results['histogram'],
                      width=1, edgecolor='none')
        axs[1, 2].set_title(f"Radiation Intensity Histogram\nAvg: {intensity_results['average_intensity']:.2f}")
        axs[1, 2].set_xlabel('Pixel Intensity')
        axs[1, 2].set_ylabel('Frequency')

        for ax in axs.flat:
            ax.axis('off')
        axs[1, 2].axis('on')

        plt.tight_layout()
        plt.show()

    def create_radiation_affected_tissue(self, image, tissue_name: str) -> RadiationAffectedTissue:
        """
        Create a RadiationAffectedTissue object from GammaRayAnalyzer results.
        :param image: Input grayscale image
        :param tissue_name: Name for the new RadiationAffectedTissue object
        :return: RadiationAffectedTissue object
        """
        # Extract relevant information from gamma_ray_analysis
        radiation_intensity_info = self.measure_radiation_intensity(image)
        average_intensity = radiation_intensity_info['average_intensity']

        # Normalize average intensity to a 0-1 scale for radiation_level
        radiation_level = average_intensity / 255

        # Create cells based on segmented image
        segmented_image = self.segment_image(image)

        # Calculate mutation risk based on anomalies
        # More anomalies might indicate higher mutation risk
        anomaly_count = len(self.detect_anomalies(image, segmented_image))
        mutation_risk = min(anomaly_count * 0.002, 0.2)  # Cap at 20%

        unique_values, counts = np.unique(segmented_image, return_counts=True)
        cells = []
        for value, count in zip(unique_values, counts):
            for i in range(int(count / 1000)):  # Create a cell for every 1000 pixels of each segment
                cell_name = f"RadiationAffectedCell_{value}_{i}"
                cell_health = str(random.uniform(70, 100))  # Assuming potentially damaged cells
                cells.append(Cell(cell_name, cell_health))

        # Create and return the RadiationAffectedTissue object
        radiation_affected_tissue = RadiationAffectedTissue(
            name=tissue_name,
            cells=cells,
            mutation_rate=mutation_risk,
            radiation_level=radiation_level,
            tissue_type="radiation_affected"
        )

        # Adjust DNA repair rate based on hot spots
        hot_spot_percentage = np.sum(self.detect_hot_spots(image)) / self.detect_hot_spots(image).size
        radiation_affected_tissue.dna_repair_rate = 0.05 - (
                    hot_spot_percentage * 0.02)  # More hot spots might indicate lower repair rate

        return radiation_affected_tissue

    def create_bone_tissue_from_gamma(self, image, tissue_name: str) -> BoneTissue:
        """
        Create a BoneTissue object from GammaRayAnalyzer results.
        :param image: Input grayscale image
        :param tissue_name: Name for the new BoneTissue object
        :return: BoneTissue object
        """
        # Extract relevant information from gamma_ray_analysis
        radiation_intensity_info = self.measure_radiation_intensity(image)
        average_intensity = radiation_intensity_info['average_intensity']

        # Normalize average intensity to a 0-2 scale for mineral_density
        # In gamma imaging, higher intensity might indicate lower density due to increased radiation passage
        mineral_density = 2 - (average_intensity / 255) * 2

        # Create cells based on segmented image
        segmented_image = self.segment_image(image)

        # Calculate cancer risk based on anomalies and radiation level
        anomaly_count = len(self.detect_anomalies(image, segmented_image))
        radiation_level = average_intensity / 255
        cancer_risk = min((anomaly_count * 0.001 + radiation_level * 0.1), 0.2)  # Cap at 20%

        unique_values, counts = np.unique(segmented_image, return_counts=True)
        cells = []
        for value, count in zip(unique_values, counts):
            for i in range(int(count / 1000)):  # Create a cell for every 1000 pixels of each segment
                cell_name = f"BoneCell_{value}_{i}"
                cell_health = str(
                    random.uniform(80, 100))  # Assuming relatively healthy cells, but potentially affected by radiation
                cells.append(Cell(cell_name, cell_health))

        # Create and return the BoneTissue object
        bone_tissue = BoneTissue(
            name=tissue_name,
            cells=cells,
            cancer_risk=cancer_risk,
            mineral_density=mineral_density
        )

        # Adjust osteoclast and osteoblast activity based on hot spots
        hot_spot_percentage = np.sum(self.detect_hot_spots(image)) / self.detect_hot_spots(image).size
        bone_tissue.osteoclast_activity = 0.02 + (
                    hot_spot_percentage * 0.08)  # More hot spots might indicate increased bone resorption
        bone_tissue.osteoblast_activity = 0.02 + (
                    hot_spot_percentage * 0.05)  # Slightly lower increase in bone formation

        return bone_tissue

    def compare_xray_and_gamma_bone_analysis(self, xray_image, gamma_image, tissue_name: str) -> dict:
        """
        Compare bone analysis results from X-ray and gamma ray images.

        :param xray_image: X-ray image of the bone
        :param gamma_image: Gamma ray image of the bone
        :param tissue_name: Name for the bone tissue
        :return: Dictionary containing comparison results
        """
        # Assuming we have access to XrayAnalyzer
        xray_analyzer = XrayAnalyzer(self.image_analyzer)

        xray_bone = xray_analyzer.create_bone_tissue_from_xray(xray_image, f"{tissue_name}_xray")
        gamma_bone = self.create_bone_tissue_from_gamma(gamma_image, f"{tissue_name}_gamma")

        comparison = {
            "tissue_name": tissue_name,
            "xray_analysis": {
                "mineral_density": xray_bone.mineral_density,
                "cancer_risk": xray_bone.cancer_risk,
                "osteoclast_activity": xray_bone.osteoclast_activity,
                "osteoblast_activity": xray_bone.osteoblast_activity,
                "average_cell_health": xray_bone.get_average_cell_health()
            },
            "gamma_analysis": {
                "mineral_density": gamma_bone.mineral_density,
                "cancer_risk": gamma_bone.cancer_risk,
                "osteoclast_activity": gamma_bone.osteoclast_activity,
                "osteoblast_activity": gamma_bone.osteoblast_activity,
                "average_cell_health": gamma_bone.get_average_cell_health()
            },
            "differences": {
                "mineral_density": gamma_bone.mineral_density - xray_bone.mineral_density,
                "cancer_risk": gamma_bone.cancer_risk - xray_bone.cancer_risk,
                "osteoclast_activity": gamma_bone.osteoclast_activity - xray_bone.osteoclast_activity,
                "osteoblast_activity": gamma_bone.osteoblast_activity - xray_bone.osteoblast_activity,
                "average_cell_health": gamma_bone.get_average_cell_health() - xray_bone.get_average_cell_health()
            }
        }

        return comparison
