import random

import numpy as np
from scipy import ndimage
from skimage import filters, measure, morphology
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from biobridge.blocks.cell import Cell


class PETScanAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer
        # Standard Uptake Value (SUV) ranges for different conditions
        self.suv_ranges = {
            "background": (0.0, 1.0),
            "normal_tissue": (1.0, 2.5),
            "inflammation": (2.5, 5.0),
            "mild_hypermetabolism": (5.0, 10.0),
            "high_hypermetabolism": (10.0, 20.0),
            "very_high_hypermetabolism": (20.0, 100.0),
        }

        # Common PET tracers and their characteristics
        self.tracer_properties = {
            "FDG": {  # Fluorodeoxyglucose - glucose metabolism
                "normal_brain_suv": 7.0,
                "normal_liver_suv": 2.5,
                "normal_muscle_suv": 1.0,
                "pathological_threshold": 2.5,
            },
            "F-DOPA": {  # Dopamine metabolism
                "normal_brain_suv": 3.0,
                "pathological_threshold": 1.5,
            },
            "F-Choline": {  # Cell membrane synthesis
                "normal_liver_suv": 2.0,
                "pathological_threshold": 2.0,
            },
        }

    def analyze_pet_scan(
        self,
        image_stack,
        tracer_type="FDG",
        slice_thickness=1.0,
        injection_dose=10.0,
        patient_weight=70.0,
        scan_time=60.0,
    ):
        """
        Analyze a PET scan volume using advanced 3D metabolic analysis.

        :param image_stack: Input PET scan volume (3D array or list of 2D slices)
        :param tracer_type: Type of radiotracer used (FDG, F-DOPA, F-Choline)
        :param slice_thickness: Thickness of each slice in mm
        :param injection_dose: Injected dose in MBq
        :param patient_weight: Patient weight in kg
        :param scan_time: Time from injection to scan in minutes
        :return: Dictionary containing comprehensive PET analysis results
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

        # Convert to Standard Uptake Values (SUV)
        suv_volume = self.convert_to_suv(
            volume, injection_dose, patient_weight, scan_time
        )

        # Enhance the volume for better analysis
        enhanced_volume = self.enhance_pet_volume(suv_volume)

        # Segment metabolic regions
        metabolic_segmentation = self.segment_metabolic_regions(suv_volume, tracer_type)

        # Detect metabolic edges and boundaries
        metabolic_edges = self.detect_metabolic_edges(enhanced_volume)

        # Detect metabolic anomalies
        metabolic_anomalies = self.detect_metabolic_anomalies(
            suv_volume, metabolic_segmentation
        )

        # Calculate metabolic measurements
        metabolic_measurements = self.calculate_metabolic_measurements(
            metabolic_segmentation, suv_volume, slice_thickness
        )

        # Analyze uptake patterns
        uptake_analysis = self.analyze_uptake_patterns(suv_volume)

        # Detect hypermetabolic lesions
        lesions = self.detect_hypermetabolic_lesions(
            suv_volume, metabolic_segmentation, tracer_type
        )

        # Quantitative analysis
        quantitative_metrics = self.calculate_quantitative_metrics(
            suv_volume
        )

        # Time-activity analysis (if multiple time points available)
        kinetic_analysis = self.analyze_tracer_kinetics(suv_volume)

        return {
            "original_volume": volume,
            "suv_volume": suv_volume,
            "enhanced_volume": enhanced_volume,
            "metabolic_segmentation": metabolic_segmentation,
            "metabolic_edges": metabolic_edges,
            "metabolic_anomalies": metabolic_anomalies,
            "metabolic_measurements": metabolic_measurements,
            "uptake_analysis": uptake_analysis,
            "lesions": lesions,
            "quantitative_metrics": quantitative_metrics,
            "kinetic_analysis": kinetic_analysis,
            "tracer_type": tracer_type,
            "slice_count": volume.shape[0],
            "slice_thickness": slice_thickness,
        }

    def convert_to_suv(self, volume, injection_dose, patient_weight, scan_time):
        """
        Convert raw PET values to Standardized Uptake Values (SUV).

        :param volume: Input PET volume (activity concentration)
        :param injection_dose: Injected dose in MBq
        :param patient_weight: Patient weight in kg
        :param scan_time: Time from injection in minutes
        :return: Volume in SUV units
        """
        # Apply decay correction (assuming F-18 with 109.8 min half-life)
        decay_constant = np.log(2) / 109.8  # min^-1
        decay_factor = np.exp(decay_constant * scan_time)

        # Convert to SUV: (tissue_activity * body_weight) / injected_dose
        # Assuming volume is in kBq/ml, convert to MBq/ml
        suv_volume = (
            (volume / 1000.0) * patient_weight / (injection_dose * decay_factor)
        )

        return suv_volume.astype(np.float32)

    def enhance_pet_volume(self, suv_volume):
        """
        Enhance PET volume using specialized filtering for metabolic data.

        :param suv_volume: Input volume in SUV units
        :return: Enhanced volume
        """
        # Apply edge-preserving smoothing
        enhanced = ndimage.gaussian_filter(suv_volume, sigma=0.5)

        # Apply bilateral filter-like enhancement
        for _ in range(2):
            enhanced = (
                filters.rank.mean_bilateral(
                    (enhanced * 100).astype(np.uint8), morphology.disk(2), s0=10, s1=10
                ).astype(np.float32)
                / 100.0
            )

        # Enhance contrast while preserving low values
        enhanced = np.where(enhanced > 1.0, enhanced * 1.2, enhanced)

        return enhanced

    def segment_metabolic_regions(self, suv_volume, tracer_type):
        """
        Segment different metabolic activity regions based on SUV values.

        :param suv_volume: Volume in SUV units
        :param tracer_type: Type of radiotracer
        :return: Dictionary of metabolic region masks
        """
        segmentation = {}

        for region, (min_suv, max_suv) in self.suv_ranges.items():
            mask = (suv_volume >= min_suv) & (suv_volume <= max_suv)
            # Clean up small artifacts
            mask = morphology.remove_small_objects(mask, min_size=20)
            mask = morphology.remove_small_holes(mask, area_threshold=10)
            segmentation[region] = mask

        # Add tracer-specific segmentation
        if tracer_type == "FDG":
            # Brain segmentation for FDG
            brain_mask = suv_volume > 5.0  # Typical brain FDG uptake
            segmentation["brain_tissue"] = brain_mask

            # Liver segmentation
            liver_mask = (suv_volume > 1.5) & (suv_volume < 4.0)
            segmentation["liver_tissue"] = liver_mask

        return segmentation

    def detect_metabolic_edges(self, enhanced_volume):
        """
        Detect metabolic boundaries and transitions.

        :param enhanced_volume: Enhanced SUV volume
        :return: 3D metabolic edge volume
        """
        # Calculate gradients in all directions
        grad_z, grad_y, grad_x = np.gradient(enhanced_volume)

        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

        # Apply adaptive threshold based on local statistics
        threshold = filters.threshold_otsu(gradient_magnitude)
        edges = gradient_magnitude > threshold

        # Clean up edges
        edges = morphology.binary_closing(edges, morphology.ball(1))

        return edges.astype(np.uint8)

    def detect_metabolic_anomalies(self, suv_volume, metabolic_segmentation):
        """
        Detect metabolic anomalies using machine learning on SUV patterns.

        :param suv_volume: Volume in SUV units
        :param metabolic_segmentation: Metabolic segmentation masks
        :return: List of metabolic anomaly locations and characteristics
        """
        # Sample points for analysis
        z_coords, y_coords, x_coords = np.meshgrid(
            np.arange(0, suv_volume.shape[0], 2),
            np.arange(0, suv_volume.shape[1], 3),
            np.arange(0, suv_volume.shape[2], 3),
            indexing="ij",
        )

        coords = np.column_stack(
            [z_coords.flatten(), y_coords.flatten(), x_coords.flatten()]
        )

        features = []
        for z, y, x in coords:
            if (
                z < suv_volume.shape[0]
                and y < suv_volume.shape[1]
                and x < suv_volume.shape[2]
            ):
                # SUV value
                suv_val = suv_volume[z, y, x]

                # Local metabolic statistics (5x5x5 neighborhood)
                z_min, z_max = max(0, z - 2), min(suv_volume.shape[0], z + 3)
                y_min, y_max = max(0, y - 2), min(suv_volume.shape[1], y + 3)
                x_min, x_max = max(0, x - 2), min(suv_volume.shape[2], x + 3)

                neighborhood = suv_volume[z_min:z_max, y_min:y_max, x_min:x_max]
                local_mean = np.mean(neighborhood)
                local_std = np.std(neighborhood)
                local_max = np.max(neighborhood)

                # Calculate contrast and heterogeneity
                contrast = local_max - np.mean(neighborhood)

                # Metabolic region encoding
                region_encoding = 0
                for i, (region, mask) in enumerate(metabolic_segmentation.items()):
                    if mask[z, y, x]:
                        region_encoding = i + 1
                        break

                features.append(
                    [
                        suv_val,
                        local_mean,
                        local_std,
                        local_max,
                        contrast,
                        region_encoding,
                        z,
                        y,
                        x,
                    ]
                )

        features = np.array(features)

        if len(features) == 0:
            return []

        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Apply Isolation Forest for anomaly detection
        clf = IsolationForest(contamination=0.01, random_state=42)
        anomaly_labels = clf.fit_predict(features_normalized)
        anomaly_scores = -clf.score_samples(features_normalized)

        # Extract anomalies with high SUV values (potential pathology)
        anomaly_indices = np.where((anomaly_labels == -1) & (features[:, 0] > 2.5))[0]
        anomalies = []

        for idx in anomaly_indices:
            coord = coords[idx]
            score = anomaly_scores[idx]
            suv_val = features[idx][0]

            anomalies.append(
                {
                    "coord": coord,
                    "anomaly_score": score,
                    "suv_value": suv_val,
                    "local_mean": features[idx][1],
                    "local_std": features[idx][2],
                    "contrast": features[idx][4],
                    "classification": self._classify_metabolic_anomaly(suv_val),
                }
            )

        return sorted(anomalies, key=lambda x: x["suv_value"], reverse=True)

    def _classify_metabolic_anomaly(self, suv_value):
        """Classify metabolic anomaly based on SUV value."""
        if suv_value > 15:
            return "very_high_uptake"
        elif suv_value > 8:
            return "high_uptake"
        elif suv_value > 4:
            return "moderate_uptake"
        else:
            return "mild_uptake"

    def calculate_metabolic_measurements(
        self, metabolic_segmentation, suv_volume, slice_thickness
    ):
        """
        Calculate metabolic measurements for different regions.

        :param metabolic_segmentation: Metabolic segmentation masks
        :param suv_volume: Volume in SUV units
        :param slice_thickness: Slice thickness in mm
        :return: Dictionary of metabolic measurements
        """
        measurements = {}

        for region, mask in metabolic_segmentation.items():
            if not np.any(mask):
                continue

            region_suv = suv_volume[mask]
            voxel_count = np.sum(mask)

            # Basic statistics
            measurements[region] = {
                "voxel_count": voxel_count,
                "volume_mm3": voxel_count * slice_thickness,
                "mean_suv": np.mean(region_suv),
                "std_suv": np.std(region_suv),
                "max_suv": np.max(region_suv),
                "min_suv": np.min(region_suv),
                "median_suv": np.median(region_suv),
                "percentile_95_suv": np.percentile(region_suv, 95),
                "total_uptake": np.sum(region_suv),
                "metabolic_volume": np.sum(region_suv > 2.5) * slice_thickness,  # MTV
                "total_lesion_glycolysis": np.sum(region_suv[region_suv > 2.5]),  # TLG
            }

        return measurements

    def analyze_uptake_patterns(self, suv_volume):
        """
        Analyze uptake patterns throughout the volume.

        :param suv_volume: Volume in SUV units
        :param tracer_type: Type of radiotracer
        :return: Uptake pattern analysis
        """
        # Global statistics
        global_mean = np.mean(suv_volume)
        global_std = np.std(suv_volume)
        global_max = np.max(suv_volume)

        # Uptake distribution analysis
        hist, bin_edges = np.histogram(suv_volume.flatten(), bins=50, density=True)

        # Find peaks in distribution
        peak_indices = []
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i - 1] and hist[i] > hist[i + 1]:
                peak_indices.append(i)

        peaks = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in peak_indices]

        # Heterogeneity analysis
        # Calculate coefficient of variation in different regions
        z_slices = suv_volume.shape[0]
        slice_variations = []

        for z in range(z_slices):
            slice_data = suv_volume[z]
            if np.mean(slice_data) > 0:
                cv = np.std(slice_data) / np.mean(slice_data)
                slice_variations.append(cv)

        heterogeneity_index = np.mean(slice_variations) if slice_variations else 0

        return {
            "global_mean_suv": global_mean,
            "global_std_suv": global_std,
            "global_max_suv": global_max,
            "uptake_peaks": peaks,
            "heterogeneity_index": heterogeneity_index,
            "coefficient_of_variation": (
                global_std / global_mean if global_mean > 0 else 0
            ),
            "high_uptake_volume": np.sum(suv_volume > 5.0),
            "pathological_volume": np.sum(suv_volume > 2.5),
        }

    def detect_hypermetabolic_lesions(
        self, suv_volume, metabolic_segmentation, tracer_type
    ):
        """
        Detect and characterize hypermetabolic lesions.

        :param suv_volume: Volume in SUV units
        :param metabolic_segmentation: Metabolic segmentation masks
        :param tracer_type: Type of radiotracer
        :return: List of detected lesions
        """
        tracer_props = self.tracer_properties.get(
            tracer_type, self.tracer_properties["FDG"]
        )
        threshold = tracer_props["pathological_threshold"]

        # Create lesion mask
        lesion_mask = suv_volume > threshold

        # Remove normal physiological uptake regions
        if "brain_tissue" in metabolic_segmentation:
            lesion_mask = lesion_mask & ~metabolic_segmentation["brain_tissue"]
        if "liver_tissue" in metabolic_segmentation:
            lesion_mask = lesion_mask & ~metabolic_segmentation["liver_tissue"]

        # Clean up small artifacts
        lesion_mask = morphology.remove_small_objects(lesion_mask, min_size=10)

        # Label connected components
        labeled_lesions = measure.label(lesion_mask)

        lesions = []
        for region in measure.regionprops(labeled_lesions):
            lesion_suv = suv_volume[labeled_lesions == region.label]

            # Calculate lesion characteristics
            suv_max = np.max(lesion_suv)
            suv_mean = np.mean(lesion_suv)
            suv_peak = np.percentile(lesion_suv, 95)  # SUVpeak

            # Calculate metabolic tumor volume (MTV)
            mtv = region.area

            # Calculate total lesion glycolysis (TLG)
            tlg = np.sum(lesion_suv)

            lesion_info = {
                "location": region.centroid,
                "suv_max": suv_max,
                "suv_mean": suv_mean,
                "suv_peak": suv_peak,
                "mtv": mtv,
                "tlg": tlg,
                "volume": region.area,
                "bbox": region.bbox,
                "malignancy_score": self._calculate_malignancy_score(
                    suv_max, suv_mean, mtv
                ),
                "heterogeneity": np.std(lesion_suv) / suv_mean if suv_mean > 0 else 0,
            }

            lesions.append(lesion_info)

        # Sort by SUV max (most suspicious first)
        return sorted(lesions, key=lambda x: x["suv_max"], reverse=True)

    def _calculate_malignancy_score(self, suv_max, suv_mean, mtv):
        """Calculate a simple malignancy risk score."""
        score = 0

        # SUV max contribution
        if suv_max > 10:
            score += 0.4
        elif suv_max > 5:
            score += 0.2

        # SUV mean contribution
        if suv_mean > 6:
            score += 0.3
        elif suv_mean > 3:
            score += 0.15

        # Size contribution
        if mtv > 1000:
            score += 0.3
        elif mtv > 100:
            score += 0.15

        return min(1.0, score)

    def calculate_quantitative_metrics(self, suv_volume):
        """
        Calculate standard quantitative PET metrics.

        :param suv_volume: Volume in SUV units
        :param tracer_type: Type of radiotracer
        :return: Dictionary of quantitative metrics
        """
        # Whole body metrics
        wb_mean = np.mean(suv_volume)
        wb_std = np.std(suv_volume)

        # Liver metrics (reference organ)
        liver_roi = suv_volume[
            suv_volume.shape[0] // 2 - 5 : suv_volume.shape[0] // 2 + 5,
            suv_volume.shape[1] // 3 : 2 * suv_volume.shape[1] // 3,
            suv_volume.shape[2] // 4 : 3 * suv_volume.shape[2] // 4,
        ]
        liver_mean = np.mean(liver_roi)

        # Calculate SUV ratios
        target_to_background = np.max(suv_volume) / wb_mean if wb_mean > 0 else 0
        target_to_liver = np.max(suv_volume) / liver_mean if liver_mean > 0 else 0

        return {
            "suv_max": np.max(suv_volume),
            "suv_mean": wb_mean,
            "suv_std": wb_std,
            "liver_mean": liver_mean,
            "target_to_background_ratio": target_to_background,
            "target_to_liver_ratio": target_to_liver,
            "metabolic_volume_threshold_2_5": np.sum(suv_volume > 2.5),
            "metabolic_volume_threshold_5_0": np.sum(suv_volume > 5.0),
            "total_lesion_glycolysis": np.sum(suv_volume[suv_volume > 2.5]),
        }

    def analyze_tracer_kinetics(self, suv_volume):
        """
        Analyze tracer kinetics (simplified for single time point).

        :param suv_volume: Volume in SUV units
        :return: Kinetic analysis results
        """
        # For single time point, we can only estimate
        # In practice, this would require multiple time points

        # Estimate uptake characteristics based on distribution
        fast_uptake = np.sum(
            suv_volume > 10.0
        )  # Very high uptake suggests fast kinetics
        moderate_uptake = np.sum((suv_volume > 2.5) & (suv_volume <= 10.0))

        return {
            "fast_uptake_volume": fast_uptake,
            "moderate_uptake_volume": moderate_uptake,
            "uptake_slope_estimate": np.max(suv_volume)
            / np.mean(suv_volume[suv_volume > 0]),
            "note": "Single time point analysis - kinetic modeling requires multiple time points",
        }

    def visualize_pet_analysis(self, analysis_results, slice_index=None):
        """
        Visualize PET analysis results for a specific slice.

        :param analysis_results: Results from analyze_pet_scan method
        :param slice_index: Index of slice to visualize
        """
        import matplotlib.pyplot as plt

        if slice_index is None:
            slice_index = analysis_results["suv_volume"].shape[0] // 2

        fig, axs = plt.subplots(2, 4, figsize=(20, 10))

        # Original slice
        axs[0, 0].imshow(analysis_results["original_volume"][slice_index], cmap="hot")
        axs[0, 0].set_title(f"Original PET Slice {slice_index}")

        # SUV slice
        im1 = axs[0, 1].imshow(analysis_results["suv_volume"][slice_index], cmap="hot")
        axs[0, 1].set_title("SUV Map")
        plt.colorbar(im1, ax=axs[0, 1], shrink=0.8)

        # Enhanced slice
        axs[0, 2].imshow(analysis_results["enhanced_volume"][slice_index], cmap="hot")
        axs[0, 2].set_title("Enhanced PET")

        # Metabolic segmentation
        seg_slice = np.zeros(analysis_results["suv_volume"][slice_index].shape)
        colors = [1, 2, 3, 4, 5, 6]

        for i, (region, mask) in enumerate(
            analysis_results["metabolic_segmentation"].items()
        ):
            if i < len(colors):
                seg_slice += mask[slice_index] * colors[i]

        axs[0, 3].set_title("Metabolic Regions")

        # Metabolic edges
        axs[1, 0].imshow(analysis_results["metabolic_edges"][slice_index], cmap="gray")
        axs[1, 0].set_title("Metabolic Boundaries")

        # Lesions overlay
        lesion_slice = analysis_results["suv_volume"][slice_index].copy()
        for lesion in analysis_results["lesions"]:
            z, y, x = lesion["location"]
            if abs(z - slice_index) < 2:  # Show lesions within 2 slices
                y, x = int(y), int(x)
                if 0 <= y < lesion_slice.shape[0] and 0 <= x < lesion_slice.shape[1]:
                    lesion_slice[y - 2 : y + 3, x - 2 : x + 3] = (
                        np.max(lesion_slice) * 1.2
                    )

        axs[1, 1].imshow(lesion_slice, cmap="hot")
        axs[1, 1].set_title("Detected Lesions")

        # SUV distribution histogram
        suv_flat = analysis_results["suv_volume"].flatten()
        axs[1, 2].hist(suv_flat[suv_flat > 0], bins=50, alpha=0.7)
        axs[1, 2].set_xlabel("SUV")
        axs[1, 2].set_ylabel("Frequency")
        axs[1, 2].set_title("SUV Distribution")
        axs[1, 2].axvline(x=2.5, color="r", linestyle="--", label="Threshold")
        axs[1, 2].legend()

        # Quantitative metrics
        metrics = analysis_results["quantitative_metrics"]
        metric_names = ["SUV_max", "SUV_mean", "TBR", "TLR"]
        metric_values = [
            metrics["suv_max"],
            metrics["suv_mean"],
            metrics["target_to_background_ratio"],
            metrics["target_to_liver_ratio"],
        ]

        bars = axs[1, 3].bar(metric_names, metric_values)
        axs[1, 3].set_title("Key Metrics")
        axs[1, 3].set_ylabel("Value")

        # Color bars based on values
        for i, bar in enumerate(bars):
            if i == 0 and metric_values[i] > 5:  # High SUV max
                bar.set_color("red")
            elif i in [2, 3] and metric_values[i] > 2:  # High ratios
                bar.set_color("orange")
            else:
                bar.set_color("blue")

        plt.xticks(rotation=45)

        for ax in axs.flat[:6]:  # All except the last two which are plots
            ax.axis("off")

        plt.tight_layout()
        plt.show()

    def create_metabolic_tissue_analysis(self, suv_volume, lesions, tissue_name: str):
        """
        Create metabolic tissue analysis from PET scan results.

        :param suv_volume: Volume in SUV units
        :param metabolic_segmentation: Metabolic segmentation masks
        :param lesions: Detected lesions
        :param tissue_name: Name for the tissue analysis
        :return: Dictionary with metabolic tissue characteristics
        """
        # Calculate overall metabolic activity
        mean_suv = np.mean(suv_volume)
        max_suv = np.max(suv_volume)

        # Determine tissue metabolic status
        if max_suv > 10:
            metabolic_status = "hypermetabolic"
            cancer_risk = 0.8
        elif max_suv > 5:
            metabolic_status = "moderately_hypermetabolic"
            cancer_risk = 0.4
        elif mean_suv > 2.5:
            metabolic_status = "mildly_hypermetabolic"
            cancer_risk = 0.2
        else:
            metabolic_status = "normal"
            cancer_risk = 0.05

        # Create cells based on metabolic activity
        high_activity_regions = np.sum(suv_volume > 5.0)
        num_cells = max(1, int(high_activity_regions / 1000))

        cells = []
        for i in range(num_cells):
            # Health inversely related to SUV (high SUV might indicate pathology)
            if mean_suv > 8:
                health = random.uniform(40, 70)
            elif mean_suv > 4:
                health = random.uniform(60, 80)
            else:
                health = random.uniform(80, 95)

            cells.append(Cell(f"MetabolicCell_{i}", str(health)))

        # Calculate metabolic metrics
        metabolic_volume = np.sum(suv_volume > 2.5)
        total_lesion_glycolysis = np.sum(suv_volume[suv_volume > 2.5])

        return {
            "name": tissue_name,
            "metabolic_status": metabolic_status,
            "mean_suv": mean_suv,
            "max_suv": max_suv,
            "metabolic_volume": metabolic_volume,
            "total_lesion_glycolysis": total_lesion_glycolysis,
            "cancer_risk": cancer_risk,
            "cells": cells,
            "lesion_count": len(lesions),
            "lesions": lesions,
            "metabolic_heterogeneity": (
                np.std(suv_volume) / mean_suv if mean_suv > 0 else 0
            ),
        }

    def compare_pet_ct(self, pet_results, ct_results):
        """
        Compare PET and CT scan results for comprehensive analysis.

        :param pet_results: Results from PET scan analysis
        :param ct_results: Results from CT scan analysis
        :return: Combined analysis results
        """
        # Find structural-metabolic correlations
        correlations = []

        # Check if CT anomalies correspond to metabolic hotspots
        if "anomalies_3d" in ct_results and pet_results["lesions"]:
            for ct_anomaly in ct_results["anomalies_3d"]:
                ct_coord = ct_anomaly["coord"]

                for pet_lesion in pet_results["lesions"]:
                    pet_coord = pet_lesion["location"]

                    # Calculate 3D distance
                    distance = np.sqrt(
                        sum((c1 - c2) ** 2 for c1, c2 in zip(ct_coord, pet_coord))
                    )

                    if distance < 5:  # Within 5 voxels
                        correlations.append(
                            {
                                "ct_anomaly": ct_anomaly,
                                "pet_lesion": pet_lesion,
                                "distance": distance,
                                "correlation_type": "structural_metabolic",
                                "significance": pet_lesion["suv_max"]
                                * (1 / (distance + 1)),
                            }
                        )

        # Tissue-specific analysis
        tissue_analysis = {}

        # Bone tissue correlation
        if "bone" in ct_results.get("tissue_segmentation", {}):
            bone_mask = ct_results["tissue_segmentation"]["bone"]
            bone_suv = pet_results["suv_volume"][bone_mask]

            if len(bone_suv) > 0:
                tissue_analysis["bone"] = {
                    "mean_suv": np.mean(bone_suv),
                    "max_suv": np.max(bone_suv),
                    "metabolic_activity": "high" if np.mean(bone_suv) > 3 else "normal",
                    "potential_metastases": len(
                        [
                            lesion
                            for lesion in pet_results["lesions"]
                            if lesion["suv_max"] > 4
                            and self._is_in_bone(lesion["location"], bone_mask)
                        ]
                    ),
                }

        # Lung tissue correlation
        if "lung" in ct_results.get("tissue_segmentation", {}):
            lung_mask = ct_results["tissue_segmentation"]["lung"]
            lung_suv = pet_results["suv_volume"][lung_mask]

            if len(lung_suv) > 0:
                tissue_analysis["lung"] = {
                    "mean_suv": np.mean(lung_suv),
                    "max_suv": np.max(lung_suv),
                    "metabolic_activity": "high" if np.mean(lung_suv) > 2 else "normal",
                    "potential_nodules": len(
                        [
                            lesion
                            for lesion in pet_results["lesions"]
                            if lesion["suv_max"] > 2.5
                            and self._is_in_lung(lesion["location"], lung_mask)
                        ]
                    ),
                }

        return {
            "structural_metabolic_correlations": correlations,
            "tissue_specific_analysis": tissue_analysis,
            "combined_risk_assessment": self._calculate_combined_risk(
                correlations, tissue_analysis
            ),
            "diagnostic_confidence": self._calculate_diagnostic_confidence(
                correlations
            ),
            "recommendations": self._generate_recommendations(
                correlations, tissue_analysis
            ),
        }

    def _is_in_bone(self, location, bone_mask):
        """Check if a location is within bone tissue."""
        z, y, x = [int(coord) for coord in location]
        if (
            0 <= z < bone_mask.shape[0]
            and 0 <= y < bone_mask.shape[1]
            and 0 <= x < bone_mask.shape[2]
        ):
            return bone_mask[z, y, x]
        return False

    def _is_in_lung(self, location, lung_mask):
        """Check if a location is within lung tissue."""
        z, y, x = [int(coord) for coord in location]
        if (
            0 <= z < lung_mask.shape[0]
            and 0 <= y < lung_mask.shape[1]
            and 0 <= x < lung_mask.shape[2]
        ):
            return lung_mask[z, y, x]
        return False

    def _calculate_combined_risk(self, correlations, tissue_analysis):
        """Calculate combined risk assessment from PET/CT correlation."""
        risk_score = 0.0

        # High-significance correlations increase risk
        for corr in correlations:
            if corr["significance"] > 10:
                risk_score += 0.3
            elif corr["significance"] > 5:
                risk_score += 0.2

        # Tissue-specific risks
        for tissue, analysis in tissue_analysis.items():
            if analysis.get("metabolic_activity") == "high":
                risk_score += 0.2
            if analysis.get("potential_metastases", 0) > 0:
                risk_score += 0.4
            if analysis.get("potential_nodules", 0) > 0:
                risk_score += 0.3

        return min(1.0, risk_score)

    def _calculate_diagnostic_confidence(self, correlations):
        """Calculate diagnostic confidence based on correlations."""
        if len(correlations) == 0:
            return 0.3  # Low confidence without correlations

        high_conf_correlations = [c for c in correlations if c["significance"] > 5]

        if len(high_conf_correlations) >= 2:
            return 0.9  # High confidence
        elif len(high_conf_correlations) == 1:
            return 0.7  # Moderate confidence
        else:
            return 0.5  # Fair confidence

    def _generate_recommendations(self, correlations, tissue_analysis):
        """Generate clinical recommendations based on analysis."""
        recommendations = []

        # High-significance findings
        high_sig_correlations = [c for c in correlations if c["significance"] > 8]
        if high_sig_correlations:
            recommendations.append(
                "Consider biopsy for high-significance structural-metabolic correlations"
            )

        # Bone metastases
        bone_mets = tissue_analysis.get("bone", {}).get("potential_metastases", 0)
        if bone_mets > 0:
            recommendations.append(
                f"Evaluate {bone_mets} potential bone metastases with bone scan"
            )

        # Lung nodules
        lung_nodules = tissue_analysis.get("lung", {}).get("potential_nodules", 0)
        if lung_nodules > 0:
            recommendations.append(
                f"Follow-up imaging for {lung_nodules} metabolically active lung nodules"
            )

        # General recommendations
        if len(correlations) > 3:
            recommendations.append(
                "Consider multidisciplinary team review for multiple findings"
            )

        if not recommendations:
            recommendations.append("Continue routine surveillance")

        return recommendations

    def generate_pet_report(self, analysis_results):
        """
        Generate a comprehensive PET scan report.

        :param analysis_results: Results from analyze_pet_scan method
        :return: Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("PET SCAN ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")

        # Basic scan information
        report.append("SCAN INFORMATION:")
        report.append(f"Tracer Type: {analysis_results['tracer_type']}")
        report.append(f"Number of Slices: {analysis_results['slice_count']}")
        report.append(f"Slice Thickness: {analysis_results['slice_thickness']} mm")
        report.append("")

        # Quantitative metrics
        metrics = analysis_results["quantitative_metrics"]
        report.append("QUANTITATIVE ANALYSIS:")
        report.append(f"SUV Max: {metrics['suv_max']:.2f}")
        report.append(f"SUV Mean: {metrics['suv_mean']:.2f}")
        report.append(
            f"Target-to-Background Ratio: {metrics['target_to_background_ratio']:.2f}"
        )
        report.append(f"Target-to-Liver Ratio: {metrics['target_to_liver_ratio']:.2f}")
        report.append(
            f"Total Lesion Glycolysis: {metrics['total_lesion_glycolysis']:.2f}"
        )
        report.append("")

        # Uptake analysis
        uptake = analysis_results["uptake_analysis"]
        report.append("UPTAKE PATTERN ANALYSIS:")
        report.append(f"Global SUV Mean: {uptake['global_mean_suv']:.2f}")
        report.append(f"Global SUV Max: {uptake['global_max_suv']:.2f}")
        report.append(f"Heterogeneity Index: {uptake['heterogeneity_index']:.3f}")
        report.append(f"Pathological Volume: {uptake['pathological_volume']} voxels")
        report.append("")

        # Lesion findings
        lesions = analysis_results["lesions"]
        report.append(f"LESION ANALYSIS ({len(lesions)} lesions detected):")
        if lesions:
            for i, lesion in enumerate(lesions[:5], 1):  # Top 5 lesions
                report.append(f"  Lesion {i}:")
                report.append(
                    f"    Location: ({lesion['location'][0]:.1f}, {lesion['location'][1]:.1f}, {lesion['location'][2]:.1f})"
                )
                report.append(f"    SUV Max: {lesion['suv_max']:.2f}")
                report.append(f"    SUV Mean: {lesion['suv_mean']:.2f}")
                report.append(f"    MTV: {lesion['mtv']} voxels")
                report.append(f"    TLG: {lesion['tlg']:.2f}")
                report.append(f"    Malignancy Score: {lesion['malignancy_score']:.2f}")
                report.append("")
        else:
            report.append("  No significant hypermetabolic lesions detected")
            report.append("")

        # Metabolic anomalies
        anomalies = analysis_results["metabolic_anomalies"]
        report.append(f"METABOLIC ANOMALIES ({len(anomalies)} detected):")
        if anomalies:
            for i, anomaly in enumerate(anomalies[:3], 1):  # Top 3 anomalies
                report.append(f"  Anomaly {i}:")
                report.append(
                    f"    Location: ({anomaly['coord'][0]}, {anomaly['coord'][1]}, {anomaly['coord'][2]})"
                )
                report.append(f"    SUV Value: {anomaly['suv_value']:.2f}")
                report.append(f"    Classification: {anomaly['classification']}")
                report.append(f"    Anomaly Score: {anomaly['anomaly_score']:.3f}")
                report.append("")
        else:
            report.append("  No significant metabolic anomalies detected")
            report.append("")

        # Clinical interpretation
        report.append("CLINICAL INTERPRETATION:")
        max_suv = metrics["suv_max"]
        if max_suv > 10:
            report.append("  High-grade hypermetabolic activity detected")
            report.append(
                "  Recommend correlation with clinical history and further evaluation"
            )
        elif max_suv > 5:
            report.append("  Moderate hypermetabolic activity detected")
            report.append("  Clinical correlation recommended")
        elif max_suv > 2.5:
            report.append("  Mild hypermetabolic activity detected")
            report.append("  Consider follow-up if clinically indicated")
        else:
            report.append("  No significant hypermetabolic activity detected")
            report.append("  Findings within normal limits")

        report.append("")
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)

        return "\n".join(report)
