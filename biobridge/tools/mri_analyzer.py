import random

import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage import gaussian_filter, label
from skimage import filters, measure, morphology
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from biobridge.blocks.cell import Cell
from biobridge.definitions.tissues.radiation_affected import RadiationAffectedTissue


class MRIAnalyzer:
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer
        self.atlas_templates = self._initialize_brain_atlas()
        self.connectivity_matrix = None
        self.cortical_thickness_map = None

    def _initialize_brain_atlas(self):
        return {
            'brodmann_areas': {
                1: 'Primary_Somatosensory_Cortex',
                2: 'Secondary_Somatosensory_Cortex', 
                3: 'Primary_Somatosensory_Cortex_3',
                4: 'Primary_Motor_Cortex',
                5: 'Somatosensory_Association_Cortex',
                6: 'Premotor_Cortex',
                7: 'Superior_Parietal_Lobule',
                8: 'Frontal_Eye_Fields',
                9: 'Dorsolateral_Prefrontal_Cortex',
                10: 'Anterior_Prefrontal_Cortex',
                17: 'Primary_Visual_Cortex',
                18: 'Secondary_Visual_Cortex',
                39: 'Angular_Gyrus',
                40: 'Supramarginal_Gyrus',
                41: 'Primary_Auditory_Cortex',
                42: 'Secondary_Auditory_Cortex',
                44: 'Brocas_Area_Pars_Opercularis',
                45: 'Brocas_Area_Pars_Triangularis',
                46: 'Dorsolateral_Prefrontal_Cortex_46'
            },
            'subcortical_structures': [
                'Thalamus', 'Caudate', 'Putamen', 'Globus_Pallidus',
                'Hippocampus', 'Amygdala', 'Brainstem', 'Cerebellum'
            ]
        }

    def analyze_mri(self, image, sequence_type="T1"):
        img_array = self.image_analyzer.ij.py.from_java(image)

        if len(img_array.shape) > 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        bias_corrected_img = self.correct_bias_field(img_array)
        denoised_img = self.reduce_noise(bias_corrected_img)
        enhanced_img = self.enhance_contrast(denoised_img, sequence_type)
        segmented = self.segment_anatomical_structures(enhanced_img, sequence_type)
        lesions = self.detect_lesions(enhanced_img, sequence_type)
        tissue_properties = self.measure_tissue_properties(enhanced_img, segmented, sequence_type)
        texture_features = self.extract_texture_features(enhanced_img)
        brain_regions = self.detect_brain_regions(enhanced_img)

        return {
            "bias_corrected_image": bias_corrected_img,
            "denoised_image": denoised_img,
            "enhanced_image": enhanced_img,
            "segmented_image": segmented,
            "lesions": lesions,
            "tissue_properties": tissue_properties,
            "texture_features": texture_features,
            "brain_regions": brain_regions,
            "sequence_type": sequence_type,
        }

    def correct_bias_field(self, image):
        bias_field = cv2.GaussianBlur(image.astype(np.float32), (61, 61), 0)
        bias_field[bias_field == 0] = 1
        corrected = (image.astype(np.float32) / bias_field) * np.mean(bias_field)
        return np.clip(corrected, 0, 255).astype(np.uint8)

    def reduce_noise(self, image):
        return cv2.fastNlMeansDenoising(image, None, h=8, searchWindowSize=21, templateWindowSize=7)

    def enhance_contrast(self, image, sequence_type):
        if sequence_type in ["T1", "T1_contrast"]:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            return clahe.apply(image.astype(np.uint8))
        elif sequence_type in ["T2", "FLAIR"]:
            gamma = 0.8
            corrected = np.power(image / 255.0, gamma)
            return (corrected * 255).astype(np.uint8)
        elif sequence_type == "DWI":
            return cv2.addWeighted(image, 0.8, cv2.Laplacian(image, cv2.CV_8U), 0.2, 0)
        else:
            clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
            return clahe.apply(image.astype(np.uint8))

    def segment_anatomical_structures(self, image, sequence_type):
        if sequence_type in ["T1", "T1_contrast"]:
            n_clusters = 6
        elif sequence_type in ["T2", "FLAIR"]:
            n_clusters = 5
        else:
            n_clusters = 4

        pixel_values = image.reshape((-1, 1)).astype(np.float32)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pixel_values)
        segmented_image = labels.reshape(image.shape).astype(np.uint8)
        
        kernel = np.ones((3, 3), np.uint8)
        segmented_image = cv2.morphologyEx(segmented_image, cv2.MORPH_CLOSE, kernel)
        segmented_image = cv2.morphologyEx(segmented_image, cv2.MORPH_OPEN, kernel)

        return segmented_image * (255 // n_clusters)

    def detect_lesions(self, image, sequence_type):
        lesions = []

        if sequence_type in ["FLAIR", "T2"]:
            threshold = filters.threshold_otsu(image) * 1.3
            binary_lesions = image > threshold
        elif sequence_type == "T1_contrast":
            threshold = filters.threshold_otsu(image) * 1.5
            binary_lesions = image > threshold
        else:
            binary_lesions = (
                cv2.adaptiveThreshold(
                    image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5
                )
                > 0
            )

        binary_lesions = morphology.remove_small_objects(binary_lesions, min_size=10)
        binary_lesions = ndimage.binary_fill_holes(binary_lesions)
        labeled_lesions = measure.label(binary_lesions)
        lesion_props = measure.regionprops(labeled_lesions, image)

        for prop in lesion_props:
            if prop.area > 5:
                lesions.append(
                    {
                        "centroid": prop.centroid,
                        "area": prop.area,
                        "mean_intensity": prop.mean_intensity,
                        "max_intensity": prop.max_intensity,
                        "eccentricity": prop.eccentricity,
                        "solidity": prop.solidity,
                        "bbox": prop.bbox,
                    }
                )

        return lesions

    def measure_tissue_properties(self, image, segmented, sequence_type):
        properties = {}
        unique_labels = np.unique(segmented)

        for label in unique_labels:
            if label == 0:
                continue

            mask = segmented == label
            tissue_pixels = image[mask]

            if len(tissue_pixels) > 0:
                tissue_name = self._get_tissue_name(label, sequence_type)
                properties[tissue_name] = {
                    "mean_intensity": float(np.mean(tissue_pixels)),
                    "std_intensity": float(np.std(tissue_pixels)),
                    "volume_pixels": int(np.sum(mask)),
                    "intensity_range": (
                        int(np.min(tissue_pixels)),
                        int(np.max(tissue_pixels)),
                    ),
                    "signal_to_noise": float(
                        np.mean(tissue_pixels) / (np.std(tissue_pixels) + 1e-6)
                    ),
                }

        return properties

    def _get_tissue_name(self, label, sequence_type):
        tissue_maps = {
            "T1": {
                1: "CSF",
                2: "Gray_Matter",
                3: "White_Matter",
                4: "Skull",
                5: "Vessels",
                6: "Background",
            },
            "T2": {
                1: "CSF",
                2: "Gray_Matter",
                3: "White_Matter",
                4: "Edema",
                5: "Background",
            },
            "FLAIR": {
                1: "Gray_Matter",
                2: "White_Matter",
                3: "Lesions",
                4: "CSF_Suppressed",
                5: "Background",
            },
        }

        tissue_map = tissue_maps.get(
            sequence_type, {1: "Tissue_1", 2: "Tissue_2", 3: "Tissue_3", 4: "Tissue_4"}
        )
        return tissue_map.get(label, f"Unknown_Tissue_{label}")

    def extract_texture_features(self, image):
        grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        lbp_like = np.zeros_like(image, dtype=np.uint8)
        for i in range(1, image.shape[0] - 1):
            for j in range(1, image.shape[1] - 1):
                center = image[i, j]
                pattern = 0
                pattern |= (image[i - 1, j - 1] > center) << 7
                pattern |= (image[i - 1, j] > center) << 6
                pattern |= (image[i - 1, j + 1] > center) << 5
                pattern |= (image[i, j + 1] > center) << 4
                pattern |= (image[i + 1, j + 1] > center) << 3
                pattern |= (image[i + 1, j] > center) << 2
                pattern |= (image[i + 1, j - 1] > center) << 1
                pattern |= (image[i, j - 1] > center) << 0
                lbp_like[i, j] = pattern

        return {
            "mean_gradient_magnitude": float(np.mean(gradient_magnitude)),
            "gradient_variance": float(np.var(gradient_magnitude)),
            "lbp_uniformity": float(len(np.unique(lbp_like)) / 256.0),
            "contrast": float(np.std(image)),
            "homogeneity": float(1.0 / (1.0 + np.var(image))),
            "entropy": float(
                -np.sum(
                    np.histogram(image, bins=256)[0]
                    * np.log2(np.histogram(image, bins=256)[0] + 1e-10)
                )
            ),
        }

    def detect_brain_regions(self, image):
        brain_mask = self._extract_brain_mask(image)
        brain_image = image * brain_mask
        
        enhanced_regions = self._perform_brain_segmentation(brain_image)
        cortical_analysis = self._analyze_cortical_structure(brain_image, brain_mask)
        subcortical_analysis = self._segment_subcortical_structures(brain_image, brain_mask)
        connectivity_analysis = self._analyze_brain_connectivity(brain_image, brain_mask)
        morphometric_analysis = self._compute_brain_morphometry(brain_image, brain_mask)
        
        comprehensive_regions = {
            **enhanced_regions,
            'cortical_analysis': cortical_analysis,
            'subcortical_structures': subcortical_analysis,
            'connectivity_metrics': connectivity_analysis,
            'morphometric_features': morphometric_analysis
        }
        
        return comprehensive_regions

    def _perform_brain_segmentation(self, brain_image):
        gradient_image = np.sqrt(
            cv2.Sobel(brain_image, cv2.CV_64F, 1, 0, ksize=3)**2 + 
            cv2.Sobel(brain_image, cv2.CV_64F, 0, 1, ksize=3)**2
        )
        
        markers = np.zeros_like(brain_image, dtype=np.int32)
        markers[brain_image < filters.threshold_otsu(brain_image) * 0.3] = 1
        markers[brain_image > filters.threshold_otsu(brain_image) * 1.4] = 2
        
        multi_scale_features = self._extract_multiscale_features(brain_image)
        
        feature_vector = np.column_stack([
            brain_image.flatten(),
            gradient_image.flatten(),
            multi_scale_features['scale_1'].flatten(),
            multi_scale_features['scale_2'].flatten(),
            multi_scale_features['scale_3'].flatten()
        ])
        
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(feature_vector)
        
        clustering = KMeans(n_clusters=8, random_state=42, n_init=15)
        cluster_labels = clustering.fit_predict(normalized_features)
        segmentation = cluster_labels.reshape(brain_image.shape)
        
        refined_regions = self._refine_segmentation_with_morphology(segmentation)
        
        return self._map_clusters_to_anatomical_regions(refined_regions, brain_image)

    def _extract_multiscale_features(self, image):
        sigma_values = [1.0, 2.0, 4.0]
        features = {}
        
        for i, sigma in enumerate(sigma_values, 1):
            smoothed = gaussian_filter(image.astype(np.float32), sigma=sigma)
            laplacian = cv2.Laplacian(smoothed.astype(np.uint8), cv2.CV_64F)
            features[f'scale_{i}'] = laplacian
            
        return features

    def _refine_segmentation_with_morphology(self, segmentation):
        refined = segmentation.copy()
        
        for label_val in np.unique(segmentation):
            if label_val == 0:
                continue
                
            mask = (segmentation == label_val).astype(np.uint8)
            
            kernel_size = max(3, int(np.sqrt(np.sum(mask)) / 20))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            refined[mask > 0] = label_val
            
        return refined

    def _analyze_cortical_structure(self, brain_image, brain_mask):
        cortical_regions = self._segment_cortical_areas(brain_image, brain_mask)
        thickness_map = self._compute_cortical_thickness(brain_image, brain_mask)
        curvature_analysis = self._analyze_cortical_curvature(brain_image, brain_mask)
        surface_area = self._estimate_cortical_surface_area(brain_mask)
        
        gyral_sulcal_analysis = self._analyze_gyral_sulcal_pattern(brain_image, brain_mask)
        
        return {
            'cortical_regions': cortical_regions,
            'cortical_thickness': {
                'mean_thickness': float(np.mean(thickness_map[thickness_map > 0])),
                'std_thickness': float(np.std(thickness_map[thickness_map > 0])),
                'thickness_map': thickness_map
            },
            'curvature_metrics': curvature_analysis,
            'surface_area_estimate': surface_area,
            'gyral_sulcal_patterns': gyral_sulcal_analysis
        }

    def _segment_cortical_areas(self, brain_image, brain_mask):
        brain_center = np.array([brain_mask.shape[0] // 2, brain_mask.shape[1] // 2])
        
        cortical_regions = {}
        
        for angle in range(0, 360, 30):
            radians = np.radians(angle)
            
            region_mask = self._create_sectorial_mask(brain_mask, brain_center, angle, 30)
            region_data = brain_image[region_mask]
            
            if len(region_data) > 100:
                region_name = f"cortical_sector_{angle}"
                cortical_regions[region_name] = {
                    'mean_intensity': float(np.mean(region_data)),
                    'volume': int(np.sum(region_mask)),
                    'intensity_variance': float(np.var(region_data)),
                    'sector_angle': angle
                }
                
        return cortical_regions

    def _create_sectorial_mask(self, brain_mask, center, angle, sector_width):
        y, x = np.ogrid[:brain_mask.shape[0], :brain_mask.shape[1]]
        
        dx = x - center[1]
        dy = y - center[0]
        
        angles = np.arctan2(dy, dx) * 180 / np.pi
        angles = (angles + 360) % 360
        
        start_angle = (angle - sector_width // 2) % 360
        end_angle = (angle + sector_width // 2) % 360
        
        if start_angle < end_angle:
            sector_mask = (angles >= start_angle) & (angles <= end_angle)
        else:
            sector_mask = (angles >= start_angle) | (angles <= end_angle)
            
        return brain_mask & sector_mask

    def _compute_cortical_thickness(self, brain_image, brain_mask):
        distance_transform = ndimage.distance_transform_edt(brain_mask)
        
        thickness_estimate = np.zeros_like(brain_image, dtype=np.float32)
        
        for i in range(1, brain_mask.shape[0] - 1):
            for j in range(1, brain_mask.shape[1] - 1):
                if brain_mask[i, j]:
                    local_region = distance_transform[i-1:i+2, j-1:j+2]
                    thickness_estimate[i, j] = np.mean(local_region) * 2
                    
        self.cortical_thickness_map = thickness_estimate
        return thickness_estimate

    def _analyze_cortical_curvature(self, brain_image, brain_mask):
        smoothed = gaussian_filter(brain_image.astype(np.float32), sigma=2.0)
        
        grad_x = cv2.Sobel(smoothed, cv2.CV_64F, 1, 0, ksize=5)
        grad_y = cv2.Sobel(smoothed, cv2.CV_64F, 0, 1, ksize=5)
        
        grad_xx = cv2.Sobel(grad_x, cv2.CV_64F, 1, 0, ksize=3)
        grad_yy = cv2.Sobel(grad_y, cv2.CV_64F, 0, 1, ksize=3)
        
        curvature = np.abs(grad_xx + grad_yy)
        
        gyral_mask = curvature > np.percentile(curvature[brain_mask], 75)
        sulcal_mask = curvature < np.percentile(curvature[brain_mask], 25)
        
        return {
            'mean_curvature': float(np.mean(curvature[brain_mask])),
            'curvature_variance': float(np.var(curvature[brain_mask])),
            'gyral_volume': int(np.sum(gyral_mask & brain_mask)),
            'sulcal_volume': int(np.sum(sulcal_mask & brain_mask)),
            'curvature_map': curvature
        }

    def _estimate_cortical_surface_area(self, brain_mask):
        contours, _ = cv2.findContours(brain_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            perimeter = cv2.arcLength(contours[0], True)
            area = cv2.contourArea(contours[0])
            
            fractal_dimension = self._compute_fractal_dimension(contours[0])
            
            return {
                'perimeter': float(perimeter),
                'area': float(area),
                'surface_complexity': float(perimeter / (2 * np.sqrt(np.pi * area))),
                'fractal_dimension': fractal_dimension
            }
        return {'perimeter': 0.0, 'area': 0.0, 'surface_complexity': 0.0, 'fractal_dimension': 1.0}

    def _compute_fractal_dimension(self, contour):
        if len(contour) < 4:
            return 1.0
            
        scales = np.logspace(0.5, 2, num=10)
        lengths = []
        
        for scale in scales:
            simplified = cv2.approxPolyDP(contour, scale, True)
            length = cv2.arcLength(simplified, True)
            lengths.append(length)
            
        log_scales = np.log(scales)
        log_lengths = np.log(lengths)
        
        if len(log_scales) > 1 and np.std(log_scales) > 0:
            slope = np.polyfit(log_scales, log_lengths, 1)[0]
            return max(1.0, min(2.0, 1 - slope))
        return 1.0

    def _analyze_gyral_sulcal_pattern(self, brain_image, brain_mask):
        smoothed = gaussian_filter(brain_image.astype(np.float32), sigma=3.0)
    
        laplacian = cv2.Laplacian(smoothed, cv2.CV_64F, ksize=5)
    
        gyral_candidates = (laplacian < -np.std(laplacian)) & brain_mask
        sulcal_candidates = (laplacian > np.std(laplacian)) & brain_mask
    
        gyral_labeled, _ = label(gyral_candidates)
        sulcal_labeled, _ = label(sulcal_candidates)
    
        gyral_props = measure.regionprops(gyral_labeled)
        sulcal_props = measure.regionprops(sulcal_labeled)
    
        gyral_count = len(gyral_props)
        sulcal_count = len(sulcal_props)
    
        return {
        'gyral_count': gyral_count,
        'sulcal_count': sulcal_count,
        'mean_gyral_area': float(np.mean([prop.area for prop in gyral_props])) if gyral_props else 0.0,
        'mean_sulcal_area': float(np.mean([prop.area for prop in sulcal_props])) if sulcal_props else 0.0,
        'gyral_sulcal_ratio': float(gyral_count / max(sulcal_count, 1)),
        'pattern_complexity': float((gyral_count + sulcal_count) / np.sum(brain_mask))
        }

    def _segment_subcortical_structures(self, brain_image, brain_mask):
        deep_structures = self._identify_deep_brain_structures(brain_image, brain_mask)
        ventricular_system = self._analyze_ventricular_system(brain_image, brain_mask)
        white_matter_tracts = self._analyze_white_matter_integrity(brain_image, brain_mask)
        
        return {
            'deep_structures': deep_structures,
            'ventricular_analysis': ventricular_system,
            'white_matter_integrity': white_matter_tracts
        }

    def _identify_deep_brain_structures(self, brain_image, brain_mask):
     h, w = brain_image.shape
     center_region = brain_image[h//4:3*h//4, w//4:3*w//4]
    
     intensity_threshold = np.percentile(center_region, 85)
     high_intensity_regions = (brain_image > intensity_threshold) & brain_mask
    
     labeled_regions, _ = label(high_intensity_regions)
     region_props = measure.regionprops(labeled_regions, brain_image)
    
     subcortical_candidates = []
     for prop in region_props:
        if 50 < prop.area < 2000:
            y, x = prop.centroid
            if h//3 < y < 2*h//3 and w//3 < x < 2*w//3:
                subcortical_candidates.append({
                    'centroid': prop.centroid,
                    'area': prop.area,
                    'mean_intensity': prop.mean_intensity,
                    'eccentricity': prop.eccentricity,
                    'compactness': 4 * np.pi * prop.area / (prop.perimeter ** 2) if prop.perimeter > 0 else 0
                })
                
     return {
         'detected_structures': subcortical_candidates,
         'structure_count': len(subcortical_candidates),
         'total_subcortical_volume': sum([struct['area'] for struct in subcortical_candidates])
     }
    
    def _analyze_ventricular_system(self, brain_image, brain_mask):
     low_intensity_threshold = np.percentile(brain_image[brain_mask], 15)
     csf_candidates = (brain_image < low_intensity_threshold) & brain_mask
    
     csf_cleaned = morphology.remove_small_objects(csf_candidates, min_size=30)
     csf_filled = ndimage.binary_fill_holes(csf_cleaned)
    
     labeled_ventricles, _ = label(csf_filled)
     ventricle_props = measure.regionprops(labeled_ventricles)
    
     ventricles = []
     for prop in ventricle_props:
        if prop.area > 100:
            ventricles.append({
                'area': prop.area,
                'centroid': prop.centroid,
                'eccentricity': prop.eccentricity,
                'solidity': prop.solidity
            })
            
     return {
        'ventricle_count': len(ventricles),
        'total_ventricular_volume': sum([v['area'] for v in ventricles]),
        'ventricle_details': ventricles,
        'brain_ventricular_ratio': sum([v['area'] for v in ventricles]) / np.sum(brain_mask) if ventricles else 0.0
     }


    def _analyze_white_matter_integrity(self, brain_image, brain_mask):
        wm_threshold_low = np.percentile(brain_image[brain_mask], 60)
        wm_threshold_high = np.percentile(brain_image[brain_mask], 95)
        
        white_matter_mask = (brain_image >= wm_threshold_low) & (brain_image <= wm_threshold_high) & brain_mask
        
        gradient_magnitude = np.sqrt(
            cv2.Sobel(brain_image, cv2.CV_64F, 1, 0, ksize=3)**2 + 
            cv2.Sobel(brain_image, cv2.CV_64F, 0, 1, ksize=3)**2
        )
        
        wm_gradient = gradient_magnitude[white_matter_mask]
        
        fa_like_measure = 1.0 / (1.0 + np.var(brain_image[white_matter_mask]) / 1000.0)
        
        tract_coherence = self._compute_tract_coherence(white_matter_mask)
        
        return {
            'white_matter_volume': int(np.sum(white_matter_mask)),
            'mean_wm_intensity': float(np.mean(brain_image[white_matter_mask])),
            'wm_intensity_uniformity': float(1.0 / (1.0 + np.std(brain_image[white_matter_mask]))),
            'fractional_anisotropy_estimate': float(fa_like_measure),
            'mean_diffusivity_estimate': float(np.mean(wm_gradient)),
            'tract_coherence': tract_coherence
        }

    def _compute_tract_coherence(self, wm_mask):
        if np.sum(wm_mask) < 100:
            return 0.0
            
        labeled_wm, num_components = label(wm_mask)
        
        if num_components == 0:
            return 0.0
            
        component_props = measure.regionprops(labeled_wm)
        
        coherence_scores = []
        for prop in component_props:
            if prop.area > 50:
                major_axis = prop.major_axis_length
                minor_axis = prop.minor_axis_length
                if minor_axis > 0:
                    aspect_ratio = major_axis / minor_axis
                    coherence_scores.append(min(aspect_ratio / 3.0, 1.0))
                    
        return float(np.mean(coherence_scores)) if coherence_scores else 0.0

    def _analyze_brain_connectivity(self, brain_image, brain_mask):
        connectivity_matrix = self._compute_structural_connectivity(brain_image, brain_mask)
        network_metrics = self._analyze_network_topology(connectivity_matrix)
        hub_regions = self._identify_connectivity_hubs(connectivity_matrix)
        
        return {
            'connectivity_matrix': connectivity_matrix,
            'network_metrics': network_metrics,
            'hub_regions': hub_regions,
            'global_efficiency': self._compute_global_efficiency(connectivity_matrix),
            'modularity': self._compute_modularity(connectivity_matrix)
        }

    def _compute_structural_connectivity(self, brain_image, brain_mask):
        h, w = brain_image.shape
        grid_size = 16
        step_h, step_w = h // grid_size, w // grid_size
        
        regions = []
        region_intensities = []
        
        for i in range(0, h - step_h, step_h):
            for j in range(0, w - step_w, step_w):
                region_mask = brain_mask[i:i+step_h, j:j+step_w]
                if np.sum(region_mask) > 0.5 * step_h * step_w:
                    region_data = brain_image[i:i+step_h, j:j+step_w][region_mask]
                    regions.append((i + step_h//2, j + step_w//2))
                    region_intensities.append(np.mean(region_data))
        
        n_regions = len(regions)
        if n_regions < 2:
            return np.zeros((2, 2))
            
        connectivity_matrix = np.zeros((n_regions, n_regions))
        
        for i in range(n_regions):
            for j in range(i+1, n_regions):
                y1, x1 = regions[i]
                y2, x2 = regions[j]
                
                distance = np.sqrt((y1-y2)**2 + (x1-x2)**2)
                intensity_correlation = abs(region_intensities[i] - region_intensities[j])
                
                connection_strength = np.exp(-distance / 50.0) * (1.0 / (1.0 + intensity_correlation / 10.0))
                
                connectivity_matrix[i, j] = connection_strength
                connectivity_matrix[j, i] = connection_strength
        
        self.connectivity_matrix = connectivity_matrix
        return connectivity_matrix

    def _analyze_network_topology(self, connectivity_matrix):
        if connectivity_matrix.shape[0] < 2:
            return {'clustering_coefficient': 0.0, 'path_length': 0.0, 'small_worldness': 0.0}
            
        threshold = np.percentile(connectivity_matrix[connectivity_matrix > 0], 75)
        binary_matrix = (connectivity_matrix > threshold).astype(int)
        
        clustering_coeff = self._compute_clustering_coefficient(binary_matrix)
        path_length = self._compute_characteristic_path_length(binary_matrix)
        small_worldness = self._compute_small_worldness(clustering_coeff, path_length)
        
        return {
            'clustering_coefficient': clustering_coeff,
            'characteristic_path_length': path_length,
            'small_worldness': small_worldness,
            'network_density': float(np.sum(binary_matrix) / (binary_matrix.shape[0] * (binary_matrix.shape[0] - 1)))
        }

    def _compute_clustering_coefficient(self, binary_matrix):
        n = binary_matrix.shape[0]
        clustering_coeffs = []
        
        for i in range(n):
            neighbors = np.where(binary_matrix[i, :] == 1)[0]
            k = len(neighbors)
            
            if k < 2:
                clustering_coeffs.append(0.0)
                continue
                
            edges_between_neighbors = 0
            for j in range(len(neighbors)):
                for l in range(j+1, len(neighbors)):
                    if binary_matrix[neighbors[j], neighbors[l]] == 1:
                        edges_between_neighbors += 1
                        
            clustering_coeff = 2.0 * edges_between_neighbors / (k * (k - 1))
            clustering_coeffs.append(clustering_coeff)
            
        return float(np.mean(clustering_coeffs))

    def _compute_characteristic_path_length(self, binary_matrix):
        n = binary_matrix.shape[0]
        distances = np.full((n, n), np.inf)
        
        np.fill_diagonal(distances, 0)
        distances[binary_matrix == 1] = 1
        
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    distances[i, j] = min(distances[i, j], distances[i, k] + distances[k, j])
        
        finite_distances = distances[np.isfinite(distances) & (distances > 0)]
        return float(np.mean(finite_distances)) if len(finite_distances) > 0 else 0.0

    def _compute_small_worldness(self, clustering_coeff, path_length):
        if path_length == 0:
            return 0.0
        return clustering_coeff / path_length

    def _identify_connectivity_hubs(self, connectivity_matrix):
        if connectivity_matrix.shape[0] < 2:
            return []
            
        node_degrees = np.sum(connectivity_matrix > np.percentile(connectivity_matrix, 75), axis=1)
        betweenness_centrality = self._compute_betweenness_centrality(connectivity_matrix)
        
        hub_threshold = np.percentile(node_degrees, 85)
        hub_indices = np.where(node_degrees >= hub_threshold)[0]
        
        hubs = []
        for idx in hub_indices:
            hubs.append({
                'node_index': int(idx),
                'degree': int(node_degrees[idx]),
                'betweenness_centrality': float(betweenness_centrality[idx]),
                'hub_score': float(node_degrees[idx] * betweenness_centrality[idx])
            })
            
        return sorted(hubs, key=lambda x: x['hub_score'], reverse=True)

    def _compute_betweenness_centrality(self, connectivity_matrix):
        n = connectivity_matrix.shape[0]
        betweenness = np.zeros(n)
        
        threshold = np.percentile(connectivity_matrix[connectivity_matrix > 0], 50)
        binary_matrix = (connectivity_matrix > threshold).astype(int)
        
        for s in range(n):
            stack = []
            paths = {s: []}
            sigma = np.zeros(n)
            sigma[s] = 1.0
            distance = np.full(n, -1)
            distance[s] = 0
            queue = [s]
            
            while queue:
                v = queue.pop(0)
                stack.append(v)
                
                for w in np.where(binary_matrix[v, :] == 1)[0]:
                    if distance[w] < 0:
                        queue.append(w)
                        distance[w] = distance[v] + 1
                    
                    if distance[w] == distance[v] + 1:
                        sigma[w] += sigma[v]
                        if w not in paths:
                            paths[w] = []
                        paths[w].append(v)
            
            delta = np.zeros(n)
            while stack:
                w = stack.pop()
                if w in paths:
                    for v in paths[w]:
                        delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                        
                if w != s:
                    betweenness[w] += delta[w]
                    
        return betweenness / 2.0 if n > 2 else betweenness

    def _compute_global_efficiency(self, connectivity_matrix):
        if connectivity_matrix.shape[0] < 2:
            return 0.0
            
        n = connectivity_matrix.shape[0]
        efficiency_sum = 0.0
        count = 0
        
        for i in range(n):
            for j in range(i+1, n):
                if connectivity_matrix[i, j] > 0:
                    efficiency_sum += connectivity_matrix[i, j]
                    count += 1
                    
        return efficiency_sum / count if count > 0 else 0.0

    def _compute_modularity(self, connectivity_matrix):
        if connectivity_matrix.shape[0] < 2:
            return 0.0
            
        n = connectivity_matrix.shape[0]
        m = np.sum(connectivity_matrix) / 2.0
        
        if m == 0:
            return 0.0
            
        degrees = np.sum(connectivity_matrix, axis=1)
        
        communities = self._detect_communities(connectivity_matrix)
        
        modularity = 0.0
        for i in range(n):
            for j in range(n):
                if communities[i] == communities[j]:
                    expected = (degrees[i] * degrees[j]) / (2.0 * m)
                    modularity += (connectivity_matrix[i, j] - expected)
                    
        return modularity / (2.0 * m)

    def _detect_communities(self, connectivity_matrix):
        n = connectivity_matrix.shape[0]
        if n < 4:
            return np.zeros(n)
            
        threshold = np.percentile(connectivity_matrix[connectivity_matrix > 0], 60)
        thresholded_matrix = connectivity_matrix > threshold
        
        communities = np.zeros(n)
        community_id = 0
        visited = np.zeros(n, dtype=bool)
        
        for i in range(n):
            if not visited[i]:
                component = self._find_connected_component(thresholded_matrix, i)
                for node in component:
                    communities[node] = community_id
                    visited[node] = True
                community_id += 1
                
        return communities

    def _find_connected_component(self, adjacency_matrix, start_node):
        component = []
        stack = [start_node]
        visited_local = set()
        
        while stack:
            node = stack.pop()
            if node not in visited_local:
                visited_local.add(node)
                component.append(node)
                
                neighbors = np.where(adjacency_matrix[node, :])[0]
                for neighbor in neighbors:
                    if neighbor not in visited_local:
                        stack.append(neighbor)
                        
        return component

    def _compute_brain_morphometry(self, brain_image, brain_mask):
        volume_analysis = self._compute_volumetric_measures(brain_mask)
        asymmetry_analysis = self._analyze_brain_asymmetry(brain_image, brain_mask)
        shape_analysis = self._analyze_brain_shape(brain_mask)
        texture_complexity = self._compute_advanced_texture_measures(brain_image, brain_mask)
        
        return {
            'volumetric_measures': volume_analysis,
            'asymmetry_analysis': asymmetry_analysis,
            'shape_analysis': shape_analysis,
            'texture_complexity': texture_complexity
        }

    def _compute_volumetric_measures(self, brain_mask):
        total_volume = np.sum(brain_mask)
        
        brain_height, brain_width = brain_mask.shape
        centroid = ndimage.center_of_mass(brain_mask)
        
        moments = measure.moments(brain_mask.astype(int))
        
        return {
            'total_brain_volume': int(total_volume),
            'brain_centroid': centroid,
            'volume_density': float(total_volume / (brain_height * brain_width)),
            'moment_invariants': {
                'hu_moment_1': float(moments[2, 0] + moments[0, 2]),
                'hu_moment_2': float((moments[2, 0] - moments[0, 2])**2 + 4 * moments[1, 1]**2),
                'compactness': float(total_volume / (np.sum(brain_mask) ** (2/3)))
            }
        }

    def _analyze_brain_asymmetry(self, brain_image, brain_mask):
        h, w = brain_mask.shape
        mid_line = w // 2
        
        left_hemisphere = brain_mask[:, :mid_line]
        right_hemisphere = brain_mask[:, mid_line:]
        
        right_flipped = np.fliplr(right_hemisphere)
        
        min_width = min(left_hemisphere.shape[1], right_flipped.shape[1])
        left_cropped = left_hemisphere[:, -min_width:]
        right_cropped = right_flipped[:, :min_width]
        
        volume_asymmetry = abs(np.sum(left_cropped) - np.sum(right_cropped))
        intensity_asymmetry = abs(np.mean(brain_image[:, :mid_line][left_hemisphere]) - 
                                np.mean(brain_image[:, mid_line:][right_hemisphere]))
        
        overlap_coefficient = np.sum(left_cropped & right_cropped) / np.sum(left_cropped | right_cropped)
        
        return {
            'volume_asymmetry_index': float(volume_asymmetry / (np.sum(left_cropped) + np.sum(right_cropped))),
            'intensity_asymmetry': float(intensity_asymmetry),
            'hemispheric_overlap': float(overlap_coefficient),
            'left_hemisphere_volume': int(np.sum(left_hemisphere)),
            'right_hemisphere_volume': int(np.sum(right_hemisphere))
        }

    def _analyze_brain_shape(self, brain_mask):
        contours, _ = cv2.findContours(brain_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        if not contours:
         return {'error': 'No contours found'}
        
        main_contour = max(contours, key=cv2.contourArea)
    
        if len(main_contour) < 5:
         return {
             'area': float(cv2.contourArea(main_contour)),
             'perimeter': float(cv2.arcLength(main_contour, True)),
             'circularity': 0.0,
             'solidity': 0.0,
             'eccentricity': 0.0,
             'aspect_ratio': 1.0,
             'orientation': 0.0,
             'centroid': (0, 0)
         }
    
        area = cv2.contourArea(main_contour)
        perimeter = cv2.arcLength(main_contour, True)
    
        hull = cv2.convexHull(main_contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
    
        ellipse = cv2.fitEllipse(main_contour)
        (center, (major_axis, minor_axis), angle) = ellipse
    
        eccentricity = np.sqrt(1 - (minor_axis / major_axis)**2) if major_axis > 0 else 0
    
        moments = cv2.moments(main_contour)
        if moments['m00'] != 0:
         cx = int(moments['m10'] / moments['m00'])
         cy = int(moments['m01'] / moments['m00'])
        else:
         cx, cy = 0, 0
        
        return {
            'area': float(area),
            'perimeter': float(perimeter),
            'circularity': float(4 * np.pi * area / (perimeter**2)) if perimeter > 0 else 0,
            'solidity': float(solidity),
            'eccentricity': float(eccentricity),
            'aspect_ratio': float(major_axis / minor_axis) if minor_axis > 0 else 0,
            'orientation': float(angle),
            'centroid': (int(cx), int(cy))
        }

    def _compute_advanced_texture_measures(self, brain_image, brain_mask):
        masked_image = brain_image[brain_mask]
        
        if len(masked_image) == 0:
            return {'error': 'No brain tissue found'}
            
        histogram, bins = np.histogram(masked_image, bins=256, range=(0, 255))
        histogram = histogram.astype(float) / np.sum(histogram)
        
        entropy = -np.sum(histogram * np.log2(histogram + 1e-10))
        
        mean_intensity = np.mean(masked_image)
        skewness = np.mean(((masked_image - mean_intensity) / np.std(masked_image))**3)
        kurtosis = np.mean(((masked_image - mean_intensity) / np.std(masked_image))**4) - 3
        
        energy = np.sum(histogram**2)
        uniformity = np.max(histogram)
        
        wavelet_features = self._compute_wavelet_features(brain_image, brain_mask)
        
        return {
            'entropy': float(entropy),
            'skewness': float(skewness),
            'kurtosis': float(kurtosis),
            'energy': float(energy),
            'uniformity': float(uniformity),
            'wavelet_features': wavelet_features
        }

    def _compute_wavelet_features(self, brain_image, brain_mask):
        try:
            approximation = gaussian_filter(brain_image.astype(np.float32), sigma=2.0)
            horizontal = brain_image - gaussian_filter(brain_image.astype(np.float32), sigma=(2.0, 0.5))
            vertical = brain_image - gaussian_filter(brain_image.astype(np.float32), sigma=(0.5, 2.0))
            diagonal = brain_image - gaussian_filter(brain_image.astype(np.float32), sigma=1.0)
            
            return {
                'approximation_energy': float(np.sum(approximation[brain_mask]**2)),
                'horizontal_energy': float(np.sum(horizontal[brain_mask]**2)),
                'vertical_energy': float(np.sum(vertical[brain_mask]**2)),
                'diagonal_energy': float(np.sum(diagonal[brain_mask]**2))
            }
        except Exception:
            return {
                'approximation_energy': 0.0,
                'horizontal_energy': 0.0,
                'vertical_energy': 0.0,
                'diagonal_energy': 0.0
            }

    def _map_clusters_to_anatomical_regions(self, clustered_image, brain_image):
        unique_clusters = np.unique(clustered_image)
        regions = {}
        
        h, w = brain_image.shape
        
        for cluster_id in unique_clusters:
            if cluster_id == 0:
                continue
                
            cluster_mask = clustered_image == cluster_id
            cluster_data = brain_image[cluster_mask]
            
            if len(cluster_data) < 10:
                continue
                
            centroid = ndimage.center_of_mass(cluster_mask)
            
            anatomical_region = self._assign_anatomical_label(centroid, (h, w), cluster_data)
            
            regions[anatomical_region] = {
                'mean_intensity': float(np.mean(cluster_data)),
                'volume': int(np.sum(cluster_mask)),
                'max_intensity': float(np.max(cluster_data)),
                'std_intensity': float(np.std(cluster_data)),
                'centroid': centroid,
                'cluster_id': int(cluster_id)
            }
            
        return regions

    def _assign_anatomical_label(self, centroid, image_shape, intensity_data):
        y, x = centroid
        h, w = image_shape
        
        rel_y, rel_x = y / h, x / w
        mean_intensity = np.mean(intensity_data)
        
        if rel_y < 0.3:
            if mean_intensity > 120:
                return "Superior_Frontal_Cortex"
            else:
                return "Frontal_White_Matter"
        elif rel_y > 0.7:
            if mean_intensity > 100:
                return "Occipital_Cortex"
            else:
                return "Occipital_White_Matter"
        elif 0.4 < rel_y < 0.6:
            if 0.3 < rel_x < 0.7:
                if mean_intensity < 80:
                    return "Deep_Gray_Matter"
                else:
                    return "Central_White_Matter"
            elif rel_x < 0.3:
                return "Left_Temporal_Region"
            else:
                return "Right_Temporal_Region"
        else:
            if mean_intensity > 110:
                return "Parietal_Cortex"
            else:
                return "Parietal_White_Matter"

    def _extract_brain_mask(self, image):
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(binary)
            cv2.fillPoly(mask, [largest_contour], 255)
            return (mask > 0).astype(np.uint8)

        return np.ones_like(image, dtype=np.uint8)

    def visualize_mri_analysis(self, original_image, analysis_results):
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(3, 3, figsize=(18, 15))

        axs[0, 0].imshow(original_image, cmap="gray")
        axs[0, 0].set_title("Original MRI Image")

        axs[0, 1].imshow(analysis_results["bias_corrected_image"], cmap="gray")
        axs[0, 1].set_title("Bias Field Corrected")

        axs[0, 2].imshow(analysis_results["enhanced_image"], cmap="gray")
        axs[0, 2].set_title("Contrast Enhanced")

        axs[1, 0].imshow(analysis_results["segmented_image"], cmap="nipy_spectral")
        axs[1, 0].set_title("Anatomical Segmentation")

        lesion_overlay = original_image.copy()
        for lesion in analysis_results["lesions"]:
            y, x = int(lesion["centroid"][0]), int(lesion["centroid"][1])
            cv2.circle(lesion_overlay, (x, y), 5, (255, 0, 0), 2)
        axs[1, 1].imshow(lesion_overlay, cmap="gray")
        axs[1, 1].set_title(f'Detected Lesions ({len(analysis_results["lesions"])})')

        if analysis_results["tissue_properties"]:
            tissues = list(analysis_results["tissue_properties"].keys())
            intensities = [
                props["mean_intensity"]
                for props in analysis_results["tissue_properties"].values()
            ]
            axs[1, 2].bar(tissues, intensities)
            axs[1, 2].set_title("Mean Tissue Intensities")
            axs[1, 2].tick_params(axis="x", rotation=45)

        if analysis_results["brain_regions"]:
            regions = list(analysis_results["brain_regions"].keys())
            volumes = [
                props["volume"] for props in analysis_results["brain_regions"].values()
            ]
            axs[2, 0].bar(regions, volumes)
            axs[2, 0].set_title("Brain Region Volumes")
            axs[2, 0].tick_params(axis="x", rotation=45)

        texture_features = analysis_results["texture_features"]
        feature_names = list(texture_features.keys())
        feature_values = list(texture_features.values())
        axs[2, 1].bar(feature_names, feature_values)
        axs[2, 1].set_title("Texture Features")
        axs[2, 1].tick_params(axis="x", rotation=45)

        axs[2, 2].text(
            0.1,
            0.5,
            f"Sequence Type: {analysis_results['sequence_type']}\n"
            f"Lesions Detected: {len(analysis_results['lesions'])}\n"
            f"Brain Regions: {len(analysis_results['brain_regions'])}\n"
            f"Tissue Types: {len(analysis_results['tissue_properties'])}",
            transform=axs[2, 2].transAxes,
            fontsize=12,
            verticalalignment="center",
        )
        axs[2, 2].set_title("Analysis Summary")

        for ax in axs.flat:
            if (
                ax != axs[2, 2]
                and ax != axs[1, 2]
                and ax != axs[2, 0]
                and ax != axs[2, 1]
            ):
                ax.axis("off")

        plt.tight_layout()
        plt.show()

    def create_brain_tissue_from_mri(self, image, tissue_name: str, sequence_type="T1"):
        analysis = self.analyze_mri(image, sequence_type)

        lesions = analysis["lesions"]
        texture_features = analysis["texture_features"]

        lesion_burden = len(lesions) / (image.size / 10000)
        mutation_risk = min(lesion_burden * 0.01, 0.15)

        tissue_integrity = 1.0 - (
            texture_features["contrast"] / 255.0 * 0.3 + lesion_burden * 0.2
        )
        tissue_integrity = max(0.5, tissue_integrity)

        segmented_image = analysis["segmented_image"]
        unique_values, counts = np.unique(segmented_image, return_counts=True)
        cells = []

        for value, count in zip(unique_values, counts):
            if value > 0:
                cell_count = min(int(count / 2000), 50)
                for i in range(cell_count):
                    cell_name = f"BrainCell_{value}_{i}"
                    base_health = tissue_integrity * 100
                    cell_health = str(random.uniform(base_health - 10, base_health + 5))
                    cells.append(Cell(cell_name, cell_health))

        brain_tissue = RadiationAffectedTissue(
            name=tissue_name,
            cells=cells,
            mutation_rate=mutation_risk,
            radiation_level=0.0,
            tissue_type="brain_tissue",
        )

        brain_tissue.dna_repair_rate = 0.08 * tissue_integrity

        return brain_tissue

    def compare_mri_sequences(self, t1_image, t2_image, flair_image, tissue_name: str) -> dict:
        t1_analysis = self.analyze_mri(t1_image, "T1")
        t2_analysis = self.analyze_mri(t2_image, "T2")
        flair_analysis = self.analyze_mri(flair_image, "FLAIR")

        t1_tissue = self.create_brain_tissue_from_mri(t1_image, f"{tissue_name}_T1", "T1")
        t2_tissue = self.create_brain_tissue_from_mri(t2_image, f"{tissue_name}_T2", "T2")
        flair_tissue = self.create_brain_tissue_from_mri(flair_image, f"{tissue_name}_FLAIR", "FLAIR")
        analyses = {"T1": t1_analysis, "T2": t2_analysis, "FLAIR": flair_analysis}

        comparison = {
            "tissue_name": tissue_name,
            "sequence_comparison": {
                "T1": {
                    "lesion_count": len(t1_analysis["lesions"]),
                    "tissue_types": len(t1_analysis["tissue_properties"]),
                    "average_cell_health": t1_tissue.get_average_cell_health(),
                    "tissue_integrity": getattr(t1_tissue, "tissue_integrity", 0.8),
                    "dominant_tissues": list(t1_analysis["tissue_properties"].keys())[:3],
                },
                "T2": {
                    "lesion_count": len(t2_analysis["lesions"]),
                    "tissue_types": len(t2_analysis["tissue_properties"]),
                    "average_cell_health": t2_tissue.get_average_cell_health(),
                    "tissue_integrity": getattr(t2_tissue, "tissue_integrity", 0.8),
                    "dominant_tissues": list(t2_analysis["tissue_properties"].keys())[:3],
                },
                "FLAIR": {
                    "lesion_count": len(flair_analysis["lesions"]),
                    "tissue_types": len(flair_analysis["tissue_properties"]),
                    "average_cell_health": flair_tissue.get_average_cell_health(),
                    "tissue_integrity": getattr(flair_tissue, "tissue_integrity", 0.8),
                    "dominant_tissues": list(flair_analysis["tissue_properties"].keys())[:3],
                },
            },
            "clinical_insights": {
                "best_lesion_detection": (
                    "FLAIR"
                    if len(flair_analysis["lesions"])
                    >= max(len(t1_analysis["lesions"]), len(t2_analysis["lesions"]))
                    else (
                        "T2"
                        if len(t2_analysis["lesions"]) > len(t1_analysis["lesions"])
                        else "T1"
                    )
                ),
                "most_detailed_segmentation": max(
                ["T1", "T2", "FLAIR"],
                    key=lambda x: len(analyses[x]["tissue_properties"])
                ),
                "overall_tissue_health": (
                    t1_tissue.get_average_cell_health()
                    + t2_tissue.get_average_cell_health()
                    + flair_tissue.get_average_cell_health()
                )
                / 3,
            },
        }

        return comparison
