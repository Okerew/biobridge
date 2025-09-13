import random

import numpy as np
from scipy import ndimage
from skimage import filters, measure, morphology
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from biobridge.blocks.cell import Cell


class SPECTScanAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer

        # SPECT intensity ranges (normalized counts)
        self.activity_ranges = {
            "background": (0.0, 0.1),
            "low_activity": (0.1, 0.3),
            "normal_activity": (0.3, 0.6),
            "high_activity": (0.6, 0.8),
            "very_high_activity": (0.8, 1.0),
        }

        # Common SPECT tracers and their characteristics
        self.tracer_properties = {
            "Tc-99m_MDP": {  # Bone scan
                "organ": "bone",
                "normal_threshold": 0.4,
                "pathological_threshold": 0.7,
                "typical_organs": ["spine", "ribs", "pelvis", "skull"],
            },
            "Tc-99m_MIBI": {  # Heart perfusion
                "organ": "heart",
                "normal_threshold": 0.5,
                "pathological_threshold": 0.3,  # Lower indicates perfusion defect
                "typical_organs": ["myocardium"],
            },
            "Tc-99m_MAG3": {  # Kidney function
                "organ": "kidney",
                "normal_threshold": 0.4,
                "pathological_threshold": 0.2,
                "typical_organs": ["kidneys", "bladder"],
            },
            "I-123_MIBG": {  # Adrenal/neuroendocrine
                "organ": "adrenal",
                "normal_threshold": 0.3,
                "pathological_threshold": 0.6,
                "typical_organs": ["adrenal_glands", "heart"],
            },
        }

    def analyze_spect_scan(
        self,
        image_stack,
        tracer_type="Tc-99m_MDP",
        slice_thickness=5.0,
    ):
        """
        Analyze a SPECT scan volume.

        :param image_stack: Input SPECT scan volume (3D array or list of 2D slices)
        :param tracer_type: Type of radiotracer used
        :param slice_thickness: Thickness of each slice in mm
        :param injection_dose: Injected dose in MBq
        :param acquisition_time: Acquisition time in minutes
        :return: Dictionary containing SPECT analysis results
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

        # Normalize volume to 0-1 range
        normalized_volume = self.normalize_spect_volume(volume)

        # Enhance the volume for better analysis
        enhanced_volume = self.enhance_spect_volume(normalized_volume)

        # Segment activity regions
        activity_segmentation = self.segment_activity_regions(
            normalized_volume, tracer_type
        )

        # Detect activity edges and boundaries
        activity_edges = self.detect_activity_edges(enhanced_volume)

        # Detect activity anomalies
        activity_anomalies = self.detect_activity_anomalies(
            normalized_volume
        )

        # Calculate activity measurements
        activity_measurements = self.calculate_activity_measurements(
            activity_segmentation, normalized_volume, slice_thickness
        )

        # Analyze uptake patterns
        uptake_analysis = self.analyze_uptake_patterns(normalized_volume, tracer_type)

        # Detect hotspots and cold spots
        hotspots, coldspots = self.detect_activity_spots(normalized_volume, tracer_type)

        # Quantitative analysis
        quantitative_metrics = self.calculate_quantitative_metrics(
            normalized_volume, tracer_type
        )

        return {
            "original_volume": volume,
            "normalized_volume": normalized_volume,
            "enhanced_volume": enhanced_volume,
            "activity_segmentation": activity_segmentation,
            "activity_edges": activity_edges,
            "activity_anomalies": activity_anomalies,
            "activity_measurements": activity_measurements,
            "uptake_analysis": uptake_analysis,
            "hotspots": hotspots,
            "coldspots": coldspots,
            "quantitative_metrics": quantitative_metrics,
            "tracer_type": tracer_type,
            "slice_count": volume.shape[0],
            "slice_thickness": slice_thickness,
        }

    def normalize_spect_volume(self, volume):
        """
        Normalize SPECT volume to 0-1 range.
        """
        volume_min = np.min(volume)
        volume_max = np.max(volume)

        if volume_max > volume_min:
            normalized = (volume - volume_min) / (volume_max - volume_min)
        else:
            normalized = volume

        return normalized.astype(np.float32)

    def enhance_spect_volume(self, normalized_volume):
        """
        Enhance SPECT volume using filtering techniques.
        """
        # Apply gentle Gaussian smoothing (SPECT has inherently lower resolution)
        enhanced = ndimage.gaussian_filter(normalized_volume, sigma=1.0)

        # Apply median filter to reduce noise
        enhanced = ndimage.median_filter(enhanced, size=3)

        # Enhance contrast
        enhanced = np.power(enhanced, 0.8)  # Gamma correction

        return enhanced

    def segment_activity_regions(self, normalized_volume, tracer_type):
        """
        Segment different activity regions based on normalized intensity values.
        """
        segmentation = {}

        for region, (min_val, max_val) in self.activity_ranges.items():
            mask = (normalized_volume >= min_val) & (normalized_volume <= max_val)
            # Clean up small artifacts
            mask = morphology.remove_small_objects(mask, min_size=50)
            mask = morphology.remove_small_holes(mask, area_threshold=25)
            segmentation[region] = mask

        # Add tracer-specific segmentation
        tracer_props = self.tracer_properties.get(
            tracer_type, self.tracer_properties["Tc-99m_MDP"]
        )

        if tracer_props["organ"] == "bone":
            # Bone-specific regions
            high_uptake = normalized_volume > tracer_props["pathological_threshold"]
            segmentation["bone_uptake"] = high_uptake

        elif tracer_props["organ"] == "heart":
            # Heart-specific regions
            perfused = normalized_volume > tracer_props["normal_threshold"]
            defect = normalized_volume < tracer_props["pathological_threshold"]
            segmentation["perfused_myocardium"] = perfused
            segmentation["perfusion_defect"] = defect

        elif tracer_props["organ"] == "kidney":
            # Kidney-specific regions
            functioning = normalized_volume > tracer_props["normal_threshold"]
            segmentation["functioning_kidney"] = functioning

        return segmentation

    def detect_activity_edges(self, enhanced_volume):
        """
        Detect activity boundaries and transitions.
        """
        # Calculate gradients
        grad_z, grad_y, grad_x = np.gradient(enhanced_volume)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

        # Apply threshold
        threshold = filters.threshold_otsu(gradient_magnitude)
        edges = gradient_magnitude > threshold

        # Clean up edges
        edges = morphology.binary_closing(edges, morphology.ball(1))

        return edges.astype(np.uint8)

    def detect_activity_anomalies(self, normalized_volume):
        """
        Detect activity anomalies using statistical analysis.
        """
        # Sample points for analysis
        z_coords, y_coords, x_coords = np.meshgrid(
            np.arange(0, normalized_volume.shape[0], 3),
            np.arange(0, normalized_volume.shape[1], 4),
            np.arange(0, normalized_volume.shape[2], 4),
            indexing="ij",
        )

        coords = np.column_stack(
            [z_coords.flatten(), y_coords.flatten(), x_coords.flatten()]
        )

        features = []
        for z, y, x in coords:
            if (
                z < normalized_volume.shape[0]
                and y < normalized_volume.shape[1]
                and x < normalized_volume.shape[2]
            ):

                # Activity value
                activity_val = normalized_volume[z, y, x]

                # Local statistics (7x7x7 neighborhood)
                z_min, z_max = max(0, z - 3), min(normalized_volume.shape[0], z + 4)
                y_min, y_max = max(0, y - 3), min(normalized_volume.shape[1], y + 4)
                x_min, x_max = max(0, x - 3), min(normalized_volume.shape[2], x + 4)

                neighborhood = normalized_volume[z_min:z_max, y_min:y_max, x_min:x_max]
                local_mean = np.mean(neighborhood)
                local_std = np.std(neighborhood)
                local_max = np.max(neighborhood)

                # Calculate contrast
                contrast = local_max - np.mean(neighborhood)

                features.append(
                    [activity_val, local_mean, local_std, local_max, contrast, z, y, x]
                )

        features = np.array(features)

        if len(features) == 0:
            return []

        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Apply Isolation Forest
        clf = IsolationForest(contamination=0.05, random_state=42)
        anomaly_labels = clf.fit_predict(features_normalized)
        anomaly_scores = -clf.score_samples(features_normalized)

        # Extract anomalies
        anomaly_indices = np.where(anomaly_labels == -1)[0]
        anomalies = []

        for idx in anomaly_indices:
            coord = coords[idx]
            score = anomaly_scores[idx]
            activity_val = features[idx][0]

            anomalies.append(
                {
                    "coord": coord,
                    "anomaly_score": score,
                    "activity_value": activity_val,
                    "local_mean": features[idx][1],
                    "local_std": features[idx][2],
                    "contrast": features[idx][4],
                    "classification": self._classify_activity_anomaly(activity_val),
                }
            )

        return sorted(anomalies, key=lambda x: x["activity_value"], reverse=True)

    def _classify_activity_anomaly(self, activity_value):
        """Classify activity anomaly based on normalized intensity."""
        if activity_value > 0.9:
            return "very_high_uptake"
        elif activity_value > 0.7:
            return "high_uptake"
        elif activity_value > 0.4:
            return "moderate_uptake"
        elif activity_value < 0.1:
            return "photopenic_area"
        else:
            return "mild_uptake"

    def calculate_activity_measurements(
        self, activity_segmentation, normalized_volume, slice_thickness
    ):
        """
        Calculate activity measurements for different regions.
        """
        measurements = {}

        for region, mask in activity_segmentation.items():
            if not np.any(mask):
                continue

            region_activity = normalized_volume[mask]
            voxel_count = np.sum(mask)

            measurements[region] = {
                "voxel_count": voxel_count,
                "volume_mm3": voxel_count * slice_thickness,
                "mean_activity": np.mean(region_activity),
                "std_activity": np.std(region_activity),
                "max_activity": np.max(region_activity),
                "min_activity": np.min(region_activity),
                "median_activity": np.median(region_activity),
                "total_counts": np.sum(region_activity),
            }

        return measurements

    def analyze_uptake_patterns(self, normalized_volume, tracer_type):
        """
        Analyze uptake patterns specific to tracer type.
        """
        global_mean = np.mean(normalized_volume)
        global_std = np.std(normalized_volume)
        global_max = np.max(normalized_volume)

        # Heterogeneity analysis
        z_slices = normalized_volume.shape[0]
        slice_variations = []

        for z in range(z_slices):
            slice_data = normalized_volume[z]
            if np.mean(slice_data) > 0:
                cv = np.std(slice_data) / np.mean(slice_data)
                slice_variations.append(cv)

        heterogeneity_index = np.mean(slice_variations) if slice_variations else 0

        # Tracer-specific analysis
        tracer_props = self.tracer_properties.get(
            tracer_type, self.tracer_properties["Tc-99m_MDP"]
        )
        high_threshold = tracer_props["pathological_threshold"]

        return {
            "global_mean_activity": global_mean,
            "global_std_activity": global_std,
            "global_max_activity": global_max,
            "heterogeneity_index": heterogeneity_index,
            "coefficient_of_variation": (
                global_std / global_mean if global_mean > 0 else 0
            ),
            "high_activity_volume": np.sum(normalized_volume > high_threshold),
            "tracer_specific_threshold": high_threshold,
        }

    def detect_activity_spots(self, normalized_volume, tracer_type):
        """
        Detect hotspots and cold spots based on tracer type.
        """
        tracer_props = self.tracer_properties.get(
            tracer_type, self.tracer_properties["Tc-99m_MDP"]
        )

        # Hotspot detection
        if tracer_props["organ"] in ["bone", "adrenal"]:
            hotspot_threshold = tracer_props["pathological_threshold"]
            hotspot_mask = normalized_volume > hotspot_threshold
        else:
            hotspot_threshold = np.percentile(normalized_volume, 95)
            hotspot_mask = normalized_volume > hotspot_threshold

        # Cold spot detection (especially for heart perfusion)
        if tracer_props["organ"] == "heart":
            coldspot_threshold = tracer_props["pathological_threshold"]
            coldspot_mask = normalized_volume < coldspot_threshold
        else:
            coldspot_threshold = np.percentile(normalized_volume, 5)
            coldspot_mask = normalized_volume < coldspot_threshold

        # Clean up masks
        hotspot_mask = morphology.remove_small_objects(hotspot_mask, min_size=20)
        coldspot_mask = morphology.remove_small_objects(coldspot_mask, min_size=20)

        # Label connected components
        labeled_hotspots = measure.label(hotspot_mask)
        labeled_coldspots = measure.label(coldspot_mask)

        # Extract hotspot properties
        hotspots = []
        for region in measure.regionprops(labeled_hotspots):
            hotspot_activity = normalized_volume[labeled_hotspots == region.label]

            hotspots.append(
                {
                    "location": region.centroid,
                    "max_activity": np.max(hotspot_activity),
                    "mean_activity": np.mean(hotspot_activity),
                    "volume": region.area,
                    "bbox": region.bbox,
                    "significance": np.max(hotspot_activity)
                    / np.mean(normalized_volume),
                }
            )

        # Extract coldspot properties
        coldspots = []
        for region in measure.regionprops(labeled_coldspots):
            coldspot_activity = normalized_volume[labeled_coldspots == region.label]

            coldspots.append(
                {
                    "location": region.centroid,
                    "min_activity": np.min(coldspot_activity),
                    "mean_activity": np.mean(coldspot_activity),
                    "volume": region.area,
                    "bbox": region.bbox,
                    "severity": (
                        np.mean(normalized_volume) - np.mean(coldspot_activity)
                    )
                    / np.mean(normalized_volume),
                }
            )

        # Sort by significance/severity
        hotspots = sorted(hotspots, key=lambda x: x["significance"], reverse=True)
        coldspots = sorted(coldspots, key=lambda x: x["severity"], reverse=True)

        return hotspots, coldspots

    def calculate_quantitative_metrics(self, normalized_volume, tracer_type):
        """
        Calculate standard quantitative SPECT metrics.
        """
        mean_activity = np.mean(normalized_volume)
        max_activity = np.max(normalized_volume)

        # Calculate background activity (assume lowest 10% represents background)
        background_threshold = np.percentile(normalized_volume, 10)
        background_mean = np.mean(
            normalized_volume[normalized_volume <= background_threshold]
        )

        # Target-to-background ratio
        target_to_background = (
            max_activity / background_mean if background_mean > 0 else 0
        )

        # Tracer-specific metrics
        tracer_props = self.tracer_properties.get(
            tracer_type, self.tracer_properties["Tc-99m_MDP"]
        )
        pathological_volume = np.sum(
            normalized_volume > tracer_props["pathological_threshold"]
        )

        return {
            "max_activity": max_activity,
            "mean_activity": mean_activity,
            "background_activity": background_mean,
            "target_to_background_ratio": target_to_background,
            "pathological_volume": pathological_volume,
            "activity_concentration_ratio": (
                max_activity / mean_activity if mean_activity > 0 else 0
            ),
        }

    def create_activity_tissue_analysis(
        self, normalized_volume, hotspots, coldspots, tissue_name: str, tracer_type: str
    ):
        """
        Create activity-based tissue analysis from SPECT scan results.
        """
        mean_activity = np.mean(normalized_volume)
        max_activity = np.max(normalized_volume)

        tracer_props = self.tracer_properties.get(
            tracer_type, self.tracer_properties["Tc-99m_MDP"]
        )

        # Determine tissue status based on tracer type and activity
        if tracer_props["organ"] == "bone":
            if max_activity > 0.8:
                activity_status = "increased_bone_uptake"
                pathology_risk = 0.7  # High risk for metastases/infection
            elif max_activity > 0.6:
                activity_status = "moderately_increased_uptake"
                pathology_risk = 0.4
            else:
                activity_status = "normal_bone_uptake"
                pathology_risk = 0.1

        elif tracer_props["organ"] == "heart":
            if len(coldspots) > 2:
                activity_status = "perfusion_defects"
                pathology_risk = 0.8  # High risk for CAD
            elif len(coldspots) > 0:
                activity_status = "mild_perfusion_defects"
                pathology_risk = 0.4
            else:
                activity_status = "normal_perfusion"
                pathology_risk = 0.1

        else:  # General case
            if max_activity > 0.7:
                activity_status = "increased_uptake"
                pathology_risk = 0.6
            else:
                activity_status = "normal_uptake"
                pathology_risk = 0.2

        # Create cells based on activity
        active_regions = np.sum(normalized_volume > 0.3)
        num_cells = max(1, int(active_regions / 2000))

        cells = []
        for i in range(num_cells):
            # Health related to activity pattern
            if activity_status in ["increased_bone_uptake", "perfusion_defects"]:
                health = random.uniform(40, 70)
            else:
                health = random.uniform(70, 95)

            cells.append(Cell(f"ActivityCell_{i}", str(health)))

        return {
            "name": tissue_name,
            "activity_status": activity_status,
            "mean_activity": mean_activity,
            "max_activity": max_activity,
            "pathology_risk": pathology_risk,
            "cells": cells,
            "hotspot_count": len(hotspots),
            "coldspot_count": len(coldspots),
            "hotspots": hotspots,
            "coldspots": coldspots,
            "tracer_type": tracer_type,
        }

    def generate_spect_report(self, analysis_results):
        """
        Generate a comprehensive SPECT scan report.
        """
        report = []
        report.append("=" * 60)
        report.append("SPECT SCAN ANALYSIS REPORT")
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
        report.append(f"Max Activity: {metrics['max_activity']:.3f}")
        report.append(f"Mean Activity: {metrics['mean_activity']:.3f}")
        report.append(f"Background Activity: {metrics['background_activity']:.3f}")
        report.append(
            f"Target-to-Background Ratio: {metrics['target_to_background_ratio']:.2f}"
        )
        report.append(f"Pathological Volume: {metrics['pathological_volume']} voxels")
        report.append("")

        # Uptake analysis
        uptake = analysis_results["uptake_analysis"]
        report.append("UPTAKE PATTERN ANALYSIS:")
        report.append(f"Global Mean Activity: {uptake['global_mean_activity']:.3f}")
        report.append(f"Global Max Activity: {uptake['global_max_activity']:.3f}")
        report.append(f"Heterogeneity Index: {uptake['heterogeneity_index']:.3f}")
        report.append(f"High Activity Volume: {uptake['high_activity_volume']} voxels")
        report.append("")

        # Hotspot findings
        hotspots = analysis_results["hotspots"]
        report.append(f"HOTSPOT ANALYSIS ({len(hotspots)} hotspots detected):")
        if hotspots:
            for i, hotspot in enumerate(hotspots[:3], 1):  # Top 3 hotspots
                report.append(f"  Hotspot {i}:")
                report.append(
                    f"    Location: ({hotspot['location'][0]:.1f}, {hotspot['location'][1]:.1f}, {hotspot['location'][2]:.1f})"
                )
                report.append(f"    Max Activity: {hotspot['max_activity']:.3f}")
                report.append(f"    Mean Activity: {hotspot['mean_activity']:.3f}")
                report.append(f"    Volume: {hotspot['volume']} voxels")
                report.append(f"    Significance: {hotspot['significance']:.2f}")
                report.append("")
        else:
            report.append("  No significant hotspots detected")
            report.append("")

        # Coldspot findings
        coldspots = analysis_results["coldspots"]
        report.append(f"COLDSPOT ANALYSIS ({len(coldspots)} coldspots detected):")
        if coldspots:
            for i, coldspot in enumerate(coldspots[:3], 1):  # Top 3 coldspots
                report.append(f"  Coldspot {i}:")
                report.append(
                    f"    Location: ({coldspot['location'][0]:.1f}, {coldspot['location'][1]:.1f}, {coldspot['location'][2]:.1f})"
                )
                report.append(f"    Min Activity: {coldspot['min_activity']:.3f}")
                report.append(f"    Mean Activity: {coldspot['mean_activity']:.3f}")
                report.append(f"    Volume: {coldspot['volume']} voxels")
                report.append(f"    Severity: {coldspot['severity']:.2f}")
                report.append("")
        else:
            report.append("  No significant coldspots detected")
            report.append("")

        # Clinical interpretation
        report.append("CLINICAL INTERPRETATION:")
        tracer_type = analysis_results["tracer_type"]
        max_activity = metrics["max_activity"]

        if "bone" in tracer_type.lower() or "mdp" in tracer_type.lower():
            if len(hotspots) > 5:
                report.append(
                    "  Multiple bone hotspots detected - consider metastatic disease"
                )
            elif len(hotspots) > 0:
                report.append(
                    "  Focal bone uptake detected - correlate with clinical history"
                )
            else:
                report.append("  Normal bone scan pattern")

        elif "mibi" in tracer_type.lower() or "heart" in tracer_type.lower():
            if len(coldspots) > 2:
                report.append(
                    "  Multiple perfusion defects detected - suggests coronary artery disease"
                )
            elif len(coldspots) > 0:
                report.append(
                    "  Perfusion defect detected - clinical correlation recommended"
                )
            else:
                report.append("  Normal myocardial perfusion")

        else:  # General interpretation
            if max_activity > 0.8:
                report.append("  High uptake detected - further evaluation recommended")
            elif max_activity > 0.5:
                report.append(
                    "  Moderate uptake detected - clinical correlation advised"
                )
            else:
                report.append("  Uptake within normal limits")

        report.append("")
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)

        return "\n".join(report)
