from collections import deque

import cv2
import matplotlib.pyplot as plt
import numpy as np

from biobridge.tools.video_analyzer import VideoAnalyzer


class FluoroscopyAnalyzer:
    def __init__(self, image_analyzer):
        """
        Initialize the FluoroscopyAnalyzer.

        :param image_analyzer: ImageAnalyzer instance for processing individual frames
        """
        self.image_analyzer = image_analyzer
        self.video_analyzer = VideoAnalyzer()
        self.frame_history = deque(
            maxlen=10
        )  # Store last 10 frames for temporal analysis
        self.motion_history = []
        self.contrast_agent_tracking = {}

    def load_fluoroscopy_video(self, video_path):
        """
        Load a fluoroscopy video file.

        :param video_path: Path to the fluoroscopy video file
        """
        self.video_analyzer.load_video(video_path)
        print(
            f"Loaded fluoroscopy video: {self.video_analyzer.frame_count} frames at {self.video_analyzer.fps} FPS"
        )

    def analyze_frame(self, frame):
        """
        Analyze a single fluoroscopy frame with enhanced X-ray techniques.

        :param frame: Input fluoroscopy frame (numpy array)
        :return: Dictionary containing analysis results
        """
        # Ensure the frame is grayscale
        if len(frame.shape) > 2:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_frame = frame.copy()

        # Apply fluoroscopy-specific preprocessing
        preprocessed = self.preprocess_fluoroscopy_frame(gray_frame)

        # Enhanced contrast for fluoroscopy
        enhanced = self.enhance_fluoroscopy_contrast(preprocessed)

        # Detect anatomical structures
        structures = self.detect_anatomical_structures(enhanced)

        # Analyze contrast agent if present
        contrast_analysis = self.analyze_contrast_agent(enhanced)

        # Measure radiation dose estimation
        dose_estimate = self.estimate_radiation_dose(gray_frame)

        # Detect motion artifacts
        motion_artifacts = self.detect_motion_artifacts(enhanced)

        # Bone density analysis (similar to X-ray)
        bone_density = self.measure_bone_density(enhanced)

        # Store frame in history for temporal analysis
        self.frame_history.append(enhanced)

        return {
            "original_frame": gray_frame,
            "preprocessed_frame": preprocessed,
            "enhanced_frame": enhanced,
            "anatomical_structures": structures,
            "contrast_analysis": contrast_analysis,
            "dose_estimate": dose_estimate,
            "motion_artifacts": motion_artifacts,
            "bone_density": bone_density,
            "frame_quality": self.assess_frame_quality(enhanced),
        }

    def preprocess_fluoroscopy_frame(self, frame):
        """
        Apply fluoroscopy-specific preprocessing to reduce noise and enhance image quality.

        :param frame: Input grayscale frame
        :return: Preprocessed frame
        """
        # Apply Gaussian blur to reduce noise common in fluoroscopy
        denoised = cv2.GaussianBlur(frame, (3, 3), 0.8)

        # Apply morphological operations to enhance structures
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)

        # Gamma correction for fluoroscopy images
        gamma = 1.2
        gamma_corrected = np.power(opened / 255.0, gamma) * 255.0
        gamma_corrected = gamma_corrected.astype(np.uint8)

        return gamma_corrected

    def enhance_fluoroscopy_contrast(self, frame):
        """
        Enhanced contrast adjustment specifically for fluoroscopy images.

        :param frame: Input frame
        :return: Contrast-enhanced frame
        """
        # Use CLAHE with parameters optimized for fluoroscopy
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(12, 12))
        enhanced = clahe.apply(frame)

        # Additional histogram stretching
        min_val, max_val = np.percentile(enhanced, [2, 98])
        stretched = np.clip((enhanced - min_val) * 255 / (max_val - min_val), 0, 255)

        return stretched.astype(np.uint8)

    def detect_anatomical_structures(self, frame):
        """
        Detect and segment anatomical structures in fluoroscopy images.

        :param frame: Enhanced fluoroscopy frame
        :return: Dictionary of detected structures
        """
        # Edge detection with parameters tuned for medical imaging
        edges = cv2.Canny(frame, 50, 150)

        # Hough line detection for linear structures (bones, instruments)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10
        )

        # Contour detection for organ boundaries
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter contours by area to identify significant structures
        significant_contours = [c for c in contours if cv2.contourArea(c) > 100]

        # Circle detection for round structures (joints, instruments)
        circles = cv2.HoughCircles(
            frame,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=5,
            maxRadius=50,
        )

        return {
            "edges": edges,
            "lines": lines if lines is not None else [],
            "contours": significant_contours,
            "circles": circles if circles is not None else np.array([]),
        }

    def analyze_contrast_agent(self, frame):
        """
        Analyze contrast agent flow and distribution in fluoroscopy.

        :param frame: Enhanced fluoroscopy frame
        :return: Contrast agent analysis results
        """
        # Threshold for high-intensity areas (contrast agent)
        _, contrast_mask = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY)

        # Find connected components in contrast areas
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            contrast_mask
        )

        # Analyze contrast agent regions
        contrast_regions = []
        for i in range(1, num_labels):  # Skip background (0)
            area = stats[i, cv2.CC_STAT_AREA]
            centroid = centroids[i]
            if area > 10:  # Filter small noise
                contrast_regions.append(
                    {
                        "area": area,
                        "centroid": centroid,
                        "intensity": np.mean(frame[labels == i]),
                    }
                )

        # Calculate total contrast volume
        total_contrast_volume = sum(region["area"] for region in contrast_regions)

        return {
            "contrast_mask": contrast_mask,
            "regions": contrast_regions,
            "total_volume": total_contrast_volume,
            "region_count": len(contrast_regions),
        }

    def estimate_radiation_dose(self, frame):
        """
        Estimate radiation dose based on image characteristics.

        :param frame: Original grayscale frame
        :return: Radiation dose estimate
        """
        # Calculate image statistics
        mean_intensity = np.mean(frame)
        std_intensity = np.std(frame)

        # Noise estimation (higher noise often indicates lower dose)
        noise_level = std_intensity / mean_intensity if mean_intensity > 0 else 0

        # Simple dose estimation based on image quality metrics
        # This is a simplified model - real dose estimation requires calibration
        dose_factor = mean_intensity / 255.0
        quality_factor = 1.0 / (1.0 + noise_level)

        estimated_dose = dose_factor * quality_factor * 100  # Arbitrary units

        return {
            "estimated_dose": estimated_dose,
            "noise_level": noise_level,
            "image_quality_score": quality_factor,
        }

    def detect_motion_artifacts(self, frame):
        """
        Detect motion artifacts in fluoroscopy images.

        :param frame: Enhanced frame
        :return: Motion artifact analysis
        """
        if len(self.frame_history) < 2:
            return {"motion_detected": False, "motion_magnitude": 0}

        # Compare current frame with previous frame
        prev_frame = self.frame_history[-2]

        # Calculate frame difference
        frame_diff = cv2.absdiff(frame, prev_frame)

        # Threshold difference to find significant changes
        _, motion_mask = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

        # Calculate motion magnitude
        motion_magnitude = np.sum(motion_mask) / motion_mask.size

        # Store motion history
        self.motion_history.append(motion_magnitude)
        if len(self.motion_history) > 50:  # Keep last 50 measurements
            self.motion_history.pop(0)

        return {
            "motion_detected": motion_magnitude > 0.05,  # 5% threshold
            "motion_magnitude": motion_magnitude,
            "motion_mask": motion_mask,
            "frame_difference": frame_diff,
        }

    def measure_bone_density(self, frame):
        """
        Measure bone density from fluoroscopy frame (adapted from X-ray analyzer).

        :param frame: Enhanced fluoroscopy frame
        :return: Bone density measurements
        """
        # Calculate histogram
        hist, bins = np.histogram(frame.flatten(), bins=256, range=(0, 256))

        # Focus on high-intensity regions (bone)
        bone_threshold = 150
        bone_pixels = frame[frame > bone_threshold]

        if len(bone_pixels) > 0:
            avg_bone_density = np.mean(bone_pixels)
            bone_area = len(bone_pixels)
        else:
            avg_bone_density = 0
            bone_area = 0

        return {
            "average_bone_density": avg_bone_density,
            "bone_area": bone_area,
            "histogram": hist,
            "bins": bins,
        }

    def assess_frame_quality(self, frame):
        """
        Assess the quality of a fluoroscopy frame.

        :param frame: Enhanced frame
        :return: Quality assessment score (0-100)
        """
        # Calculate various quality metrics

        # Contrast measure
        contrast = np.std(frame)

        # Sharpness measure (Laplacian variance)
        laplacian_var = cv2.Laplacian(frame, cv2.CV_64F).var()

        # Dynamic range
        dynamic_range = np.max(frame) - np.min(frame)

        # Normalize and combine metrics
        contrast_score = min(contrast / 50.0, 1.0) * 40
        sharpness_score = min(laplacian_var / 1000.0, 1.0) * 40
        range_score = min(dynamic_range / 255.0, 1.0) * 20

        total_score = contrast_score + sharpness_score + range_score

        return {
            "overall_score": total_score,
            "contrast": contrast,
            "sharpness": laplacian_var,
            "dynamic_range": dynamic_range,
        }

    def analyze_fluoroscopy_sequence(self, frame_interval=1, max_frames=None):
        """
        Analyze an entire fluoroscopy video sequence.

        :param frame_interval: Interval between analyzed frames
        :param max_frames: Maximum number of frames to analyze
        :return: Sequence analysis results
        """
        results = []
        temporal_analysis = {
            "motion_timeline": [],
            "contrast_timeline": [],
            "quality_timeline": [],
        }

        frame_count = min(
            max_frames or self.video_analyzer.frame_count,
            self.video_analyzer.frame_count,
        )

        for i in range(0, frame_count, frame_interval):
            frame = self.video_analyzer.get_frame(i)
            if frame is not None:
                analysis = self.analyze_frame(frame)
                results.append(
                    {
                        "frame_number": i,
                        "timestamp": i / self.video_analyzer.fps,
                        "analysis": analysis,
                    }
                )

                # Store temporal data
                temporal_analysis["motion_timeline"].append(
                    analysis["motion_artifacts"]["motion_magnitude"]
                )
                temporal_analysis["contrast_timeline"].append(
                    analysis["contrast_analysis"]["total_volume"]
                )
                temporal_analysis["quality_timeline"].append(
                    analysis["frame_quality"]["overall_score"]
                )

        # Add temporal analysis summary
        temporal_analysis["avg_motion"] = np.mean(temporal_analysis["motion_timeline"])
        temporal_analysis["peak_contrast"] = np.max(
            temporal_analysis["contrast_timeline"]
        )
        temporal_analysis["avg_quality"] = np.mean(
            temporal_analysis["quality_timeline"]
        )

        return {
            "frame_results": results,
            "temporal_analysis": temporal_analysis,
            "sequence_summary": self.generate_sequence_summary(temporal_analysis),
        }

    def generate_sequence_summary(self, temporal_analysis):
        """
        Generate a summary of the fluoroscopy sequence analysis.

        :param temporal_analysis: Temporal analysis data
        :return: Summary dictionary
        """
        return {
            "motion_assessment": (
                "High"
                if temporal_analysis["avg_motion"] > 0.1
                else "Medium" if temporal_analysis["avg_motion"] > 0.05 else "Low"
            ),
            "contrast_peak_detected": temporal_analysis["peak_contrast"] > 0,
            "overall_quality": (
                "Excellent"
                if temporal_analysis["avg_quality"] > 80
                else (
                    "Good"
                    if temporal_analysis["avg_quality"] > 60
                    else "Fair" if temporal_analysis["avg_quality"] > 40 else "Poor"
                )
            ),
            "recommendations": self.generate_recommendations(temporal_analysis),
        }

    def generate_recommendations(self, temporal_analysis):
        """
        Generate recommendations based on fluoroscopy analysis.

        :param temporal_analysis: Temporal analysis data
        :return: List of recommendations
        """
        recommendations = []

        if temporal_analysis["avg_motion"] > 0.1:
            recommendations.append(
                "Consider patient stabilization - high motion detected"
            )

        if temporal_analysis["avg_quality"] < 60:
            recommendations.append(
                "Image quality is suboptimal - check equipment settings"
            )

        if temporal_analysis["peak_contrast"] == 0:
            recommendations.append("No contrast agent detected - verify injection")

        if len(recommendations) == 0:
            recommendations.append("Fluoroscopy sequence quality is acceptable")

        return recommendations

    def visualize_fluoroscopy_analysis(self, frame_analysis):
        """
        Visualize the results of fluoroscopy frame analysis.

        :param frame_analysis: Results from analyze_frame method
        """
        fig, axs = plt.subplots(3, 3, figsize=(18, 15))

        # Original frame
        axs[0, 0].imshow(frame_analysis["original_frame"], cmap="gray")
        axs[0, 0].set_title("Original Fluoroscopy Frame")

        # Enhanced frame
        axs[0, 1].imshow(frame_analysis["enhanced_frame"], cmap="gray")
        axs[0, 1].set_title("Enhanced Frame")

        # Anatomical structures - edges
        axs[0, 2].imshow(frame_analysis["anatomical_structures"]["edges"], cmap="gray")
        axs[0, 2].set_title("Detected Edges")

        # Contrast agent analysis
        axs[1, 0].imshow(
            frame_analysis["contrast_analysis"]["contrast_mask"], cmap="hot"
        )
        axs[1, 0].set_title("Contrast Agent Detection")

        # Motion artifacts
        if "motion_mask" in frame_analysis["motion_artifacts"]:
            axs[1, 1].imshow(
                frame_analysis["motion_artifacts"]["motion_mask"], cmap="Reds"
            )
            axs[1, 1].set_title("Motion Artifacts")

        # Frame difference
        if "frame_difference" in frame_analysis["motion_artifacts"]:
            axs[1, 2].imshow(
                frame_analysis["motion_artifacts"]["frame_difference"], cmap="gray"
            )
            axs[1, 2].set_title("Frame Difference")

        # Bone density histogram
        bone_data = frame_analysis["bone_density"]
        axs[2, 0].bar(
            bone_data["bins"][:-1], bone_data["histogram"], width=1, edgecolor="none"
        )
        axs[2, 0].set_title(
            f"Intensity Histogram\nAvg Bone Density: {bone_data['average_bone_density']:.2f}"
        )
        axs[2, 0].set_xlabel("Pixel Intensity")
        axs[2, 0].set_ylabel("Frequency")

        # Quality metrics
        quality = frame_analysis["frame_quality"]
        metrics = ["Overall", "Contrast", "Sharpness", "Range"]
        values = [
            quality["overall_score"],
            quality["contrast"],
            quality["sharpness"] / 10,
            quality["dynamic_range"] / 2.55,
        ]
        axs[2, 1].bar(metrics, values)
        axs[2, 1].set_title("Quality Metrics")
        axs[2, 1].set_ylabel("Score")

        # Dose estimation
        dose = frame_analysis["dose_estimate"]
        dose_info = f"Estimated Dose: {dose['estimated_dose']:.2f}\n"
        dose_info += f"Noise Level: {dose['noise_level']:.3f}\n"
        dose_info += f"Quality Score: {dose['image_quality_score']:.3f}"
        axs[2, 2].text(0.1, 0.5, dose_info, fontsize=12, verticalalignment="center")
        axs[2, 2].set_title("Radiation Dose Estimate")

        # Turn off axes for image plots
        for i in range(3):
            for j in range(3):
                if i < 2 or j < 1:
                    axs[i, j].axis("off")

        # Keep axes on for plots
        axs[2, 0].axis("on")
        axs[2, 1].axis("on")
        axs[2, 2].axis("off")

        plt.tight_layout()
        plt.show()

    def create_enhanced_fluoroscopy_video(
        self, output_path, enhancement_type="contrast"
    ):
        """
        Create an enhanced version of the fluoroscopy video.

        :param output_path: Path to save enhanced video
        :param enhancement_type: Type of enhancement ("contrast", "edges", "motion")
        """
        frame_width = int(self.video_analyzer.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.video_analyzer.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.video_analyzer.fps

        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        out = cv2.VideoWriter(
            output_path, fourcc, fps, (frame_width, frame_height), False
        )

        for i in range(self.video_analyzer.frame_count):
            frame = self.video_analyzer.get_frame(i)
            if frame is not None:
                gray_frame = (
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    if len(frame.shape) > 2
                    else frame
                )

                if enhancement_type == "contrast":
                    enhanced = self.enhance_fluoroscopy_contrast(gray_frame)
                elif enhancement_type == "edges":
                    enhanced = self.detect_anatomical_structures(gray_frame)["edges"]
                elif enhancement_type == "motion":
                    motion_analysis = self.detect_motion_artifacts(gray_frame)
                    enhanced = motion_analysis.get("motion_mask", gray_frame)
                else:
                    enhanced = gray_frame

                out.write(enhanced)

        out.release()
        print(f"Enhanced fluoroscopy video saved to {output_path}")

    def close(self):
        """Release resources."""
        self.video_analyzer.close()
