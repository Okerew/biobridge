import random
import warnings

import cv2
import numpy as np
from scipy import ndimage
from skimage import feature, filters, measure, morphology
from sklearn.cluster import KMeans

from biobridge.blocks.cell import Cell
from biobridge.definitions.tissues.breast import BreastTissue

warnings.filterwarnings("ignore")


class MammographyAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer
        # BI-RADS density categories
        self.density_categories = {
            "A": "Almost entirely fatty",
            "B": "Scattered areas of fibroglandular density",
            "C": "Heterogeneously dense",
            "D": "Extremely dense",
        }

    def analyze_mammogram(self, image, view="CC", laterality="L"):
        """
        Comprehensive mammography analysis including density, masses, calcifications.

        :param image: Input mammographic image (ImageJ DataArray)
        :param view: Mammographic view ('CC', 'MLO', 'ML', 'LM')
        :param laterality: Breast laterality ('L' for left, 'R' for right)
        :return: Dictionary containing comprehensive analysis results
        """
        # Convert ImageJ image to numpy array
        img_array = self.image_analyzer.ij.py.from_java(image)

        # Ensure grayscale
        if len(img_array.shape) > 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Preprocessing
        preprocessed = self.preprocess_mammogram(img_array)

        # Segment breast region
        breast_mask = self.segment_breast_region(preprocessed)

        # Enhance image for feature detection
        enhanced = self.enhance_mammogram(preprocessed, breast_mask)

        # Breast density analysis (BI-RADS)
        density_analysis = self.analyze_breast_density(enhanced, breast_mask)

        # Mass detection
        masses = self.detect_masses(enhanced, breast_mask)

        # Calcification detection
        calcifications = self.detect_calcifications(enhanced, breast_mask)

        # Architectural distortion detection
        distortions = self.detect_architectural_distortion(enhanced, breast_mask)

        # Asymmetry detection (if bilateral images available)
        asymmetries = self.detect_asymmetries(enhanced, breast_mask)

        # Skin thickening analysis
        skin_analysis = self.analyze_skin_thickening(enhanced, breast_mask)

        # Overall risk assessment
        risk_assessment = self.calculate_cancer_risk(
            masses, calcifications, distortions, asymmetries
        )

        return {
            "original_image": img_array,
            "preprocessed_image": preprocessed,
            "breast_mask": breast_mask,
            "enhanced_image": enhanced,
            "view": view,
            "laterality": laterality,
            "density_analysis": density_analysis,
            "masses": masses,
            "calcifications": calcifications,
            "architectural_distortions": distortions,
            "asymmetries": asymmetries,
            "skin_analysis": skin_analysis,
            "cancer_risk_assessment": risk_assessment,
        }

    def preprocess_mammogram(self, image):
        """
        Preprocess mammographic image for optimal analysis.

        :param image: Input mammographic image
        :return: Preprocessed image
        """
        # Convert to float for processing
        img = image.astype(np.float32)

        # Normalize intensity
        img = (img - np.min(img)) / (np.max(img) - np.min(img))

        # Apply artifact removal (paddle edge, labels)
        # Remove very bright regions (labels, markers)
        mask_artifacts = img < 0.95
        img = img * mask_artifacts

        # Gentle noise reduction while preserving microcalcifications
        img = cv2.bilateralFilter((img * 255).astype(np.uint8), 5, 50, 50) / 255.0

        return img

    def segment_breast_region(self, image):
        """
        Segment the breast region from background and artifacts.

        :param image: Preprocessed mammographic image
        :return: Binary mask of breast region
        """
        # Otsu thresholding for initial segmentation
        _, binary = cv2.threshold(
            (image * 255).astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Remove small artifacts and fill holes
        binary = binary.astype(bool)
        binary = morphology.remove_small_objects(binary, min_size=1000)
        binary = morphology.remove_small_holes(binary, area_threshold=500)

        # Find largest connected component (breast)
        labeled = measure.label(binary)
        if isinstance(labeled, tuple):
            labeled = labeled[0]
        if np.max(labeled) > 0:
            largest_region = np.argmax(np.bincount(labeled.flat)[1:]) + 1
            breast_mask = labeled == largest_region
        else:
            breast_mask = binary

        # Morphological operations to smooth breast boundary
        kernel = morphology.disk(5)
        breast_mask = morphology.binary_closing(breast_mask, kernel)
        breast_mask = morphology.binary_opening(breast_mask, morphology.disk(3))

        return breast_mask

    def enhance_mammogram(self, image, breast_mask):
        """
        Enhance mammographic image for better feature visibility.

        :param image: Preprocessed image
        :param breast_mask: Breast region mask
        :return: Enhanced image
        """
        enhanced = image.copy()

        # Apply CLAHE only within breast region
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        breast_region = (enhanced * breast_mask * 255).astype(np.uint8)
        enhanced_region = clahe.apply(breast_region) / 255.0

        # Combine enhanced region with original background
        enhanced = enhanced * (~breast_mask) + enhanced_region * breast_mask

        # Unsharp masking for better edge definition
        gaussian_blur = cv2.GaussianBlur(enhanced, (5, 5), 1.0)
        enhanced = enhanced + 0.3 * (enhanced - gaussian_blur)
        enhanced = np.clip(enhanced, 0, 1)

        return enhanced

    def analyze_breast_density(self, image, breast_mask):
        """
        Analyze breast density according to BI-RADS categories.

        :param image: Enhanced mammographic image
        :param breast_mask: Breast region mask
        :return: Density analysis results
        """
        breast_pixels = image[breast_mask]

        # Calculate density metrics
        mean_density = np.mean(breast_pixels)
        density_std = np.std(breast_pixels)

        # Segment dense tissue using adaptive thresholding
        dense_threshold = np.percentile(breast_pixels, 75)
        dense_tissue_mask = (image > dense_threshold) & breast_mask

        # Calculate percentage of dense tissue
        breast_area = np.sum(breast_mask)
        dense_area = np.sum(dense_tissue_mask)
        density_percentage = (dense_area / breast_area) * 100 if breast_area > 0 else 0

        # Determine BI-RADS category
        if density_percentage < 10:
            birads_category = "A"
        elif density_percentage < 25:
            birads_category = "B"
        elif density_percentage < 50:
            birads_category = "C"
        else:
            birads_category = "D"

        return {
            "density_percentage": density_percentage,
            "birads_category": birads_category,
            "category_description": self.density_categories[birads_category],
            "mean_density": mean_density,
            "density_std": density_std,
            "dense_tissue_mask": dense_tissue_mask,
        }

    def detect_masses(self, image, breast_mask):
        """
        Detect potential masses in mammographic image.

        :param image: Enhanced image
        :param breast_mask: Breast region mask
        :return: List of detected masses
        """
        masses = []

        # Apply Gaussian filtering for mass detection
        smoothed = cv2.GaussianBlur(image, (7, 7), 2.0)

        # Detect local maxima (potential mass centers)
        local_maxima = feature.peak_local_max(
            smoothed * breast_mask,
            min_distance=20,
            threshold_abs=0.1,
            threshold_rel=0.3,
        )

        for coord in zip(local_maxima[0], local_maxima[1]):
            y, x = coord

            # Extract region around potential mass
            region_size = 40
            y_min = max(0, y - region_size // 2)
            y_max = min(image.shape[0], y + region_size // 2)
            x_min = max(0, x - region_size // 2)
            x_max = min(image.shape[1], x + region_size // 2)

            roi = image[y_min:y_max, x_min:x_max]
            roi_mask = breast_mask[y_min:y_max, x_min:x_max]

            if np.sum(roi_mask) < 100:  # Skip if too small
                continue

            # Analyze region characteristics
            center_intensity = image[y, x]
            surrounding_mean = np.mean(roi[roi_mask])
            contrast = center_intensity - surrounding_mean

            # Check for mass-like characteristics
            if contrast > 0.1:  # Sufficient contrast
                # Measure circularity and size
                _, binary_roi = cv2.threshold(
                    (roi * 255).astype(np.uint8),
                    0,
                    255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU,
                )

                contours, _ = cv2.findContours(
                    binary_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 50:  # Minimum area threshold
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)

                            # Mass characteristics
                            mass_info = {
                                "center": (x, y),
                                "area": area,
                                "circularity": circularity,
                                "contrast": contrast,
                                "intensity": center_intensity,
                                "suspicion_level": self.assess_mass_suspicion(
                                    circularity, contrast, area
                                ),
                            }
                            masses.append(mass_info)

        # Remove duplicate detections
        masses = self.remove_duplicate_masses(masses)

        return masses

    def detect_calcifications(self, image, breast_mask):
        """
        Detect microcalcifications and macrocalcifications.

        :param image: Enhanced image
        :param breast_mask: Breast region mask
        :return: List of detected calcifications
        """
        calcifications = []

        # High-pass filtering to enhance small bright spots
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        high_pass = cv2.filter2D(image, -1, kernel)
        high_pass = np.clip(high_pass, 0, 1)

        # Apply breast mask
        high_pass = high_pass * breast_mask

        # Threshold for calcification detection
        calc_threshold = np.percentile(high_pass[breast_mask], 98)
        calc_candidates = high_pass > calc_threshold

        # Remove noise and artifacts
        calc_candidates = morphology.remove_small_objects(calc_candidates, min_size=3)

        # Label connected components
        labeled_calcs = measure.label(calc_candidates)

        for region in measure.regionprops(labeled_calcs):
            if region.area >= 2:  # Minimum size for calcification
                centroid = region.centroid
                area = region.area
                intensity = np.mean(high_pass[labeled_calcs == region.label])

                # Classify calcification type
                if area <= 5:
                    calc_type = "microcalcification"
                    suspicion = "moderate" if intensity > 0.8 else "low"
                else:
                    calc_type = "macrocalcification"
                    suspicion = "low"

                calc_info = {
                    "center": (int(centroid[1]), int(centroid[0])),
                    "area": area,
                    "type": calc_type,
                    "intensity": intensity,
                    "suspicion_level": suspicion,
                }
                calcifications.append(calc_info)

        # Analyze clustering patterns
        if len(calcifications) > 5:
            calcifications = self.analyze_calcification_clustering(calcifications)

        return calcifications

    def detect_architectural_distortion(self, image, breast_mask):
        """
        Detect architectural distortion patterns.

        :param image: Enhanced image
        :param breast_mask: Breast region mask
        :return: List of detected distortions
        """
        distortions = []

        # Apply Gabor filters at multiple orientations
        orientations = [0, 30, 60, 90, 120, 150]
        gabor_responses = []

        for angle in orientations:
            real, _ = filters.gabor(image, frequency=0.1, theta=np.radians(angle))
            gabor_responses.append(real * breast_mask)

        # Analyze local orientation coherence
        window_size = 32
        step_size = 16

        for y in range(0, image.shape[0] - window_size, step_size):
            for x in range(0, image.shape[1] - window_size, step_size):
                window_mask = breast_mask[y : y + window_size, x : x + window_size]

                if np.sum(window_mask) < window_size * window_size * 0.5:
                    continue

                # Calculate orientation energy
                orientation_energy = []
                for gabor_resp in gabor_responses:
                    window_resp = gabor_resp[y : y + window_size, x : x + window_size]
                    energy = np.sum(window_resp[window_mask] ** 2)
                    orientation_energy.append(energy)

                # Check for dominant orientation (potential distortion)
                max_energy = max(orientation_energy)
                total_energy = sum(orientation_energy)

                if total_energy > 0:
                    coherence = max_energy / total_energy

                    if coherence > 0.6:  # Strong directional component
                        dominant_orientation = orientations[
                            np.argmax(orientation_energy)
                        ]

                        distortion_info = {
                            "center": (x + window_size // 2, y + window_size // 2),
                            "dominant_orientation": dominant_orientation,
                            "coherence": coherence,
                            "suspicion_level": (
                                "high" if coherence > 0.8 else "moderate"
                            ),
                        }
                        distortions.append(distortion_info)

        # Remove overlapping detections
        distortions = self.remove_overlapping_distortions(distortions)

        return distortions

    def detect_asymmetries(self, image, breast_mask):
        """
        Detect focal asymmetries and developing asymmetries.

        :param image: Enhanced image
        :param breast_mask: Breast region mask
        :return: List of detected asymmetries
        """
        asymmetries = []

        # This is a simplified version - in practice, you'd compare with contralateral breast
        # Here we look for local density variations

        # Apply median filtering
        median_filtered = ndimage.median_filter(image * breast_mask, size=21)

        # Calculate local contrast
        contrast_map = np.abs(image - median_filtered)
        contrast_map = contrast_map * breast_mask

        # Find regions of high local contrast
        high_contrast_threshold = np.percentile(contrast_map[breast_mask], 95)
        asymmetry_candidates = contrast_map > high_contrast_threshold

        # Remove small artifacts
        asymmetry_candidates = morphology.remove_small_objects(
            asymmetry_candidates, min_size=100
        )

        # Label and analyze regions
        labeled_asymmetries = measure.label(asymmetry_candidates)

        for region in measure.regionprops(labeled_asymmetries):
            if region.area > 200:  # Minimum size for significant asymmetry
                centroid = region.centroid
                area = region.area

                # Calculate asymmetry strength
                region_mask = labeled_asymmetries == region.label
                asymmetry_strength = np.mean(contrast_map[region_mask])

                asymmetry_info = {
                    "center": (int(centroid[1]), int(centroid[0])),
                    "area": area,
                    "strength": asymmetry_strength,
                    "suspicion_level": (
                        "high" if asymmetry_strength > 0.3 else "moderate"
                    ),
                }
                asymmetries.append(asymmetry_info)

        return asymmetries

    def analyze_skin_thickening(self, image, breast_mask):
        """
        Analyze skin thickening which can indicate inflammatory conditions.

        :param image: Enhanced image
        :param breast_mask: Breast region mask
        :return: Skin analysis results
        """
        # Find breast boundary
        boundary = morphology.binary_erosion(breast_mask) ^ breast_mask

        # Dilate to get skin region
        skin_region = (
            morphology.binary_dilation(boundary, morphology.disk(10)) & breast_mask
        )

        if np.sum(skin_region) == 0:
            return {"skin_thickness_normal": True, "mean_skin_intensity": 0}

        # Analyze skin intensity
        skin_intensities = image[skin_region]
        mean_skin_intensity = np.mean(skin_intensities)
        skin_std = np.std(skin_intensities)

        # Normal skin should be relatively uniform and moderately intense
        skin_thickness_normal = mean_skin_intensity < 0.7 and skin_std < 0.2

        return {
            "skin_thickness_normal": skin_thickness_normal,
            "mean_skin_intensity": mean_skin_intensity,
            "skin_std": skin_std,
            "skin_region_mask": skin_region,
        }

    def assess_mass_suspicion(self, circularity, contrast, area):
        """
        Assess suspicion level of detected mass.

        :param circularity: Mass circularity measure
        :param contrast: Mass contrast with surroundings
        :param area: Mass area
        :return: Suspicion level string
        """
        suspicion_score = 0

        # Irregular shape is more suspicious
        if circularity < 0.6:
            suspicion_score += 2
        elif circularity < 0.8:
            suspicion_score += 1

        # High contrast is more suspicious
        if contrast > 0.3:
            suspicion_score += 2
        elif contrast > 0.15:
            suspicion_score += 1

        # Size considerations
        if area > 500:
            suspicion_score += 1

        if suspicion_score >= 4:
            return "high"
        elif suspicion_score >= 2:
            return "moderate"
        else:
            return "low"

    def analyze_calcification_clustering(self, calcifications):
        """
        Analyze clustering patterns of calcifications.

        :param calcifications: List of detected calcifications
        :return: Updated calcifications with clustering analysis
        """
        if len(calcifications) < 5:
            return calcifications

        # Extract positions
        positions = np.array([calc["center"] for calc in calcifications])

        # Use K-means to find clusters
        n_clusters = min(3, len(calcifications) // 3)
        if n_clusters > 1:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(positions)

            # Analyze each cluster
            for i, calc in enumerate(calcifications):
                cluster_id = cluster_labels[i]
                cluster_positions = positions[cluster_labels == cluster_id]

                if len(cluster_positions) >= 5:  # Significant cluster
                    # Calculate cluster tightness
                    cluster_center = np.mean(cluster_positions, axis=0)
                    distances = np.linalg.norm(
                        cluster_positions - cluster_center, axis=1
                    )
                    avg_distance = np.mean(distances)

                    # Tight clusters are more suspicious
                    if avg_distance < 30:
                        calc["cluster_suspicion"] = "high"
                    elif avg_distance < 50:
                        calc["cluster_suspicion"] = "moderate"
                    else:
                        calc["cluster_suspicion"] = "low"
                else:
                    calc["cluster_suspicion"] = "isolated"

        return calcifications

    def remove_duplicate_masses(self, masses, distance_threshold=30):
        """
        Remove duplicate mass detections.

        :param masses: List of detected masses
        :param distance_threshold: Minimum distance between masses
        :return: Filtered list of masses
        """
        if len(masses) <= 1:
            return masses

        filtered_masses = []
        for i, mass1 in enumerate(masses):
            is_duplicate = False
            for j, mass2 in enumerate(filtered_masses):
                distance = np.sqrt(
                    (mass1["center"][0] - mass2["center"][0]) ** 2
                    + (mass1["center"][1] - mass2["center"][1]) ** 2
                )
                if distance < distance_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered_masses.append(mass1)

        return filtered_masses

    def remove_overlapping_distortions(self, distortions, distance_threshold=50):
        """
        Remove overlapping architectural distortion detections.
        """
        if len(distortions) <= 1:
            return distortions

        filtered_distortions = []
        for distortion in distortions:
            is_overlapping = False
            for existing in filtered_distortions:
                distance = np.sqrt(
                    (distortion["center"][0] - existing["center"][0]) ** 2
                    + (distortion["center"][1] - existing["center"][1]) ** 2
                )
                if distance < distance_threshold:
                    is_overlapping = True
                    break

            if not is_overlapping:
                filtered_distortions.append(distortion)

        return filtered_distortions

    def calculate_cancer_risk(self, masses, calcifications, distortions, asymmetries):
        """
        Calculate overall cancer risk assessment.

        :param masses: Detected masses
        :param calcifications: Detected calcifications
        :param distortions: Detected architectural distortions
        :param asymmetries: Detected asymmetries
        :return: Risk assessment dictionary
        """
        risk_factors = []
        risk_score = 0

        # Assess masses
        high_suspicion_masses = sum(1 for m in masses if m["suspicion_level"] == "high")
        moderate_suspicion_masses = sum(
            1 for m in masses if m["suspicion_level"] == "moderate"
        )

        if high_suspicion_masses > 0:
            risk_score += high_suspicion_masses * 3
            risk_factors.append(f"{high_suspicion_masses} high-suspicion mass(es)")

        if moderate_suspicion_masses > 0:
            risk_score += moderate_suspicion_masses * 1
            risk_factors.append(
                f"{moderate_suspicion_masses} moderate-suspicion mass(es)"
            )

        # Assess calcifications
        high_suspicion_calcs = sum(
            1
            for c in calcifications
            if c.get("cluster_suspicion") == "high" or c["suspicion_level"] == "high"
        )

        if high_suspicion_calcs >= 5:
            risk_score += 3
            risk_factors.append("Suspicious calcification cluster")
        elif high_suspicion_calcs > 0:
            risk_score += 1
            risk_factors.append("Scattered suspicious calcifications")

        # Assess architectural distortions
        high_suspicion_distortions = sum(
            1 for d in distortions if d["suspicion_level"] == "high"
        )

        if high_suspicion_distortions > 0:
            risk_score += high_suspicion_distortions * 2
            risk_factors.append(
                f"{high_suspicion_distortions} architectural distortion(s)"
            )

        # Assess asymmetries
        high_suspicion_asymmetries = sum(
            1 for a in asymmetries if a["suspicion_level"] == "high"
        )

        if high_suspicion_asymmetries > 0:
            risk_score += high_suspicion_asymmetries * 1
            risk_factors.append(
                f"{high_suspicion_asymmetries} significant asymmetr(y/ies)"
            )

        # Determine overall risk level
        if risk_score == 0:
            risk_level = "low"
            recommendation = "Routine screening"
        elif risk_score <= 2:
            risk_level = "low-moderate"
            recommendation = "Consider additional imaging or short-term follow-up"
        elif risk_score <= 5:
            risk_level = "moderate"
            recommendation = "Additional imaging recommended"
        else:
            risk_level = "high"
            recommendation = "Tissue sampling may be indicated"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
        }

    def visualize_mammography_analysis(self, analysis_results):
        """
        Visualize mammography analysis results.

        :param analysis_results: Results from analyze_mammogram method
        """
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle

        fig, axs = plt.subplots(2, 3, figsize=(18, 12))

        # Original mammogram
        axs[0, 0].imshow(analysis_results["original_image"], cmap="gray")
        axs[0, 0].set_title(
            f"Original Mammogram\n{analysis_results['view']} {analysis_results['laterality']}"
        )

        # Enhanced mammogram with breast mask
        enhanced_with_mask = analysis_results["enhanced_image"].copy()
        enhanced_with_mask[~analysis_results["breast_mask"]] = 0
        axs[0, 1].imshow(enhanced_with_mask, cmap="gray")
        axs[0, 1].set_title("Enhanced Image with Breast Segmentation")

        # Density analysis
        density_overlay = analysis_results["enhanced_image"].copy()
        if "dense_tissue_mask" in analysis_results["density_analysis"]:
            density_overlay[
                analysis_results["density_analysis"]["dense_tissue_mask"]
            ] = 1.0
        axs[0, 2].imshow(density_overlay, cmap="hot")
        density_info = analysis_results["density_analysis"]
        axs[0, 2].set_title(
            f"Breast Density Analysis\nBI-RADS {density_info['birads_category']} ({density_info['density_percentage']:.1f}%)"
        )

        # Findings overlay
        findings_overlay = analysis_results["enhanced_image"].copy()
        axs[1, 0].imshow(findings_overlay, cmap="gray")

        # Plot masses
        for mass in analysis_results["masses"]:
            center = mass["center"]
            color = (
                "red"
                if mass["suspicion_level"] == "high"
                else "yellow" if mass["suspicion_level"] == "moderate" else "green"
            )
            circle = Circle(center, radius=15, fill=False, color=color, linewidth=2)
            axs[1, 0].add_patch(circle)

        # Plot calcifications
        for calc in analysis_results["calcifications"]:
            center = calc["center"]
            color = "blue" if calc["suspicion_level"] == "high" else "cyan"
            axs[1, 0].plot(
                center[0], center[1], "x", color=color, markersize=8, markeredgewidth=2
            )

        # Plot architectural distortions
        for distortion in analysis_results["architectural_distortions"]:
            center = distortion["center"]
            axs[1, 0].plot(
                center[0],
                center[1],
                "+",
                color="magenta",
                markersize=12,
                markeredgewidth=3,
            )

        axs[1, 0].set_title(
            "Detected Findings\n(Red/Yellow/Green: Masses, Blue/Cyan: Calcifications, Magenta: Distortions)"
        )

        # Risk assessment
        risk_info = analysis_results["cancer_risk_assessment"]
        axs[1, 1].text(
            0.1,
            0.9,
            f"Risk Level: {risk_info['risk_level'].upper()}",
            fontsize=14,
            fontweight="bold",
            transform=axs[1, 1].transAxes,
        )
        axs[1, 1].text(
            0.1,
            0.8,
            f"Risk Score: {risk_info['risk_score']}",
            fontsize=12,
            transform=axs[1, 1].transAxes,
        )

        # List risk factors
        y_pos = 0.7
        for factor in risk_info["risk_factors"][:5]:  # Show up to 5 factors
            axs[1, 1].text(
                0.1, y_pos, f"• {factor}", fontsize=10, transform=axs[1, 1].transAxes
            )
            y_pos -= 0.1

        axs[1, 1].text(
            0.1,
            0.3,
            f"Recommendation:\n{risk_info['recommendation']}",
            fontsize=10,
            transform=axs[1, 1].transAxes,
            wrap=True,
        )
        axs[1, 1].set_xlim(0, 1)
        axs[1, 1].set_ylim(0, 1)
        axs[1, 1].set_title("Cancer Risk Assessment")
        axs[1, 1].axis("off")

        # Summary statistics
        stats_text = f"""FINDINGS SUMMARY:
        
Masses: {len(analysis_results['masses'])}
  - High suspicion: {sum(1 for m in analysis_results['masses'] if m['suspicion_level'] == 'high')}
  - Moderate suspicion: {sum(1 for m in analysis_results['masses'] if m['suspicion_level'] == 'moderate')}
  - Low suspicion: {sum(1 for m in analysis_results['masses'] if m['suspicion_level'] == 'low')}

Calcifications: {len(analysis_results['calcifications'])}
  - Microcalcifications: {sum(1 for c in analysis_results['calcifications'] if c['type'] == 'microcalcification')}
  - Macrocalcifications: {sum(1 for c in analysis_results['calcifications'] if c['type'] == 'macrocalcification')}

Architectural Distortions: {len(analysis_results['architectural_distortions'])}

Asymmetries: {len(analysis_results['asymmetries'])}

Skin Analysis: {'Normal' if analysis_results['skin_analysis']['skin_thickness_normal'] else 'Abnormal thickening detected'}
        """

        axs[1, 2].text(
            0.05,
            0.95,
            stats_text,
            fontsize=9,
            transform=axs[1, 2].transAxes,
            verticalalignment="top",
            fontfamily="monospace",
        )
        axs[1, 2].set_xlim(0, 1)
        axs[1, 2].set_ylim(0, 1)
        axs[1, 2].set_title("Analysis Summary")
        axs[1, 2].axis("off")

        # Remove axes for image plots
        for ax in axs.flat[:4]:
            ax.axis("off")

        plt.tight_layout()
        plt.show()

    def generate_birads_assessment(self, analysis_results):
        """
        Generate BI-RADS assessment based on analysis results.

        :param analysis_results: Results from analyze_mammogram method
        :return: BI-RADS assessment dictionary
        """
        masses = analysis_results["masses"]
        calcifications = analysis_results["calcifications"]
        distortions = analysis_results["architectural_distortions"]
        asymmetries = analysis_results["asymmetries"]

        # Determine BI-RADS category
        high_suspicion_findings = (
            sum(1 for m in masses if m["suspicion_level"] == "high")
            + sum(1 for c in calcifications if c.get("cluster_suspicion") == "high")
            + sum(1 for d in distortions if d["suspicion_level"] == "high")
        )

        moderate_suspicion_findings = (
            sum(1 for m in masses if m["suspicion_level"] == "moderate")
            + sum(1 for c in calcifications if c["suspicion_level"] == "moderate")
            + sum(1 for d in distortions if d["suspicion_level"] == "moderate")
            + sum(1 for a in asymmetries if a["suspicion_level"] == "high")
        )

        if high_suspicion_findings > 0:
            if high_suspicion_findings >= 2:
                birads_category = 5
                description = "Highly suggestive of malignancy"
                recommendation = "Tissue diagnosis"
            else:
                birads_category = 4
                description = "Suspicious abnormality"
                recommendation = "Tissue diagnosis"
        elif moderate_suspicion_findings > 0:
            birads_category = 3
            description = "Probably benign finding"
            recommendation = "Short-term follow-up"
        elif (
            len(masses) + len(calcifications) + len(distortions) + len(asymmetries) > 0
        ):
            birads_category = 2
            description = "Benign finding"
            recommendation = "Routine screening"
        else:
            birads_category = 1
            description = "Negative"
            recommendation = "Routine screening"

        return {
            "birads_category": birads_category,
            "description": description,
            "recommendation": recommendation,
            "assessment_date": "Current analysis",
            "findings_count": {
                "masses": len(masses),
                "calcifications": len(calcifications),
                "distortions": len(distortions),
                "asymmetries": len(asymmetries),
            },
        }

    def create_breast_tissue_from_mammogram(
        self, image, analysis_results, tissue_name: str
    ):
        """
        Create breast tissue representation from mammography analysis.

        :param image: Original mammographic image
        :param analysis_results: Analysis results
        :param tissue_name: Name for the tissue
        :return: BreastTissue object with mammography-derived properties
        """
        breast_mask = analysis_results["breast_mask"]
        density_analysis = analysis_results["density_analysis"]
        cancer_risk_assessment = analysis_results["cancer_risk_assessment"]

        risk_mapping = {
            "low": 0.01,
            "low-moderate": 0.03,
            "moderate": 0.08,
            "high": 0.15,
        }
        cancer_risk = risk_mapping.get(cancer_risk_assessment["risk_level"], 0.01)

        mammographic_density = density_analysis["density_percentage"] / 100.0
        birads_category = density_analysis["birads_category"]

        num_cells = max(10, int(np.sum(breast_mask) / 5000))
        cells = []

        mass_locations = [
            (m["center"][1], m["center"][0]) for m in analysis_results["masses"]
        ]
        calc_locations = [
            (c["center"][1], c["center"][0]) 
            for c in analysis_results["calcifications"]
        ]

        for i in range(num_cells):
            base_health = random.uniform(85, 98)

            for mass_loc in mass_locations:
                y_pos = (i * 100) % image.shape[0]
                x_pos = (i * 100) // image.shape[0] % image.shape[1]
                distance = np.sqrt(
                    (y_pos - mass_loc[0]) ** 2 + (x_pos - mass_loc[1]) ** 2
                )
                if distance < 50:
                    base_health -= random.uniform(5, 15)

            for calc_loc in calc_locations:
                y_pos = (i * 100) % image.shape[0]
                x_pos = (i * 100) // image.shape[0] % image.shape[1]
                distance = np.sqrt(
                    (y_pos - calc_loc[0]) ** 2 + (x_pos - calc_loc[1]) ** 2
                )
                if distance < 30:
                    base_health -= random.uniform(2, 8)

            cell_health = max(50.0, min(100.0, base_health))
            cell_name = f"BreastCell_{i}"
            cells.append(Cell(cell_name, str(cell_health)))

        breast_tissue = BreastTissue(
            name=tissue_name,
            cells=cells,
            cancer_risk=cancer_risk,
            mammographic_density=mammographic_density,
            birads_category=birads_category,
        )

        activity_modifier = min(0.02, cancer_risk_assessment["risk_score"] * 0.005)
        breast_tissue.ductal_activity = min(0.1, 0.03 + activity_modifier)
        breast_tissue.stromal_activity = min(0.1, 0.02 + activity_modifier)

        skin_analysis = analysis_results["skin_analysis"]
        if not skin_analysis["skin_thickness_normal"]:
            breast_tissue.apply_stress(0.3)

        return breast_tissue

    def compare_bilateral_mammograms(self, left_analysis, right_analysis):
        """
        Compare bilateral mammographic findings for asymmetry assessment.

        :param left_analysis: Analysis results for left breast
        :param right_analysis: Analysis results for right breast
        :return: Bilateral comparison results
        """
        comparison_results = {
            "density_difference": abs(
                left_analysis["density_analysis"]["density_percentage"]
                - right_analysis["density_analysis"]["density_percentage"]
            ),
            "findings_asymmetry": {},
            "overall_asymmetry_score": 0,
        }

        # Compare findings counts
        left_counts = {
            "masses": len(left_analysis["masses"]),
            "calcifications": len(left_analysis["calcifications"]),
            "distortions": len(left_analysis["architectural_distortions"]),
        }

        right_counts = {
            "masses": len(right_analysis["masses"]),
            "calcifications": len(right_analysis["calcifications"]),
            "distortions": len(right_analysis["architectural_distortions"]),
        }

        asymmetry_score = 0

        for finding_type in left_counts.keys():
            difference = abs(left_counts[finding_type] - right_counts[finding_type])
            comparison_results["findings_asymmetry"][finding_type] = {
                "left_count": left_counts[finding_type],
                "right_count": right_counts[finding_type],
                "difference": difference,
            }
            asymmetry_score += difference

        # Add density asymmetry to score
        if comparison_results["density_difference"] > 20:  # >20% density difference
            asymmetry_score += 2
        elif comparison_results["density_difference"] > 10:  # >10% density difference
            asymmetry_score += 1

        comparison_results["overall_asymmetry_score"] = asymmetry_score

        # Determine asymmetry significance
        if asymmetry_score >= 5:
            comparison_results["asymmetry_significance"] = "high"
            comparison_results["recommendation"] = (
                "Consider additional imaging or clinical correlation"
            )
        elif asymmetry_score >= 3:
            comparison_results["asymmetry_significance"] = "moderate"
            comparison_results["recommendation"] = "Monitor for changes on follow-up"
        else:
            comparison_results["asymmetry_significance"] = "low"
            comparison_results["recommendation"] = "Continue routine screening"

        return comparison_results

    def export_analysis_report(self, analysis_results, birads_assessment=None):
        """
        Export a comprehensive analysis report.

        :param analysis_results: Analysis results
        :param birads_assessment: Optional BI-RADS assessment
        :return: Formatted report string
        """
        if birads_assessment is None:
            birads_assessment = self.generate_birads_assessment(analysis_results)

        report = f"""
MAMMOGRAPHY ANALYSIS REPORT
===========================

PATIENT INFORMATION:
View: {analysis_results['view']}
Laterality: {analysis_results['laterality']}
Analysis Date: Current

BREAST DENSITY:
BI-RADS Category: {analysis_results['density_analysis']['birads_category']}
Description: {analysis_results['density_analysis']['category_description']}
Dense Tissue Percentage: {analysis_results['density_analysis']['density_percentage']:.1f}%

FINDINGS:

Masses ({len(analysis_results['masses'])} detected):"""

        for i, mass in enumerate(analysis_results["masses"], 1):
            report += f"""
  {i}. Location: ({mass['center'][0]}, {mass['center'][1]})
     Size: {mass['area']} pixels
     Suspicion Level: {mass['suspicion_level']}
     Circularity: {mass['circularity']:.3f}"""

        report += f"""

Calcifications ({len(analysis_results['calcifications'])} detected):"""

        micro_count = sum(
            1
            for c in analysis_results["calcifications"]
            if c["type"] == "microcalcification"
        )
        macro_count = sum(
            1
            for c in analysis_results["calcifications"]
            if c["type"] == "macrocalcification"
        )

        report += f"""
  Microcalcifications: {micro_count}
  Macrocalcifications: {macro_count}"""

        for i, calc in enumerate(analysis_results["calcifications"], 1):
            cluster_info = calc.get("cluster_suspicion", "isolated")
            report += f"""
  {i}. Location: ({calc['center'][0]}, {calc['center'][1]})
     Type: {calc['type']}
     Suspicion Level: {calc['suspicion_level']}
     Cluster Pattern: {cluster_info}"""

        report += f"""

Architectural Distortions ({len(analysis_results['architectural_distortions'])} detected):"""

        for i, distortion in enumerate(
            analysis_results["architectural_distortions"], 1
        ):
            report += f"""
  {i}. Location: ({distortion['center'][0]}, {distortion['center'][1]})
     Dominant Orientation: {distortion['dominant_orientation']}°
     Coherence: {distortion['coherence']:.3f}
     Suspicion Level: {distortion['suspicion_level']}"""

        report += f"""

Asymmetries ({len(analysis_results['asymmetries'])} detected):"""

        for i, asymmetry in enumerate(analysis_results["asymmetries"], 1):
            report += f"""
  {i}. Location: ({asymmetry['center'][0]}, {asymmetry['center'][1]})
     Area: {asymmetry['area']} pixels
     Strength: {asymmetry['strength']:.3f}
     Suspicion Level: {asymmetry['suspicion_level']}"""

        skin_status = (
            "Normal"
            if analysis_results["skin_analysis"]["skin_thickness_normal"]
            else "Thickening detected"
        )

        report += f"""

SKIN ANALYSIS:
Status: {skin_status}
Mean Skin Intensity: {analysis_results['skin_analysis']['mean_skin_intensity']:.3f}

BI-RADS ASSESSMENT:
Category: BI-RADS {birads_assessment['birads_category']}
Description: {birads_assessment['description']}
Recommendation: {birads_assessment['recommendation']}

CANCER RISK ASSESSMENT:
Risk Level: {analysis_results['cancer_risk_assessment']['risk_level'].upper()}
Risk Score: {analysis_results['cancer_risk_assessment']['risk_score']}
Risk Factors:"""

        for factor in analysis_results["cancer_risk_assessment"]["risk_factors"]:
            report += f"""
  - {factor}"""

        report += f"""

RECOMMENDATION:
{analysis_results['cancer_risk_assessment']['recommendation']}

---
Report generated by MammographyAnalyzer
Analysis based on automated image processing algorithms
Clinical correlation and expert radiologist interpretation recommended
        """

        return report
