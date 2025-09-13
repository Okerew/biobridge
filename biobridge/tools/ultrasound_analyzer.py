import random

import numpy as np
from scipy import ndimage
from skimage import feature, filters, measure, morphology, restoration

from biobridge.blocks.cell import Cell
from biobridge.definitions.tissues.muscle import MuscleTissue
from biobridge.definitions.tissues.organ import OrganTissue


class UltrasoundAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer

        # Acoustic impedance ranges for different tissues (in Rayls x 10^6)
        # These are approximate ranges for ultrasound echogenicity classification
        self.echogenicity_ranges = {
            "anechoic": (0, 0.05),  # Fluid-filled structures (cysts, vessels)
            "hypoechoic": (0.05, 0.3),  # Muscle, solid organs
            "isoechoic": (0.3, 0.6),  # Normal tissue reference
            "hyperechoic": (0.6, 0.9),  # Fat, fibrous tissue
            "highly_hyperechoic": (0.9, 1.0),  # Bone, gas, calcifications
        }

        # Ultrasound frequency ranges and their penetration depths
        self.frequency_penetration = {
            "low_freq": {"range": (2, 5), "depth_mm": 200},  # Abdominal imaging
            "mid_freq": {"range": (5, 10), "depth_mm": 100},  # General imaging
            "high_freq": {"range": (10, 15), "depth_mm": 50},  # Superficial structures
            "very_high_freq": {
                "range": (15, 22),
                "depth_mm": 25,
            },  # Dermatology, small parts
        }

    def analyze_ultrasound(
        self,
        image_stack,
        frequency_mhz=7.5,
        depth_mm=100,
        gain_compensation=True,
        is_doppler=False,
    ):
        """
        Analyze an ultrasound image or volume using specialized techniques.

        :param image_stack: Input ultrasound data (2D image or 3D volume)
        :param frequency_mhz: Transducer frequency in MHz
        :param depth_mm: Imaging depth in mm
        :param gain_compensation: Whether to apply time-gain compensation
        :param is_doppler: Whether this is Doppler ultrasound data
        :return: Dictionary containing comprehensive analysis results
        """
        # Convert to numpy array if needed
        if isinstance(image_stack, list):
            if len(image_stack) > 1:
                volume = np.stack(
                    [self.image_analyzer.ij.py.from_java(img) for img in image_stack]
                )
                is_3d = True
            else:
                volume = self.image_analyzer.ij.py.from_java(image_stack[0])
                is_3d = False
        else:
            volume = self.image_analyzer.ij.py.from_java(image_stack)
            is_3d = len(volume.shape) == 3 and volume.shape[0] > 1

        # Ensure proper format (grayscale)
        if len(volume.shape) == 4:
            volume = np.mean(volume, axis=-1)

        # Apply ultrasound-specific preprocessing
        if gain_compensation:
            volume = self.apply_time_gain_compensation(volume, depth_mm)

        # Reduce speckle noise
        despeckled_volume = self.reduce_speckle_noise(volume)

        # Enhance contrast
        enhanced_volume = self.enhance_ultrasound_contrast(despeckled_volume)

        # Classify tissue echogenicity
        echogenicity_map = self.classify_echogenicity(enhanced_volume)

        # Detect and analyze shadows and enhancements
        acoustic_analysis = self.analyze_acoustic_properties(enhanced_volume)

        # Edge detection optimized for ultrasound
        edges = self.detect_ultrasound_edges(enhanced_volume)

        # Detect anatomical structures
        structure_detection = self.detect_anatomical_structures(
            enhanced_volume, echogenicity_map, frequency_mhz
        )

        # Measure distances and areas
        measurements = self.perform_ultrasound_measurements(
             structure_detection
        )

        # Detect abnormalities
        abnormalities = self.detect_ultrasound_abnormalities(
            enhanced_volume, echogenicity_map, structure_detection
        )

        # Blood flow analysis (if Doppler)
        flow_analysis = None
        if is_doppler:
            flow_analysis = self.analyze_doppler_flow(volume)

        # Texture analysis for tissue characterization
        texture_features = self.analyze_ultrasound_texture(enhanced_volume)

        return {
            "original_volume": volume,
            "despeckled_volume": despeckled_volume,
            "enhanced_volume": enhanced_volume,
            "echogenicity_map": echogenicity_map,
            "acoustic_analysis": acoustic_analysis,
            "edges": edges,
            "structure_detection": structure_detection,
            "measurements": measurements,
            "abnormalities": abnormalities,
            "flow_analysis": flow_analysis,
            "texture_features": texture_features,
            "frequency_mhz": frequency_mhz,
            "depth_mm": depth_mm,
            "is_3d": is_3d,
            "is_doppler": is_doppler,
        }

    def apply_time_gain_compensation(self, volume, depth_mm):
        """
        Apply time-gain compensation to correct for attenuation with depth.

        :param volume: Input ultrasound volume
        :param depth_mm: Maximum imaging depth in mm
        :return: TGC-corrected volume
        """
        if len(volume.shape) == 2:
            # 2D image - apply depth-dependent gain
            height = volume.shape[0]
            depth_profile = np.linspace(0, depth_mm, height)

            # Exponential attenuation correction (simplified)
            attenuation_coefficient = 0.5  # dB/cm/MHz (approximate)
            gain_curve = np.exp(depth_profile * attenuation_coefficient / 10)

            corrected = volume * gain_curve[:, np.newaxis]

        else:
            # 3D volume - apply to each slice
            corrected = np.zeros_like(volume)
            for i in range(volume.shape[0]):
                corrected[i] = self.apply_time_gain_compensation(volume[i], depth_mm)

        return np.clip(corrected, 0, np.max(volume))

    def reduce_speckle_noise(self, volume):
        """
        Reduce speckle noise while preserving edges using adaptive filtering.

        :param volume: Input ultrasound volume
        :return: Despeckled volume
        """
        if len(volume.shape) == 2:
            # Apply anisotropic diffusion for speckle reduction
            despeckled = restoration.denoise_tv_chambolle(
                volume, weight=0.1, max_num_iter=100
            )

            # Alternative: Lee filter for speckle
            # Apply median filter with small kernel
            despeckled = ndimage.median_filter(despeckled, size=3)

        else:
            # 3D volume processing
            despeckled = np.zeros_like(volume)
            for i in range(volume.shape[0]):
                despeckled[i] = self.reduce_speckle_noise(volume[i])

        return despeckled

    def enhance_ultrasound_contrast(self, volume):
        """
        Enhance contrast using CLAHE and other techniques.

        :param volume: Input volume
        :return: Enhanced volume
        """
        if len(volume.shape) == 2:
            # Normalize to 0-1 range
            normalized = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # Convert to uint8 for CLAHE
            img_uint8 = (normalized * 255).astype(np.uint8)

            # Simple histogram equalization (CLAHE not available in skimage.exposure)
            # Apply local histogram equalization
            enhanced = filters.rank.enhance_contrast(img_uint8, np.ones((9, 9)))

            # Convert back to float
            enhanced = enhanced.astype(np.float32) / 255.0

        else:
            enhanced = np.zeros_like(volume)
            for i in range(volume.shape[0]):
                enhanced[i] = self.enhance_ultrasound_contrast(volume[i])

        return enhanced

    def classify_echogenicity(self, volume):
        """
        Classify pixels by echogenicity level.

        :param volume: Enhanced ultrasound volume
        :return: Dictionary of echogenicity masks
        """
        if len(volume.shape) == 2:
            echogenicity_map = {}

            # Normalize volume for classification
            normalized = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))

            for echo_type, (min_val, max_val) in self.echogenicity_ranges.items():
                mask = (normalized >= min_val) & (normalized < max_val)
                # Clean up small artifacts
                mask = morphology.remove_small_objects(mask, min_size=20)
                echogenicity_map[echo_type] = mask

        else:
            # 3D processing
            echogenicity_map = {
                echo_type: np.zeros_like(volume, dtype=bool)
                for echo_type in self.echogenicity_ranges.keys()
            }

            for i in range(volume.shape[0]):
                slice_echo = self.classify_echogenicity(volume[i])
                for echo_type, mask in slice_echo.items():
                    echogenicity_map[echo_type][i] = mask

        return echogenicity_map

    def analyze_acoustic_properties(self, volume):
        """
        Analyze acoustic shadows and enhancements.

        :param volume: Enhanced ultrasound volume
        :return: Dictionary of acoustic property analysis
        """
        if len(volume.shape) == 2:
            # Detect acoustic shadows (dark areas behind echogenic structures)
            # Calculate column-wise intensity profiles
            column_profiles = np.mean(volume, axis=1)

            # Find sudden intensity drops that might indicate shadows
            gradient = np.gradient(column_profiles)
            shadow_threshold = -np.std(gradient) * 2
            shadow_regions = gradient < shadow_threshold

            # Detect acoustic enhancement (bright areas behind anechoic structures)
            enhancement_threshold = np.std(gradient) * 2
            enhancement_regions = gradient > enhancement_threshold

            # Create 2D masks
            shadow_mask = np.zeros_like(volume, dtype=bool)
            enhancement_mask = np.zeros_like(volume, dtype=bool)

            for i, has_shadow in enumerate(shadow_regions):
                if has_shadow and i < volume.shape[0]:
                    shadow_mask[i : min(i + 10, volume.shape[0]), :] = True

            for i, has_enhancement in enumerate(enhancement_regions):
                if has_enhancement and i < volume.shape[0]:
                    enhancement_mask[i : min(i + 10, volume.shape[0]), :] = True

            return {
                "acoustic_shadows": shadow_mask,
                "acoustic_enhancement": enhancement_mask,
                "column_profiles": column_profiles,
            }

        else:
            # 3D analysis
            results = {
                "acoustic_shadows": np.zeros_like(volume, dtype=bool),
                "acoustic_enhancement": np.zeros_like(volume, dtype=bool),
                "column_profiles": [],
            }

            for i in range(volume.shape[0]):
                slice_analysis = self.analyze_acoustic_properties(volume[i])
                results["acoustic_shadows"][i] = slice_analysis["acoustic_shadows"]
                results["acoustic_enhancement"][i] = slice_analysis[
                    "acoustic_enhancement"
                ]
                results["column_profiles"].append(slice_analysis["column_profiles"])

            return results

    def detect_ultrasound_edges(self, volume):
        """
        Detect edges optimized for ultrasound imaging characteristics.

        :param volume: Enhanced ultrasound volume
        :return: Edge map
        """
        if len(volume.shape) == 2:
            # Use Canny edge detection with parameters optimized for ultrasound
            edges = feature.canny(
                volume, sigma=1.0, low_threshold=0.1, high_threshold=0.2
            )

        else:
            # 3D edge detection
            edges = np.zeros_like(volume, dtype=bool)
            for i in range(volume.shape[0]):
                edges[i] = self.detect_ultrasound_edges(volume[i])

        return edges

    def detect_anatomical_structures(self, volume, echogenicity_map, frequency_mhz):
        """
        Detect common anatomical structures based on echogenicity patterns.

        :param volume: Enhanced ultrasound volume
        :param echogenicity_map: Echogenicity classification
        :param frequency_mhz: Ultrasound frequency
        :return: Dictionary of detected structures
        """
        structures = {
            "vessels": [],
            "organs": [],
            "cysts": [],
            "masses": [],
            "bones": [],
        }

        if len(volume.shape) == 2:
            # Detect blood vessels (anechoic tubular structures)
            vessel_candidates = echogenicity_map["anechoic"]
            vessel_labels = measure.label(vessel_candidates)

            for region in measure.regionprops(vessel_labels):
                # Filter by shape - vessels tend to be elongated
                if region.eccentricity > 0.7 and region.area > 50:
                    structures["vessels"].append(
                        {
                            "centroid": region.centroid,
                            "area": region.area,
                            "eccentricity": region.eccentricity,
                            "diameter_estimate": np.sqrt(region.area / np.pi) * 2,
                        }
                    )

            # Detect cysts (round anechoic structures)
            for region in measure.regionprops(vessel_labels):
                if region.eccentricity < 0.5 and region.area > 100:
                    structures["cysts"].append(
                        {
                            "centroid": region.centroid,
                            "area": region.area,
                            "diameter_estimate": np.sqrt(region.area / np.pi) * 2,
                        }
                    )

            # Detect hyperechoic structures (potential calcifications, bones)
            hyperechoic_candidates = echogenicity_map["highly_hyperechoic"]
            bone_labels = measure.label(hyperechoic_candidates)

            for region in measure.regionprops(bone_labels):
                if region.area > 30:
                    structures["bones"].append(
                        {"centroid": region.centroid, "area": region.area}
                    )

            # Detect solid masses (mixed echogenicity patterns)
            # Look for regions with heterogeneous echogenicity
            mass_candidates = (
                echogenicity_map["hypoechoic"]
                | echogenicity_map["isoechoic"]
                | echogenicity_map["hyperechoic"]
            )

            mass_labels = measure.label(mass_candidates)
            for region in measure.regionprops(mass_labels):
                if region.area > 200:  # Significant size
                    # Check echogenicity heterogeneity within the region
                    mask = mass_labels == region.label
                    region_intensities = volume[mask]
                    intensity_std = np.std(region_intensities)

                    if intensity_std > 0.1:  # Heterogeneous
                        structures["masses"].append(
                            {
                                "centroid": region.centroid,
                                "area": region.area,
                                "heterogeneity": intensity_std,
                            }
                        )

        else:
            # 3D structure detection
            for i in range(volume.shape[0]):
                slice_echo = {k: v[i] for k, v in echogenicity_map.items()}
                slice_structures = self.detect_anatomical_structures(
                    volume[i], slice_echo, frequency_mhz
                )

                # Aggregate 3D structures
                for structure_type, detections in slice_structures.items():
                    for detection in detections:
                        detection["slice"] = i
                        structures[structure_type].append(detection)

        return structures

    def perform_ultrasound_measurements(self, structure_detection):
        """
        Perform standard ultrasound measurements.

        :param volume: Enhanced ultrasound volume
        :param structure_detection: Detected anatomical structures
        :return: Dictionary of measurements
        """
        measurements = {
            "distances": [],
            "areas": [],
            "volumes": [],
            "vessel_diameters": [],
        }

        # Measure detected vessels
        for vessel in structure_detection["vessels"]:
            measurements["vessel_diameters"].append(
                {
                    "location": vessel["centroid"],
                    "diameter_mm": vessel[
                        "diameter_estimate"
                    ],  # Convert pixels to mm if needed
                    "area_mm2": vessel["area"],
                }
            )

        # Measure cysts and masses
        for cyst in structure_detection["cysts"]:
            measurements["areas"].append(
                {
                    "type": "cyst",
                    "location": cyst["centroid"],
                    "area_mm2": cyst["area"],
                    "diameter_mm": cyst["diameter_estimate"],
                }
            )

        for mass in structure_detection["masses"]:
            measurements["areas"].append(
                {"type": "mass", "location": mass["centroid"], "area_mm2": mass["area"]}
            )

        return measurements

    def detect_ultrasound_abnormalities(
        self, volume, echogenicity_map, structure_detection
    ):
        """
        Detect potential abnormalities in ultrasound images.

        :param volume: Enhanced ultrasound volume
        :param echogenicity_map: Echogenicity classification
        :param structure_detection: Detected anatomical structures
        :return: List of potential abnormalities
        """
        abnormalities = []

        # Check for unusually large cysts
        for cyst in structure_detection["cysts"]:
            if cyst["diameter_estimate"] > 20:  # Large cyst
                abnormalities.append(
                    {
                        "type": "large_cyst",
                        "location": cyst["centroid"],
                        "severity": "moderate",
                        "description": f"Large cyst detected, diameter: {cyst['diameter_estimate']:.1f}mm",
                    }
                )

        # Check for masses with high heterogeneity
        for mass in structure_detection["masses"]:
            if mass.get("heterogeneity", 0) > 0.2:
                abnormalities.append(
                    {
                        "type": "heterogeneous_mass",
                        "location": mass["centroid"],
                        "severity": "high",
                        "description": "Highly heterogeneous mass detected",
                    }
                )

        # Check for abnormal acoustic patterns
        if len(volume.shape) == 2:
            # Look for regions with unusual echogenicity patterns
            total_pixels = volume.size
            anechoic_ratio = np.sum(echogenicity_map["anechoic"]) / total_pixels

            if anechoic_ratio > 0.3:  # Too much anechoic tissue
                abnormalities.append(
                    {
                        "type": "excessive_anechoic_regions",
                        "location": "global",
                        "severity": "moderate",
                        "description": f"High proportion of anechoic tissue: {anechoic_ratio:.2%}",
                    }
                )

        return abnormalities

    def analyze_doppler_flow(self, volume):
        """
        Analyze Doppler flow patterns for blood flow assessment.

        :param volume: Doppler ultrasound volume
        :return: Flow analysis results
        """
        if len(volume.shape) < 3:
            return {"error": "Doppler analysis requires temporal data"}

        # Calculate temporal differences to detect flow
        temporal_diff = np.diff(volume, axis=0)
        flow_magnitude = np.mean(np.abs(temporal_diff), axis=0)

        # Detect high flow regions
        flow_threshold = np.percentile(flow_magnitude, 90)
        high_flow_regions = flow_magnitude > flow_threshold

        # Label flow regions
        flow_labels = measure.label(high_flow_regions)

        flow_regions = []
        for region in measure.regionprops(flow_labels):
            if region.area > 20:
                flow_regions.append(
                    {
                        "centroid": region.centroid,
                        "area": region.area,
                        "mean_flow": np.mean(
                            flow_magnitude[flow_labels == region.label]
                        ),
                    }
                )

        return {
            "flow_magnitude": flow_magnitude,
            "flow_regions": flow_regions,
            "mean_flow_velocity": np.mean(flow_magnitude),
            "max_flow_velocity": np.max(flow_magnitude),
        }

    def analyze_ultrasound_texture(self, volume):
        """
        Analyze texture features for tissue characterization.

        :param volume: Enhanced ultrasound volume
        :return: Texture feature analysis
        """
        if len(volume.shape) == 2:
            # Calculate Gray-Level Co-occurrence Matrix features
            # This is a simplified version - full implementation would use skimage.feature.greycomatrix

            # Calculate local statistics
            mean_filter = ndimage.uniform_filter(volume, size=5)
            variance = ndimage.uniform_filter(volume**2, size=5) - mean_filter**2

            # Calculate local entropy (simplified)
            entropy_filter = ndimage.generic_filter(
                volume, lambda x: -np.sum(x * np.log(x + 1e-10)), size=5
            )

            return {
                "local_mean": mean_filter,
                "local_variance": variance,
                "local_entropy": entropy_filter,
                "global_mean": np.mean(volume),
                "global_variance": np.var(volume),
                "global_entropy": -np.sum(volume * np.log(volume + 1e-10)),
            }

        else:
            # 3D texture analysis
            texture_features = []
            for i in range(volume.shape[0]):
                slice_texture = self.analyze_ultrasound_texture(volume[i])
                texture_features.append(slice_texture)

            return {
                "slice_features": texture_features,
                "mean_texture_variance": np.mean(
                    [tf["global_variance"] for tf in texture_features]
                ),
            }

    def visualize_ultrasound_analysis(self, analysis_results, slice_index=None):
        """
        Visualize ultrasound analysis results.

        :param analysis_results: Results from analyze_ultrasound method
        :param slice_index: Index of slice to visualize (None for 2D or middle slice)
        """
        import matplotlib.pyplot as plt

        is_3d = analysis_results["is_3d"]

        if is_3d and slice_index is None:
            slice_index = analysis_results["original_volume"].shape[0] // 2
        elif not is_3d:
            slice_index = 0

        # Get 2D slices for visualization
        if is_3d:
            original = analysis_results["original_volume"][slice_index]
            enhanced = analysis_results["enhanced_volume"][slice_index]
            edges = analysis_results["edges"][slice_index]
        else:
            original = analysis_results["original_volume"]
            enhanced = analysis_results["enhanced_volume"]
            edges = analysis_results["edges"]

        fig, axs = plt.subplots(2, 4, figsize=(20, 10))

        # Original image
        axs[0, 0].imshow(original, cmap="gray")
        axs[0, 0].set_title("Original Ultrasound")

        # Enhanced image
        axs[0, 1].imshow(enhanced, cmap="gray")
        axs[0, 1].set_title("Enhanced (Despeckled)")

        # Echogenicity map
        echo_overlay = np.zeros((*original.shape, 3))
        colors = [(0, 0, 1), (0, 0.5, 1), (0.5, 0.5, 0.5), (1, 1, 0), (1, 0, 0)]

        for i, (echo_type, mask) in enumerate(
            analysis_results["echogenicity_map"].items()
        ):
            if i < len(colors):
                if is_3d:
                    echo_slice = mask[slice_index]
                else:
                    echo_slice = mask
                for c in range(3):
                    echo_overlay[:, :, c] += echo_slice * colors[i][c]

        axs[0, 2].imshow(echo_overlay)
        axs[0, 2].set_title("Echogenicity Classification")

        # Edge detection
        axs[0, 3].imshow(edges, cmap="gray")
        axs[0, 3].set_title("Edge Detection")

        # Acoustic shadows and enhancement
        acoustic = analysis_results["acoustic_analysis"]
        if is_3d:
            shadows = acoustic["acoustic_shadows"][slice_index]
            enhancement = acoustic["acoustic_enhancement"][slice_index]
        else:
            shadows = acoustic["acoustic_shadows"]
            enhancement = acoustic["acoustic_enhancement"]

        acoustic_overlay = np.zeros_like(original)
        acoustic_overlay[shadows] = 0.3
        acoustic_overlay[enhancement] = 0.8

        axs[1, 0].imshow(acoustic_overlay, cmap="RdBu")
        axs[1, 0].set_title("Acoustic Properties")

        # Structure detection overlay
        structure_overlay = original.copy()
        structures = analysis_results["structure_detection"]

        # Mark detected structures
        for vessel in structures["vessels"]:
            if not is_3d or vessel.get("slice", 0) == slice_index:
                y, x = vessel["centroid"]
                if (
                    0 <= int(y) < structure_overlay.shape[0]
                    and 0 <= int(x) < structure_overlay.shape[1]
                ):
                    structure_overlay[int(y), int(x)] = np.max(structure_overlay)

        axs[1, 1].imshow(structure_overlay, cmap="hot")
        axs[1, 1].set_title("Detected Structures")

        # Measurements bar chart
        measurements = analysis_results["measurements"]
        vessel_diameters = [v["diameter_mm"] for v in measurements["vessel_diameters"]]

        if vessel_diameters:
            axs[1, 2].bar(range(len(vessel_diameters)), vessel_diameters)
            axs[1, 2].set_title("Vessel Diameters (mm)")
            axs[1, 2].set_ylabel("Diameter (mm)")
        else:
            axs[1, 2].text(0.5, 0.5, "No vessels detected", ha="center", va="center")
            axs[1, 2].set_title("Vessel Measurements")

        # Abnormalities summary
        abnormalities = analysis_results["abnormalities"]
        abnormality_text = f"Abnormalities found: {len(abnormalities)}\n"

        for i, abn in enumerate(abnormalities[:5]):  # Show first 5
            abnormality_text += f"{i+1}. {abn['type']}: {abn['severity']}\n"

        axs[1, 3].text(
            0.05,
            0.95,
            abnormality_text,
            transform=axs[1, 3].transAxes,
            verticalalignment="top",
            fontsize=10,
        )
        axs[1, 3].set_title("Detected Abnormalities")

        for ax in axs.flat[:-2]:  # All except text plots
            ax.axis("off")

        # Remove axes for text plots
        axs[1, 2].set_xticks([])
        axs[1, 3].set_xticks([])
        axs[1, 3].set_yticks([])

        plt.tight_layout()
        plt.show()

    def create_tissue_from_ultrasound(
        self,
        volume,
        echogenicity_map,
        structure_detection,
        tissue_type="muscle",
        tissue_name="UltrasoundTissue",
    ):
        """
        Create tissue objects from ultrasound analysis results.

        :param volume: Enhanced ultrasound volume
        :param echogenicity_map: Echogenicity classification
        :param structure_detection: Detected structures
        :param tissue_type: Type of tissue to create ("muscle", "organ")
        :param tissue_name: Name for the tissue
        :return: Tissue object
        """
        # Calculate tissue characteristics from ultrasound data
        if len(volume.shape) == 2:
            tissue_volume = volume.size
        else:
            tissue_volume = volume.size

        # Analyze echogenicity distribution for tissue health
        total_pixels = volume.size
        hypoechoic_ratio = np.sum(echogenicity_map["hypoechoic"]) / total_pixels

        # Create cells based on tissue characteristics
        num_cells = max(1, int(tissue_volume / 5000))  # One cell per 5k pixels
        cells = []

        for i in range(num_cells):
            # Health based on echogenicity patterns
            if tissue_type == "muscle":
                # Muscle should be primarily hypoechoic
                if 0.6 <= hypoechoic_ratio <= 0.8:
                    health = random.uniform(85, 95)
                elif 0.4 <= hypoechoic_ratio <= 0.9:
                    health = random.uniform(75, 90)
                else:
                    health = random.uniform(60, 80)
            else:
                # General tissue health assessment
                normal_echo_ratio = echogenicity_map["isoechoic"].sum() / total_pixels
                if normal_echo_ratio > 0.5:
                    health = random.uniform(80, 95)
                else:
                    health = random.uniform(70, 85)

            cells.append(Cell(f"{tissue_type.capitalize()}Cell_{i}", str(health)))

        # Calculate additional tissue properties
        intensity_variance = np.var(volume)

        # Assess vascularization from detected vessels
        vessel_density = len(structure_detection["vessels"]) / (tissue_volume / 10000)

        if tissue_type == "muscle":
            # Create muscle tissue
            # Muscle contractility based on echogenicity homogeneity
            contractility = max(0.1, 1.0 - intensity_variance)

            tissue = MuscleTissue(
                name=tissue_name,
                cells=cells,
            )

            # Set additional properties
            tissue.contraction_rate = contractility

        else:
            # Create organ tissue
            # Organ function based on echogenicity normality
            organ_function = 1.0 - (abs(0.5 - normal_echo_ratio) * 2)
            organ_function = max(0.3, min(1.0, organ_function))

            # Metabolic rate from vascular density
            metabolic_rate = min(1.0, vessel_density * 0.5 + 0.3)

            tissue = OrganTissue(
                name=tissue_name,
                cells=cells,
                organ_type="generic",
                organ_function=organ_function,
                metabolic_rate=metabolic_rate,
            )

            # Set perfusion based on detected vessels
            tissue.perfusion_rate = min(1.0, vessel_density * 0.3 + 0.2)

        return tissue

    def perform_real_time_analysis(self, image_stream, analysis_params=None):
        """
        Perform real-time ultrasound analysis on a stream of images.

        :param image_stream: Generator or iterator of ultrasound images
        :param analysis_params: Dictionary of analysis parameters
        :return: Generator of real-time analysis results
        """
        if analysis_params is None:
            analysis_params = {
                "frequency_mhz": 7.5,
                "depth_mm": 100,
                "track_movement": True,
                "detect_changes": True,
            }

        previous_frame = None
        frame_count = 0

        for frame in image_stream:
            frame_count += 1

            # Convert frame if needed
            if hasattr(frame, "shape"):
                current_frame = frame
            else:
                current_frame = self.image_analyzer.ij.py.from_java(frame)

            # Quick analysis for real-time performance
            quick_results = self.quick_ultrasound_analysis(
                current_frame,
            )

            # Motion detection if enabled
            motion_info = None
            if analysis_params.get("track_movement") and previous_frame is not None:
                motion_info = self.detect_motion(previous_frame, current_frame)

            # Change detection
            change_info = None
            if analysis_params.get("detect_changes") and previous_frame is not None:
                change_info = self.detect_structural_changes(
                    previous_frame, current_frame
                )

            yield {
                "frame_number": frame_count,
                "quick_analysis": quick_results,
                "motion_info": motion_info,
                "change_info": change_info,
                "timestamp": frame_count * 0.033,  # Assuming 30 FPS
            }

            previous_frame = current_frame.copy()

    def quick_ultrasound_analysis(self, frame):
        """
        Perform quick analysis suitable for real-time processing.

        :param frame: Single ultrasound frame
        :param frequency_mhz: Ultrasound frequency
        :param depth_mm: Imaging depth
        :return: Quick analysis results
        """
        # Fast speckle reduction
        despeckled = ndimage.median_filter(frame, size=3)

        # Quick echogenicity classification
        normalized = (despeckled - np.min(despeckled)) / (
            np.max(despeckled) - np.min(despeckled)
        )

        anechoic_count = np.sum(normalized < 0.2)
        hypoechoic_count = np.sum((normalized >= 0.2) & (normalized < 0.5))
        hyperechoic_count = np.sum(normalized >= 0.7)

        # Quick structure detection
        # Find large anechoic regions (potential vessels/cysts)
        anechoic_mask = normalized < 0.2
        anechoic_regions = measure.label(anechoic_mask)
        large_anechoic = []

        for region in measure.regionprops(anechoic_regions):
            if region.area > 50:
                large_anechoic.append(
                    {"centroid": region.centroid, "area": region.area}
                )

        return {
            "mean_intensity": np.mean(normalized),
            "intensity_std": np.std(normalized),
            "anechoic_ratio": anechoic_count / frame.size,
            "hypoechoic_ratio": hypoechoic_count / frame.size,
            "hyperechoic_ratio": hyperechoic_count / frame.size,
            "large_anechoic_regions": large_anechoic,
            "frame_quality": self.assess_image_quality(frame),
        }

    def detect_motion(self, previous_frame, current_frame):
        """
        Detect motion between consecutive ultrasound frames.

        :param previous_frame: Previous ultrasound frame
        :param current_frame: Current ultrasound frame
        :return: Motion detection results
        """
        # Calculate frame difference
        frame_diff = np.abs(
            current_frame.astype(np.float32) - previous_frame.astype(np.float32)
        )

        # Threshold for motion detection
        motion_threshold = np.mean(frame_diff) + 2 * np.std(frame_diff)
        motion_mask = frame_diff > motion_threshold

        # Calculate motion statistics
        motion_pixels = np.sum(motion_mask)
        motion_percentage = motion_pixels / frame_diff.size

        # Find motion centers
        motion_regions = measure.label(motion_mask)
        motion_centers = []

        for region in measure.regionprops(motion_regions):
            if region.area > 20:
                motion_centers.append(
                    {
                        "centroid": region.centroid,
                        "area": region.area,
                        "intensity": np.mean(
                            frame_diff[motion_regions == region.label]
                        ),
                    }
                )

        return {
            "motion_percentage": motion_percentage,
            "motion_intensity": (
                np.mean(frame_diff[motion_mask]) if motion_pixels > 0 else 0
            ),
            "motion_centers": motion_centers,
            "overall_displacement": np.mean(frame_diff),
        }

    def detect_structural_changes(self, previous_frame, current_frame):
        """
        Detect structural changes between frames.

        :param previous_frame: Previous ultrasound frame
        :param current_frame: Current ultrasound frame
        :return: Structural change analysis
        """
        # Smooth both frames to focus on structural changes
        prev_smooth = ndimage.gaussian_filter(previous_frame, sigma=2)
        curr_smooth = ndimage.gaussian_filter(current_frame, sigma=2)

        # Calculate structural similarity
        diff = np.abs(prev_smooth - curr_smooth)
        structural_change_score = np.mean(diff) / (np.mean(prev_smooth) + 1e-6)

        # Detect new structures (bright regions in current that weren't in previous)
        new_structures = curr_smooth > prev_smooth + np.std(prev_smooth)
        disappeared_structures = prev_smooth > curr_smooth + np.std(curr_smooth)

        return {
            "structural_change_score": structural_change_score,
            "new_structure_pixels": np.sum(new_structures),
            "disappeared_structure_pixels": np.sum(disappeared_structures),
            "stability_index": 1.0 - min(1.0, structural_change_score),
        }

    def assess_image_quality(self, frame):
        """
        Assess the quality of an ultrasound image.

        :param frame: Ultrasound frame
        :return: Quality metrics
        """
        # Calculate image sharpness using Laplacian variance
        laplacian = ndimage.laplace(frame.astype(np.float32))
        sharpness = np.var(laplacian)

        # Calculate contrast using standard deviation
        contrast = np.std(frame)

        # Calculate signal-to-noise ratio estimate
        # Use the ratio of signal variance to noise variance estimate
        signal_power = np.var(frame)
        # Estimate noise from high-frequency components
        high_freq = ndimage.gaussian_filter(frame, sigma=0.5) - frame
        noise_power = np.var(high_freq)
        snr = signal_power / (noise_power + 1e-6)

        # Overall quality score (0-1)
        # Normalize metrics and combine
        sharpness_norm = min(1.0, sharpness / 1000)  # Adjust scaling as needed
        contrast_norm = min(1.0, contrast / 100)  # Adjust scaling as needed
        snr_norm = min(1.0, snr / 50)  # Adjust scaling as needed

        quality_score = (sharpness_norm + contrast_norm + snr_norm) / 3

        return {
            "sharpness": sharpness,
            "contrast": contrast,
            "snr": snr,
            "overall_quality": quality_score,
            "quality_grade": (
                "excellent"
                if quality_score > 0.8
                else (
                    "good"
                    if quality_score > 0.6
                    else "fair" if quality_score > 0.4 else "poor"
                )
            ),
        }

    def calibrate_measurements(self, pixel_size_mm=None, depth_calibration=None):
        """
        Calibrate pixel measurements to physical units.

        :param pixel_size_mm: Size of one pixel in mm
        :param depth_calibration: Depth calibration parameters
        :return: Calibration parameters
        """
        if pixel_size_mm is None:
            # Default calibration based on typical ultrasound settings
            pixel_size_mm = 0.1  # 0.1mm per pixel

        if depth_calibration is None:
            depth_calibration = {
                "pixels_per_mm": 10,  # 10 pixels per mm depth
                "time_gain_curve": lambda depth: 1.0 + 0.1 * depth,  # Simple TGC
            }

        self.calibration = {
            "pixel_size_mm": pixel_size_mm,
            "depth_calibration": depth_calibration,
        }

        return self.calibration

    def export_measurements_to_dicom(self, analysis_results, patient_info=None):
        """
        Export measurements in DICOM-like format.

        :param analysis_results: Results from ultrasound analysis
        :param patient_info: Patient information dictionary
        :return: Dictionary with DICOM-like measurement data
        """
        measurements = analysis_results["measurements"]

        dicom_data = {
            "StudyInstanceUID": f"1.2.3.4.5.{random.randint(100000, 999999)}",
            "SeriesInstanceUID": f"1.2.3.4.6.{random.randint(100000, 999999)}",
            "SOPInstanceUID": f"1.2.3.4.7.{random.randint(100000, 999999)}",
            "StudyDate": "20250822",  # Current date
            "StudyTime": "120000",
            "Modality": "US",
            "Manufacturer": "BioBridge Ultrasound Analyzer",
            "PatientInfo": patient_info or {},
            "ImageType": ["ORIGINAL", "PRIMARY", "OTHER"],
            "TransducerFrequency": analysis_results.get("frequency_mhz", 7.5),
            "DepthOfScanField": analysis_results.get("depth_mm", 100),
            "Measurements": {
                "VesselDiameters": measurements.get("vessel_diameters", []),
                "Areas": measurements.get("areas", []),
                "Distances": measurements.get("distances", []),
                "Volumes": measurements.get("volumes", []),
            },
            "DetectedStructures": analysis_results["structure_detection"],
            "Abnormalities": analysis_results["abnormalities"],
            "QualityMetrics": analysis_results.get("quality_metrics", {}),
        }

        return dicom_data
