import unittest
from unittest.mock import Mock, patch
import numpy as np
import cv2
from biobridge.tools.mri_analyzer import MRIAnalyzer


class TestMRIAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.mock_image_analyzer = Mock()
        self.analyzer = MRIAnalyzer(self.mock_image_analyzer)
        
        self.sample_image = np.random.randint(50, 200, (128, 128), dtype=np.uint8)
        self.sample_brain_mask = np.ones((128, 128), dtype=np.uint8)
        
        binary_mask = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(binary_mask, (50, 50), 30, 1, -1)
        self.valid_brain_mask = binary_mask
        
    def test_initialization(self):
        self.assertIsNotNone(self.analyzer.atlas_templates)
        self.assertIn('brodmann_areas', self.analyzer.atlas_templates)
        self.assertIn('subcortical_structures', self.analyzer.atlas_templates)
        
    def test_atlas_initialization(self):
        atlas = self.analyzer._initialize_brain_atlas()
        
        self.assertIn('brodmann_areas', atlas)
        self.assertIn('subcortical_structures', atlas)
        self.assertEqual(atlas['brodmann_areas'][4], 'Primary_Motor_Cortex')
        self.assertIn('Thalamus', atlas['subcortical_structures'])
        
    def test_correct_bias_field(self):
        valid_image = np.random.randint(10, 250, (64, 64), dtype=np.uint8)
        result = self.analyzer.correct_bias_field(valid_image)
        
        self.assertEqual(result.shape, valid_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        
    def test_reduce_noise(self):
        result = self.analyzer.reduce_noise(self.sample_image)
        
        self.assertEqual(result.shape, self.sample_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        
    def test_enhance_contrast_sequences(self):
        sequences = ["T1", "T2", "FLAIR", "DWI", "T1_contrast"]
        
        for seq in sequences:
            result = self.analyzer.enhance_contrast(self.sample_image, seq)
            self.assertEqual(result.shape, self.sample_image.shape)
            self.assertEqual(result.dtype, np.uint8)
        
    def test_segment_anatomical_structures(self):
        result = self.analyzer.segment_anatomical_structures(self.sample_image, "T1")
        
        self.assertEqual(result.shape, self.sample_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        
    def test_detect_lesions(self):
        result = self.analyzer.detect_lesions(self.sample_image, "FLAIR")
        
        self.assertIsInstance(result, list)
        
    def test_measure_tissue_properties(self):
        segmented = np.random.randint(1, 4, (128, 128), dtype=np.uint8)
        result = self.analyzer.measure_tissue_properties(self.sample_image, segmented, "T1")
        
        self.assertIsInstance(result, dict)
        
    def test_get_tissue_name(self):
        t1_name = self.analyzer._get_tissue_name(2, "T1")
        self.assertEqual(t1_name, "Gray_Matter")
        
        unknown_name = self.analyzer._get_tissue_name(99, "Unknown")
        self.assertEqual(unknown_name, "Unknown_Tissue_99")
        
    def test_extract_texture_features(self):
        result = self.analyzer.extract_texture_features(self.sample_image)
        
        self.assertIsInstance(result, dict)
        expected_keys = ['mean_gradient_magnitude', 'gradient_variance', 'lbp_uniformity',
                        'contrast', 'homogeneity', 'entropy']
        for key in expected_keys:
            self.assertIn(key, result)
            
    def test_extract_brain_mask(self):
        brain_image = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(brain_image, (50, 50), 30, 200, -1)
        
        result = self.analyzer._extract_brain_mask(brain_image)
        
        self.assertEqual(result.shape, brain_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        
    def test_extract_multiscale_features(self):
        result = self.analyzer._extract_multiscale_features(self.sample_image.astype(np.float32))
        
        self.assertIsInstance(result, dict)
        self.assertIn('scale_1', result)
        self.assertIn('scale_2', result)
        self.assertIn('scale_3', result)
        
    def test_compute_cortical_thickness(self):
        result = self.analyzer._compute_cortical_thickness(self.sample_image, self.valid_brain_mask)
        
        self.assertEqual(result.shape, self.sample_image.shape)
        self.assertEqual(result.dtype, np.float32)
        
    def test_analyze_cortical_curvature(self):
        result = self.analyzer._analyze_cortical_curvature(self.sample_image[:100, :100], self.valid_brain_mask)
        
        self.assertIsInstance(result, dict)
        self.assertIn('mean_curvature', result)
        self.assertIn('curvature_variance', result)
        
    def test_compute_structural_connectivity_valid_size(self):
        large_image = np.random.randint(50, 200, (64, 64), dtype=np.uint8)
        large_mask = np.ones((64, 64), dtype=np.uint8)
        
        result = self.analyzer._compute_structural_connectivity(large_image, large_mask)
        
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result.shape), 2)
        
    def test_clustering_coefficient(self):
        test_matrix = np.array([[0, 1, 1, 0],
                               [1, 0, 1, 1],
                               [1, 1, 0, 1],
                               [0, 1, 1, 0]])
        result = self.analyzer._compute_clustering_coefficient(test_matrix)
        
        self.assertIsInstance(result, float)
        
    def test_analyze_brain_asymmetry(self):
        large_image = np.random.randint(50, 200, (100, 100), dtype=np.uint8)
        large_mask = np.ones((100, 100), dtype=np.uint8)
        
        result = self.analyzer._analyze_brain_asymmetry(large_image, large_mask)
        
        self.assertIsInstance(result, dict)
        self.assertIn('volume_asymmetry_index', result)
        
    def test_analyze_brain_shape_with_valid_contour(self):
        binary_mask = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(binary_mask, (50, 50), 30, 1, -1)
        
        result = self.analyzer._analyze_brain_shape(binary_mask)
        
        self.assertIsInstance(result, dict)
        if 'error' not in result:
            self.assertIn('area', result)
            self.assertIn('perimeter', result)
        
    def test_assign_anatomical_label(self):
        centroid = (32, 32)
        image_shape = (128, 128)
        intensity_data = np.array([120, 125, 115])
        
        result = self.analyzer._assign_anatomical_label(centroid, image_shape, intensity_data)
        
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        
    def test_analyze_mri_with_mock(self):
        mock_java_image = Mock()
        self.analyzer.image_analyzer.ij.py.from_java.return_value = self.sample_image
        
        result = self.analyzer.analyze_mri(mock_java_image, "T1")
        
        self.assertIsInstance(result, dict)
        expected_keys = ['bias_corrected_image', 'denoised_image', 'enhanced_image',
                        'segmented_image', 'lesions', 'tissue_properties',
                        'texture_features', 'brain_regions', 'sequence_type']
        for key in expected_keys:
            self.assertIn(key, result)
            
    def test_create_brain_tissue_from_mri_with_proper_mock(self):
        mock_java_image = Mock()
        mock_java_image.size = 16384
        
        mock_analysis_result = {
            'lesions': [{'centroid': (100, 100), 'area': 50}],
            'texture_features': {'contrast': 128.0},
            'segmented_image': np.random.randint(0, 4, (128, 128), dtype=np.uint8)
        }
        
        with patch.object(self.analyzer, 'analyze_mri', return_value=mock_analysis_result):
            result = self.analyzer.create_brain_tissue_from_mri(mock_java_image, "test_tissue", "T1")
            
            self.assertEqual(result.name, "test_tissue")
            self.assertEqual(result.tissue_type, "brain_tissue")
            
    def test_compare_mri_sequences_fixed(self):
        mock_t1_image = Mock()
        mock_t1_image.size = 16384
        mock_t2_image = Mock()
        mock_t2_image.size = 16384
        mock_flair_image = Mock()
        mock_flair_image.size = 16384
        
        mock_analysis_result = {
            'lesions': [{'centroid': (100, 100), 'area': 50}],
            'tissue_properties': {'Gray_Matter': {'mean_intensity': 120.0}},
            'texture_features': {'contrast': 128.0},
            'segmented_image': np.random.randint(0, 4, (128, 128), dtype=np.uint8)
        }
        
        with patch.object(self.analyzer, 'analyze_mri', return_value=mock_analysis_result):
            with patch.object(self.analyzer, 'create_brain_tissue_from_mri') as mock_create:
                mock_tissue = Mock()
                mock_tissue.get_average_cell_health.return_value = 85.0
                mock_create.return_value = mock_tissue
                
                result = self.analyzer.compare_mri_sequences(mock_t1_image, mock_t2_image, 
                                                           mock_flair_image, "test_comparison")
                
                self.assertIsInstance(result, dict)
                self.assertIn('tissue_name', result)
                self.assertIn('sequence_comparison', result)
                
    def test_edge_cases_with_valid_inputs(self):
        valid_small_image = np.random.randint(10, 250, (32, 32), dtype=np.uint8)
        
        lesions = self.analyzer.detect_lesions(valid_small_image, "T1")
        self.assertIsInstance(lesions, list)
        
        result = self.analyzer.extract_texture_features(valid_small_image)
        self.assertIsInstance(result, dict)
        
    def test_connectivity_with_proper_dimensions(self):
        proper_image = np.random.randint(50, 200, (64, 64), dtype=np.uint8)
        proper_mask = np.ones((64, 64), dtype=np.uint8)
        
        result = self.analyzer._compute_structural_connectivity(proper_image, proper_mask)
        self.assertIsInstance(result, np.ndarray)


if __name__ == '__main__':
    unittest.main(verbosity=2)
