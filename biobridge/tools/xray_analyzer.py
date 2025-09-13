import random

import cv2
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from biobridge.blocks.cell import Cell
from biobridge.definitions.tissues.bone import BoneTissue


class XrayAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer

    def analyze_xray(self, image):
        """
        Analyze an X-ray image using advanced techniques.

        :param image: Input X-ray image (ImageJ DataArray)
        :return: Dictionary containing analysis results
        """
        # Convert ImageJ image to numpy array
        img_array = self.image_analyzer.ij.py.from_java(image)

        # Ensure the image is grayscale
        if len(img_array.shape) > 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Enhance contrast
        enhanced_img = self.enhance_contrast(img_array)

        # Detect edges
        edges = self.detect_edges(enhanced_img)

        # Segment the image
        segmented = self.segment_image(enhanced_img)

        # Detect anomalies
        anomalies = self.detect_anomalies(enhanced_img, segmented)

        # Measure bone density
        bone_density = self.measure_bone_density(enhanced_img)

        return {
            "enhanced_image": enhanced_img,
            "edges": edges,
            "segmented_image": segmented,
            "anomalies": anomalies,
            "bone_density": bone_density,
        }

    def enhance_contrast(self, image):
        """
        Enhance the contrast of the X-ray image using adaptive histogram equalization.

        :param image: Input grayscale image
        :return: Contrast-enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image.astype(np.uint8))

    def detect_edges(self, image):
        """
        Detect edges in the X-ray image using Canny edge detection with automatic threshold selection.

        :param image: Input grayscale image
        :return: Edge image
        """
        sigma = np.median(image) / 0.3
        lower = int(max(0, (1.0 - 0.33) * sigma))
        upper = int(min(255, (1.0 + 0.33) * sigma))
        return cv2.Canny(image, lower, upper)

    def segment_image(self, image):
        """
        Segment the X-ray image using K-means clustering.

        :param image: Input grayscale image
        :return: Segmented image
        """
        # Reshape the image to a 2D array of pixels
        pixel_values = image.reshape((-1, 1))
        pixel_values = np.float32(pixel_values)

        # Define criteria and apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 3  # number of clusters
        pixel_values = np.asarray(pixel_values)
        _, labels, centers = cv2.kmeans(
            pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        # Convert back to 8-bit values
        centers = np.uint8(centers)

        # Reshape labels back to the original image dimensions
        segmented_image = centers[labels.flatten()].reshape(image.shape)

        return segmented_image

    def detect_anomalies(self, image, segmented):
        """
        Detect potential anomalies in the X-ray image using Isolation Forest.

        :param image: Original grayscale image
        :param segmented: Segmented image
        :return: List of potential anomalies (coordinates and scores)
        """
        # Prepare the data
        features = np.column_stack(
            (
                image.flatten(),
                segmented.flatten(),
                np.indices(image.shape).reshape(2, -1).T,
            )
        )

        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Apply Isolation Forest
        clf = IsolationForest(contamination=0.01, random_state=42)
        anomaly_labels = clf.fit_predict(features_normalized)

        # Find anomaly coordinates
        anomaly_coords = np.column_stack(
            np.where(anomaly_labels.reshape(image.shape) == -1)
        )

        # Calculate anomaly scores
        anomaly_scores = -clf.score_samples(features_normalized)
        anomaly_scores = anomaly_scores.reshape(image.shape)

        return [
            {"coord": coord, "score": anomaly_scores[coord[0], coord[1]]}
            for coord in anomaly_coords
        ]

    def measure_bone_density(self, image):
        """
        Measure approximate bone density from the X-ray image using histogram analysis.

        :param image: Input grayscale image
        :return: Estimated bone density value and histogram
        """
        # Calculate histogram
        hist, bins = np.histogram(image.flatten(), bins=256, range=(0, 256))

        # Estimate bone density as the weighted average of pixel intensities
        total_intensity = np.sum(hist * bins[:-1])
        total_pixels = np.sum(hist)
        avg_density = total_intensity / total_pixels if total_pixels > 0 else 0

        return {"average_density": avg_density, "histogram": hist, "bins": bins}

    def visualize_xray_analysis(self, original_image, analysis_results):
        """
        Visualize the results of X-ray analysis.

        :param original_image: Original X-ray image
        :param analysis_results: Results from analyze_xray method
        """
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(2, 3, figsize=(15, 10))

        # Original image
        axs[0, 0].imshow(original_image, cmap="gray")
        axs[0, 0].set_title("Original X-ray")

        # Enhanced image
        axs[0, 1].imshow(analysis_results["enhanced_image"], cmap="gray")
        axs[0, 1].set_title("Enhanced X-ray")

        # Edge detection
        axs[0, 2].imshow(analysis_results["edges"], cmap="gray")
        axs[0, 2].set_title("Edge Detection")

        # Segmentation
        axs[1, 0].imshow(analysis_results["segmented_image"], cmap="nipy_spectral")
        axs[1, 0].set_title("Segmentation")

        # Anomaly detection
        anomaly_img = original_image.copy()
        for anomaly in analysis_results["anomalies"]:
            y, x = anomaly["coord"]
            anomaly_img[y, x] = 255  # Mark anomalies as white pixels
        axs[1, 1].imshow(anomaly_img, cmap="gray")
        axs[1, 1].set_title("Anomaly Detection")

        # Bone density histogram
        density_results = analysis_results["bone_density"]
        axs[1, 2].bar(
            density_results["bins"][:-1],
            density_results["histogram"],
            width=1,
            edgecolor="none",
        )
        axs[1, 2].set_title(
            f"Bone Density Histogram\nAvg: {density_results['average_density']:.2f}"
        )
        axs[1, 2].set_xlabel("Pixel Intensity")
        axs[1, 2].set_ylabel("Frequency")

        for ax in axs.flat:
            ax.axis("off")
        axs[1, 2].axis("on")

        plt.tight_layout()
        plt.show()

    def create_bone_tissue_from_xray(self, image, tissue_name: str) -> BoneTissue:
        """
        Create a BoneTissue object from XrayAnalyzer results.
        :param image: Input grayscale image
        :param tissue_name: Name for the new BoneTissue object
        :return: BoneTissue object
        """
        # Extract relevant information from xray_analysis
        bone_density_info = self.measure_bone_density(image)
        average_density = bone_density_info["average_density"]

        # Normalize average density to a 0-2 scale for mineral_density
        mineral_density = (average_density / 255) * 2

        # Create cells based on segmented image
        segmented_image = self.segment_image(image)

        # Calculate cancer risk based on anomalies
        # More anomalies might indicate higher cancer risk
        anomaly_count = len(self.detect_anomalies(image, segmented_image))
        cancer_risk = min(anomaly_count * 0.001, 0.1)  # Cap at 10%

        unique_values, counts = np.unique(segmented_image, return_counts=True)
        cells = []
        for value, count in zip(unique_values, counts):
            for i in range(
                int(count / 1000)
            ):  # Create a cell for every 1000 pixels of each segment
                cell_name = f"BoneCell_{value}_{i}"
                cell_health = str(
                    random.uniform(85, 100)
                )  # Assuming relatively healthy cells
                cells.append(Cell(cell_name, cell_health))

        # Create and return the BoneTissue object
        bone_tissue = BoneTissue(
            name=tissue_name,
            cells=cells,
            cancer_risk=cancer_risk,
            mineral_density=mineral_density,
        )

        # Adjust osteoclast and osteoblast activity based on edge detection
        edge_percentage = (
            np.sum(self.detect_edges(image)) / self.detect_edges(image).size
        )
        bone_tissue.osteoclast_activity = 0.01 + (
            edge_percentage * 0.05
        )  # More edges might indicate more remodeling
        bone_tissue.osteoblast_activity = 0.02 + (edge_percentage * 0.05)

        return bone_tissue
