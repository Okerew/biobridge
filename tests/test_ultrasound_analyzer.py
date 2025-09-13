import unittest
import numpy as np
from unittest.mock import MagicMock
from biobridge.tools.ultrasound_analyzer import UltrasoundAnalyzer

class TestUltrasoundAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a mock image_analyzer
        self.mock_image_analyzer = MagicMock()
        self.mock_image_analyzer.ij.py.from_java.return_value = np.random.randint(0, 255, (128, 128), dtype=np.uint8)

        # Initialize UltrasoundAnalyzer with the mock
        self.analyzer = UltrasoundAnalyzer(self.mock_image_analyzer)

        # Create a sample ultrasound image (2D)
        self.sample_image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)

    def test_analyze_ultrasound(self):
        # Test the analyze_ultrasound method
        result = self.analyzer.analyze_ultrasound(self.sample_image, frequency_mhz=7.5, depth_mm=100)

        # Check if the result is a dictionary and contains expected keys
        self.assertIsInstance(result, dict)
        self.assertIn("original_volume", result)
        self.assertIn("despeckled_volume", result)
        self.assertIn("enhanced_volume", result)
        self.assertIn("echogenicity_map", result)
        self.assertIn("acoustic_analysis", result)
        self.assertIn("edges", result)
        self.assertIn("structure_detection", result)
        self.assertIn("measurements", result)
        self.assertIn("abnormalities", result)
        self.assertIn("texture_features", result)

    def test_apply_time_gain_compensation(self):
        # Test the apply_time_gain_compensation method
        corrected = self.analyzer.apply_time_gain_compensation(self.sample_image, depth_mm=100)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(corrected, np.ndarray)
        self.assertEqual(corrected.shape, self.sample_image.shape)

    def test_reduce_speckle_noise(self):
        # Test the reduce_speckle_noise method
        despeckled = self.analyzer.reduce_speckle_noise(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(despeckled, np.ndarray)
        self.assertEqual(despeckled.shape, self.sample_image.shape)

    def test_enhance_ultrasound_contrast(self):
        # Test the enhance_ultrasound_contrast method
        enhanced = self.analyzer.enhance_ultrasound_contrast(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(enhanced, np.ndarray)
        self.assertEqual(enhanced.shape, self.sample_image.shape)

    def test_classify_echogenicity(self):
        # Test the classify_echogenicity method
        echogenicity_map = self.analyzer.classify_echogenicity(self.sample_image)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(echogenicity_map, dict)
        self.assertIn("anechoic", echogenicity_map)
        self.assertIn("hypoechoic", echogenicity_map)
        self.assertIn("isoechoic", echogenicity_map)
        self.assertIn("hyperechoic", echogenicity_map)
        self.assertIn("highly_hyperechoic", echogenicity_map)

    def test_analyze_acoustic_properties(self):
        # Test the analyze_acoustic_properties method
        acoustic_analysis = self.analyzer.analyze_acoustic_properties(self.sample_image)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(acoustic_analysis, dict)
        self.assertIn("acoustic_shadows", acoustic_analysis)
        self.assertIn("acoustic_enhancement", acoustic_analysis)
        self.assertIn("column_profiles", acoustic_analysis)

    def test_detect_ultrasound_edges(self):
        # Test the detect_ultrasound_edges method
        edges = self.analyzer.detect_ultrasound_edges(self.sample_image)

        # Check if the output is a NumPy array and is 2D
        self.assertIsInstance(edges, np.ndarray)
        self.assertEqual(len(edges.shape), 2)

    def test_detect_anatomical_structures(self):
        # Test the detect_anatomical_structures method
        echogenicity_map = self.analyzer.classify_echogenicity(self.sample_image)
        structure_detection = self.analyzer.detect_anatomical_structures(
            self.sample_image, echogenicity_map, frequency_mhz=7.5
        )

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(structure_detection, dict)
        self.assertIn("vessels", structure_detection)
        self.assertIn("organs", structure_detection)
        self.assertIn("cysts", structure_detection)
        self.assertIn("masses", structure_detection)
        self.assertIn("bones", structure_detection)

    def test_perform_ultrasound_measurements(self):
        # Test the perform_ultrasound_measurements method
        echogenicity_map = self.analyzer.classify_echogenicity(self.sample_image)
        structure_detection = self.analyzer.detect_anatomical_structures(
            self.sample_image, echogenicity_map, frequency_mhz=7.5
        )
        measurements = self.analyzer.perform_ultrasound_measurements(structure_detection)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(measurements, dict)
        self.assertIn("vessel_diameters", measurements)
        self.assertIn("areas", measurements)

    def test_detect_ultrasound_abnormalities(self):
        # Test the detect_ultrasound_abnormalities method
        echogenicity_map = self.analyzer.classify_echogenicity(self.sample_image)
        structure_detection = self.analyzer.detect_anatomical_structures(
            self.sample_image, echogenicity_map, frequency_mhz=7.5
        )
        abnormalities = self.analyzer.detect_ultrasound_abnormalities(
            self.sample_image, echogenicity_map, structure_detection
        )

        # Check if the output is a list
        self.assertIsInstance(abnormalities, list)

    def test_analyze_ultrasound_texture(self):
        # Test the analyze_ultrasound_texture method
        texture_features = self.analyzer.analyze_ultrasound_texture(self.sample_image)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(texture_features, dict)
        self.assertIn("local_mean", texture_features)
        self.assertIn("local_variance", texture_features)
        self.assertIn("local_entropy", texture_features)

    def test_quick_ultrasound_analysis(self):
        # Test the quick_ultrasound_analysis method
        quick_results = self.analyzer.quick_ultrasound_analysis(self.sample_image)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(quick_results, dict)
        self.assertIn("mean_intensity", quick_results)
        self.assertIn("intensity_std", quick_results)
        self.assertIn("anechoic_ratio", quick_results)
        self.assertIn("hypoechoic_ratio", quick_results)
        self.assertIn("hyperechoic_ratio", quick_results)

    def test_assess_image_quality(self):
        # Test the assess_image_quality method
        quality_metrics = self.analyzer.assess_image_quality(self.sample_image)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(quality_metrics, dict)
        self.assertIn("sharpness", quality_metrics)
        self.assertIn("contrast", quality_metrics)
        self.assertIn("snr", quality_metrics)
        self.assertIn("overall_quality", quality_metrics)
        self.assertIn("quality_grade", quality_metrics)

if __name__ == "__main__":
    unittest.main()
