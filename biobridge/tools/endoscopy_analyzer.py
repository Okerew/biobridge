import cv2
import numpy as np
from skimage import feature, measure, morphology
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class EndoscopyAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer
        # Color ranges for different tissue conditions in HSV space
        self.tissue_color_ranges = {
            "healthy_mucosa": {
                "hue": (5, 25),
                "saturation": (40, 120),
                "value": (80, 200),
            },
            "inflamed": {"hue": (0, 15), "saturation": (120, 255), "value": (100, 255)},
            "ulcerated": {
                "hue": (160, 180),
                "saturation": (30, 100),
                "value": (50, 150),
            },
            "polyp": {"hue": (10, 30), "saturation": (80, 180), "value": (120, 220)},
            "bleeding": {"hue": (0, 10), "saturation": (200, 255), "value": (50, 200)},
            "barrett": {"hue": (20, 40), "saturation": (60, 140), "value": (90, 180)},
        }

        # Texture features for tissue classification
        self.texture_params = {"patch_size": 32, "n_bins": 256, "multichannel": True}

    def analyze_endoscopy_image(
        self, image, endoscopy_type="gastric", enhanced_processing=True
    ):
        """
        Analyze an endoscopic image using advanced computer vision techniques.

        :param image: Input endoscopic image (2D or 3D array)
        :param endoscopy_type: Type of endoscopy ('gastric', 'colonoscopy', 'esophageal')
        :param enhanced_processing: Whether to apply enhanced processing techniques
        :return: Dictionary containing comprehensive analysis results
        """
        # Convert from ImageJ if needed
        if hasattr(image, "getProcessor"):
            rgb_image = self.image_analyzer.ij.py.from_java(image)
        else:
            rgb_image = np.array(image)

        # Ensure RGB format
        if len(rgb_image.shape) == 2:
            rgb_image = np.stack([rgb_image] * 3, axis=-1)
        elif rgb_image.shape[-1] == 4:  # RGBA
            rgb_image = rgb_image[:, :, :3]

        # Normalize to 0-255 range
        if rgb_image.max() <= 1.0:
            rgb_image = (rgb_image * 255).astype(np.uint8)

        # Convert to different color spaces
        hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
        lab_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)

        # Enhance image quality
        if enhanced_processing:
            enhanced_image = self.enhance_endoscopy_image(rgb_image)
        else:
            enhanced_image = rgb_image

        # Segment different tissue types and conditions
        tissue_segmentation = self.segment_endoscopy_tissues(hsv_image)

        # Detect edges and boundaries
        edges = self.detect_endoscopy_edges(enhanced_image)

        # Analyze texture patterns
        texture_analysis = self.analyze_texture_patterns(enhanced_image)

        # Detect abnormalities
        abnormalities = self.detect_abnormalities(
            rgb_image, hsv_image)

        # Measure lesions and structures
        measurements = self.measure_endoscopy_features(tissue_segmentation, rgb_image)

        # Classify tissue health
        tissue_health = self.classify_tissue_health(
            rgb_image, tissue_segmentation, texture_analysis
        )

        # Detect specific conditions based on endoscopy type
        specific_findings = self.detect_specific_conditions(
         tissue_segmentation, endoscopy_type
        )

        # Calculate severity scores
        severity_scores = self.calculate_severity_scores(abnormalities, tissue_health)

        return {
            "original_image": rgb_image,
            "enhanced_image": enhanced_image,
            "hsv_image": hsv_image,
            "lab_image": lab_image,
            "tissue_segmentation": tissue_segmentation,
            "edges": edges,
            "texture_analysis": texture_analysis,
            "abnormalities": abnormalities,
            "measurements": measurements,
            "tissue_health": tissue_health,
            "specific_findings": specific_findings,
            "severity_scores": severity_scores,
            "endoscopy_type": endoscopy_type,
        }

    def enhance_endoscopy_image(self, rgb_image):
        """
        Enhance endoscopy image quality using multiple techniques.

        :param rgb_image: Input RGB image
        :return: Enhanced image
        """
        enhanced = rgb_image.copy().astype(np.float32)

        # CLAHE (Contrast Limited Adaptive Histogram Equalization) on each channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        for i in range(3):
            enhanced[:, :, i] = clahe.apply(enhanced[:, :, i].astype(np.uint8))

        # Gaussian blur for noise reduction
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0.5)

        # Sharpening filter
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) / 9
        enhanced = cv2.filter2D(enhanced, -1, kernel)

        # Color correction
        enhanced = self.correct_color_cast(enhanced)

        return np.clip(enhanced, 0, 255).astype(np.uint8)

    def correct_color_cast(self, image):
        """
        Correct color cast in endoscopy images.

        :param image: Input image
        :return: Color-corrected image
        """
        # Gray world assumption
        mean_r = np.mean(image[:, :, 0])
        mean_g = np.mean(image[:, :, 1])
        mean_b = np.mean(image[:, :, 2])

        gray_mean = (mean_r + mean_g + mean_b) / 3

        # Apply correction factors
        if mean_r > 0:
            image[:, :, 0] = image[:, :, 0] * (gray_mean / mean_r)
        if mean_g > 0:
            image[:, :, 1] = image[:, :, 1] * (gray_mean / mean_g)
        if mean_b > 0:
            image[:, :, 2] = image[:, :, 2] * (gray_mean / mean_b)

        return image

    def segment_endoscopy_tissues(self, hsv_image):
        """
        Segment different tissue types and conditions in endoscopy images.

        :param hsv_image: HSV color space image
        :param endoscopy_type: Type of endoscopy
        :return: Dictionary of tissue masks
        """
        segmentation = {}
        h, s, v = cv2.split(hsv_image)

        for condition, color_range in self.tissue_color_ranges.items():
            # Create mask for each condition
            h_mask = (h >= color_range["hue"][0]) & (h <= color_range["hue"][1])
            s_mask = (s >= color_range["saturation"][0]) & (
                s <= color_range["saturation"][1]
            )
            v_mask = (v >= color_range["value"][0]) & (v <= color_range["value"][1])

            mask = h_mask & s_mask & v_mask

            # Morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Remove small objects
            mask = morphology.remove_small_objects(mask.astype(bool), min_size=100)

            segmentation[condition] = mask

        # Additional segmentation using K-means clustering
        kmeans_segmentation = self.kmeans_tissue_segmentation(hsv_image)
        segmentation.update(kmeans_segmentation)

        return segmentation

    def kmeans_tissue_segmentation(self, hsv_image, n_clusters=5):
        """
        Perform tissue segmentation using K-means clustering.

        :param hsv_image: HSV image
        :param n_clusters: Number of clusters
        :return: Dictionary of cluster masks
        """
        # Reshape image for clustering
        pixel_data = hsv_image.reshape(-1, 3)

        # Apply K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pixel_data)

        # Reshape back to image dimensions
        segmented = labels.reshape(hsv_image.shape[:2])

        # Create masks for each cluster
        cluster_masks = {}
        for i in range(n_clusters):
            mask = segmented == i
            cluster_masks[f"cluster_{i}"] = mask

        return cluster_masks

    def detect_endoscopy_edges(self, image):
        """
        Detect edges in endoscopy images using multiple methods.

        :param image: Input image
        :return: Edge map
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Canny edge detection
        edges_canny = cv2.Canny(gray, 50, 150)

        # Sobel edge detection
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges_sobel = np.sqrt(sobelx**2 + sobely**2)
        edges_sobel = (edges_sobel / edges_sobel.max() * 255).astype(np.uint8)

        # Combine edge maps
        combined_edges = cv2.bitwise_or(edges_canny, edges_sobel)

        return combined_edges

    def analyze_texture_patterns(self, image):
        """
        Analyze texture patterns in endoscopy images.

        :param image: Input image
        :return: Texture analysis results
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        texture_features = {}

        # Local Binary Pattern (LBP)
        lbp = feature.local_binary_pattern(gray, P=8, R=1, method="uniform")
        texture_features["lbp_histogram"] = np.histogram(lbp, bins=10)[0]

        # Gray Level Co-occurrence Matrix (GLCM) features
        distances = [1, 2, 3]
        angles = [0, 45, 90, 135]

        glcm_features = {
            "contrast": [],
            "dissimilarity": [],
            "homogeneity": [],
            "energy": [],
        }

        for distance in distances:
            for angle in angles:
                try:
                    glcm = feature.graycomatrix(
                        gray,
                        distances=[distance],
                        angles=[np.radians(angle)],
                        levels=256,
                        symmetric=True,
                        normed=True,
                    )

                    glcm_features["contrast"].append(
                        feature.graycoprops(glcm, "contrast")[0, 0]
                    )
                    glcm_features["dissimilarity"].append(
                        feature.graycoprops(glcm, "dissimilarity")[0, 0]
                    )
                    glcm_features["homogeneity"].append(
                        feature.graycoprops(glcm, "homogeneity")[0, 0]
                    )
                    glcm_features["energy"].append(
                        feature.graycoprops(glcm, "energy")[0, 0]
                    )
                except:
                    # Handle potential errors with GLCM calculation
                    glcm_features["contrast"].append(0)
                    glcm_features["dissimilarity"].append(0)
                    glcm_features["homogeneity"].append(0)
                    glcm_features["energy"].append(0)

        # Calculate mean values
        for key in glcm_features:
            texture_features[f"glcm_{key}_mean"] = np.mean(glcm_features[key])
            texture_features[f"glcm_{key}_std"] = np.std(glcm_features[key])

        # Fractal dimension
        texture_features["fractal_dimension"] = self.calculate_fractal_dimension(gray)

        return texture_features

    def calculate_fractal_dimension(self, image):
        """
        Calculate fractal dimension of an image texture.

        :param image: Grayscale image
        :return: Fractal dimension
        """

        def boxcount(Z, k):
            S = np.add.reduceat(
                np.add.reduceat(Z, np.arange(0, Z.shape[0], k), axis=0),
                np.arange(0, Z.shape[1], k),
                axis=1,
            )
            return len(np.where((S > 0) & (S < k * k))[0])

        # Convert to binary
        Z = image < np.mean(image)

        # Calculate box-counting dimension
        p = min(Z.shape)
        n = 2 ** np.floor(np.log(p) / np.log(2))
        n = int(np.log(n) / np.log(2))
        sizes = 2 ** np.arange(n, 1, -1)
        counts = []

        for size in sizes:
            try:
                counts.append(boxcount(Z, size))
            except:
                counts.append(0)

        # Fit the slope
        if len(counts) > 1 and np.any(counts):
            coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
            return -coeffs[0]
        else:
            return 1.0  # Default value

    def detect_abnormalities(self, rgb_image, hsv_image):
        """
        Detect abnormalities using machine learning and image analysis.

        :param rgb_image: RGB image
        :param hsv_image: HSV image
        :param tissue_segmentation: Tissue segmentation results
        :param texture_analysis: Texture analysis results
        :return: List of detected abnormalities
        """
        abnormalities = []
        h, w = rgb_image.shape[:2]

        # Create feature vectors for anomaly detection
        patch_size = 32
        features = []
        coordinates = []

        for y in range(0, h - patch_size, patch_size // 2):
            for x in range(0, w - patch_size, patch_size // 2):
                patch_rgb = rgb_image[y : y + patch_size, x : x + patch_size]
                patch_hsv = hsv_image[y : y + patch_size, x : x + patch_size]

                # Extract features
                feature_vector = []

                # Color statistics
                for channel in range(3):
                    feature_vector.extend(
                        [
                            np.mean(patch_rgb[:, :, channel]),
                            np.std(patch_rgb[:, :, channel]),
                            np.mean(patch_hsv[:, :, channel]),
                            np.std(patch_hsv[:, :, channel]),
                        ]
                    )

                # Texture features
                gray_patch = cv2.cvtColor(patch_rgb, cv2.COLOR_RGB2GRAY)

                # Edge density
                edges = cv2.Canny(gray_patch, 50, 150)
                feature_vector.append(np.sum(edges) / (patch_size * patch_size))

                # Local binary pattern
                try:
                    lbp = feature.local_binary_pattern(
                        gray_patch, P=8, R=1, method="uniform"
                    )
                    feature_vector.append(np.std(lbp))
                except:
                    feature_vector.append(0)

                features.append(feature_vector)
                coordinates.append((x + patch_size // 2, y + patch_size // 2))

        if len(features) > 0:
            features = np.array(features)

            # Normalize features
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features)

            # Apply Isolation Forest
            clf = IsolationForest(contamination=0.05, random_state=42)
            anomaly_labels = clf.fit_predict(features_normalized)
            anomaly_scores = -clf.score_samples(features_normalized)

            # Extract anomalies
            anomaly_indices = np.where(anomaly_labels == -1)[0]

            for idx in anomaly_indices:
                x, y = coordinates[idx]
                score = anomaly_scores[idx]

                # Classify type of abnormality based on color and texture
                patch_rgb = rgb_image[max(0, y - 16) : y + 16, max(0, x - 16) : x + 16]
                patch_hsv = hsv_image[max(0, y - 16) : y + 16, max(0, x - 16) : x + 16]

                abnormality_type = self.classify_abnormality_type(patch_rgb, patch_hsv)

                abnormalities.append(
                    {
                        "location": (x, y),
                        "score": score,
                        "type": abnormality_type,
                        "size": patch_size,
                    }
                )

        return abnormalities

    def classify_abnormality_type(self, patch_rgb, patch_hsv):
        """
        Classify the type of abnormality based on color and texture features.

        :param patch_rgb: RGB patch
        :param patch_hsv: HSV patch
        :return: Abnormality type
        """
        if patch_rgb.size == 0 or patch_hsv.size == 0:
            return "unknown"

        # Analyze color characteristics
        mean_hue = np.mean(patch_hsv[:, :, 0])
        mean_sat = np.mean(patch_hsv[:, :, 1])
        mean_val = np.mean(patch_hsv[:, :, 2])

        # Red regions (potential bleeding or inflammation)
        if mean_hue < 15 and mean_sat > 100:
            return "bleeding_or_inflammation"

        # White/pale regions (potential ulceration)
        elif mean_val > 180 and mean_sat < 50:
            return "ulceration_or_scar"

        # Dark regions (potential neoplasia)
        elif mean_val < 80:
            return "neoplastic_lesion"

        # Irregular texture (potential dysplasia)
        else:
            return "texture_abnormality"

    def measure_endoscopy_features(self, tissue_segmentation, rgb_image):
        """
        Measure various features in endoscopy images.

        :param tissue_segmentation: Tissue segmentation results
        :param rgb_image: Original RGB image
        :return: Measurement results
        """
        measurements = {}

        for tissue_type, mask in tissue_segmentation.items():
            if np.any(mask):
                # Label connected components
                labeled_mask = measure.label(mask)
                regions = measure.regionprops(labeled_mask)

                region_data = []
                for region in regions:
                    if region.area > 50:  # Minimum size filter
                        region_info = {
                            "area": region.area,
                            "perimeter": region.perimeter,
                            "centroid": region.centroid,
                            "eccentricity": region.eccentricity,
                            "solidity": region.solidity,
                            "extent": region.extent,
                            "major_axis_length": region.major_axis_length,
                            "minor_axis_length": region.minor_axis_length,
                        }

                        # Calculate mean color in region
                        mask_region = labeled_mask == region.label
                        region_colors = rgb_image[mask_region]
                        region_info["mean_color"] = np.mean(region_colors, axis=0)

                        region_data.append(region_info)

                measurements[tissue_type] = {
                    "total_area": np.sum(mask),
                    "region_count": len(region_data),
                    "regions": region_data,
                }
            else:
                measurements[tissue_type] = {
                    "total_area": 0,
                    "region_count": 0,
                    "regions": [],
                }

        return measurements

    def classify_tissue_health(self, rgb_image, tissue_segmentation, texture_analysis):
        """
        Classify the health status of different tissues.

        :param rgb_image: RGB image
        :param hsv_image: HSV image
        :param tissue_segmentation: Tissue segmentation results
        :param texture_analysis: Texture analysis results
        :return: Tissue health classification
        """
        health_classification = {}

        # Overall image health score
        overall_score = 100.0

        # Penalize for inflammatory regions
        if np.any(tissue_segmentation.get("inflamed", False)):
            inflamed_area = np.sum(tissue_segmentation["inflamed"])
            total_area = rgb_image.shape[0] * rgb_image.shape[1]
            inflammatory_ratio = inflamed_area / total_area
            overall_score -= inflammatory_ratio * 30

        # Penalize for ulcerated regions
        if np.any(tissue_segmentation.get("ulcerated", False)):
            ulcer_area = np.sum(tissue_segmentation["ulcerated"])
            total_area = rgb_image.shape[0] * rgb_image.shape[1]
            ulcer_ratio = ulcer_area / total_area
            overall_score -= ulcer_ratio * 40

        # Penalize for bleeding
        if np.any(tissue_segmentation.get("bleeding", False)):
            bleeding_area = np.sum(tissue_segmentation["bleeding"])
            total_area = rgb_image.shape[0] * rgb_image.shape[1]
            bleeding_ratio = bleeding_area / total_area
            overall_score -= bleeding_ratio * 50

        # Texture irregularity penalty
        if texture_analysis.get("fractal_dimension", 1.0) > 1.8:
            overall_score -= 15

        health_classification["overall_health_score"] = max(0, overall_score)

        # Individual tissue health
        for tissue_type, mask in tissue_segmentation.items():
            if np.any(mask):
                tissue_score = 100.0

                # Color-based health assessment
                tissue_region = rgb_image[mask]
                color_std = np.std(tissue_region, axis=0)

                # High color variation suggests pathology
                if np.mean(color_std) > 30:
                    tissue_score -= 20

                # Specific conditions
                if "inflamed" in tissue_type:
                    tissue_score -= 25
                elif "ulcerated" in tissue_type:
                    tissue_score -= 35
                elif "bleeding" in tissue_type:
                    tissue_score -= 45
                elif "polyp" in tissue_type:
                    tissue_score -= 15

                health_classification[tissue_type] = max(0, tissue_score)

        return health_classification

    def detect_specific_conditions(self, tissue_segmentation, endoscopy_type):
        """
        Detect specific conditions based on endoscopy type.

        :param rgb_image: RGB image
        :param hsv_image: HSV image
        :param tissue_segmentation: Tissue segmentation
        :param endoscopy_type: Type of endoscopy
        :return: Specific findings
        """
        findings = {}

        if endoscopy_type == "gastric":
            findings.update(self.detect_gastric_conditions(tissue_segmentation))
        elif endoscopy_type == "colonoscopy":
            findings.update(self.detect_colon_conditions(tissue_segmentation))
        elif endoscopy_type == "esophageal":
            findings.update(self.detect_esophageal_conditions(tissue_segmentation))

        return findings

    def detect_gastric_conditions(self, tissue_segmentation):
        """Detect gastric-specific conditions."""
        findings = {}

        # H. pylori gastritis (reddish, nodular appearance)
        if np.any(tissue_segmentation.get("inflamed", False)):
            findings["h_pylori_gastritis"] = {
                "detected": True,
                "severity": (
                    "moderate"
                    if np.sum(tissue_segmentation["inflamed"]) > 1000
                    else "mild"
                ),
            }

        # Peptic ulcers
        if np.any(tissue_segmentation.get("ulcerated", False)):
            findings["peptic_ulcer"] = {
                "detected": True,
                "count": len(
                    measure.regionprops(measure.label(tissue_segmentation["ulcerated"]))
                ),
            }

        # Gastric polyps
        if np.any(tissue_segmentation.get("polyp", False)):
            findings["gastric_polyps"] = {
                "detected": True,
                "count": len(
                    measure.regionprops(measure.label(tissue_segmentation["polyp"]))
                ),
            }

        return findings

    def detect_colon_conditions(self, tissue_segmentation):
        """Detect colon-specific conditions."""
        findings = {}

        # Inflammatory bowel disease
        if np.any(tissue_segmentation.get("inflamed", False)):
            findings["inflammatory_bowel_disease"] = {
                "detected": True,
                "type": (
                    "ulcerative_colitis"
                    if np.any(tissue_segmentation.get("ulcerated", False))
                    else "crohns_disease"
                ),
            }

        # Colon polyps
        if np.any(tissue_segmentation.get("polyp", False)):
            polyp_regions = measure.regionprops(
                measure.label(tissue_segmentation["polyp"])
            )
            findings["colon_polyps"] = {
                "detected": True,
                "count": len(polyp_regions),
                "largest_size": (
                    max([region.area for region in polyp_regions])
                    if polyp_regions
                    else 0
                ),
            }

        # Diverticulosis (look for pocket-like structures)
        findings["diverticulosis"] = {"detected": False}

        return findings

    def detect_esophageal_conditions(self, tissue_segmentation):
        """Detect esophageal-specific conditions."""
        findings = {}

        # Barrett's esophagus
        if np.any(tissue_segmentation.get("barrett", False)):
            findings["barretts_esophagus"] = {
                "detected": True,
                "extent": np.sum(tissue_segmentation["barrett"]),
            }

        # Esophagitis
        if np.any(tissue_segmentation.get("inflamed", False)):
            findings["esophagitis"] = {
                "detected": True,
                "severity": (
                    "severe"
                    if np.sum(tissue_segmentation["inflamed"]) > 2000
                    else "mild"
                ),
            }

        # Esophageal varices (dilated vessels)
        findings["esophageal_varices"] = {"detected": False}  # Simplified

        return findings

    def calculate_severity_scores(self, abnormalities, tissue_health):
        """
        Calculate severity scores for different conditions.

        :param abnormalities: Detected abnormalities
        :param tissue_health: Tissue health classification
        :return: Severity scores
        """
        scores = {
            "inflammation_score": 0,
            "ulceration_score": 0,
            "bleeding_score": 0,
            "overall_severity": 0,
        }

        # Count abnormalities by type
        abnormality_counts = {}
        for abnormality in abnormalities:
            ab_type = abnormality["type"]
            abnormality_counts[ab_type] = abnormality_counts.get(ab_type, 0) + 1

        # Calculate scores
        scores["inflammation_score"] = min(
            100, abnormality_counts.get("bleeding_or_inflammation", 0) * 10
        )
        scores["ulceration_score"] = min(
            100, abnormality_counts.get("ulceration_or_scar", 0) * 15
        )
        scores["bleeding_score"] = min(
            100, abnormality_counts.get("bleeding_or_inflammation", 0) * 20
        )

        # Overall severity
        overall_health = tissue_health.get("overall_health_score", 100)
        scores["overall_severity"] = 100 - overall_health

        return scores
