import unittest
import numpy as np
from unittest.mock import MagicMock
from biobridge.tools.gamma_analyzer import GammaRayAnalyzer

class TestGammaRayAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a mock image_analyzer
        self.mock_image_analyzer = MagicMock()
        self.mock_image_analyzer.ij.py.from_java.return_value = np.random.randint(0, 255, (128, 128), dtype=np.uint8)

        # Initialize GammaRayAnalyzer with the mock
        self.analyzer = GammaRayAnalyzer(self.mock_image_analyzer)

        # Create a sample gamma ray image (2D)
        self.sample_image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)

    def test_analyze_gamma_ray(self):
        # Test the analyze_gamma_ray method
        result = self.analyzer.analyze_gamma_ray(self.sample_image)

        # Check if the result is a dictionary and contains expected keys
        self.assertIsInstance(result, dict)
        self.assertIn("denoised_image", result)
        self.assertIn("enhanced_image", result)
        self.assertIn("hot_spots", result)
        self.assertIn("segmented_image", result)
        self.assertIn("anomalies", result)
        self.assertIn("radiation_intensity", result)

    def test_reduce_noise(self):
        # Test the reduce_noise method
        denoised = self.analyzer.reduce_noise(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(denoised, np.ndarray)
        self.assertEqual(denoised.shape, self.sample_image.shape)

    def test_enhance_contrast(self):
        # Test the enhance_contrast method
        enhanced = self.analyzer.enhance_contrast(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(enhanced, np.ndarray)
        self.assertEqual(enhanced.shape, self.sample_image.shape)

    def test_detect_hot_spots(self):
        # Test the detect_hot_spots method
        hot_spots = self.analyzer.detect_hot_spots(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(hot_spots, np.ndarray)
        self.assertEqual(hot_spots.shape, self.sample_image.shape)

    def test_segment_image(self):
        # Test the segment_image method
        segmented = self.analyzer.segment_image(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(segmented, np.ndarray)
        self.assertEqual(segmented.shape, self.sample_image.shape)

    def test_detect_anomalies(self):
        # Test the detect_anomalies method
        segmented = self.analyzer.segment_image(self.sample_image)
        anomalies = self.analyzer.detect_anomalies(self.sample_image, segmented)

        # Check if the output is a list
        self.assertIsInstance(anomalies, list)

    def test_measure_radiation_intensity(self):
        # Test the measure_radiation_intensity method
        radiation_intensity = self.analyzer.measure_radiation_intensity(self.sample_image)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(radiation_intensity, dict)
        self.assertIn("average_intensity", radiation_intensity)
        self.assertIn("histogram", radiation_intensity)
        self.assertIn("bins", radiation_intensity)

    def test_create_radiation_affected_tissue(self):
        # Test the create_radiation_affected_tissue method
        radiation_tissue = self.analyzer.create_radiation_affected_tissue(self.sample_image, "TestRadiationTissue")

        # Check if the output is a RadiationAffectedTissue object
        from biobridge.definitions.tissues.radiation_affected import RadiationAffectedTissue
        self.assertIsInstance(radiation_tissue, RadiationAffectedTissue)
        self.assertEqual(radiation_tissue.name, "TestRadiationTissue")

    def test_create_bone_tissue_from_gamma(self):
        # Test the create_bone_tissue_from_gamma method
        bone_tissue = self.analyzer.create_bone_tissue_from_gamma(self.sample_image, "TestBoneTissue")

        # Check if the output is a BoneTissue object
        from biobridge.tools.xray_analyzer import BoneTissue
        self.assertIsInstance(bone_tissue, BoneTissue)
        self.assertEqual(bone_tissue.name, "TestBoneTissue")

    def test_compare_xray_and_gamma_bone_analysis(self):
        # Test the compare_xray_and_gamma_bone_analysis method
        xray_image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        gamma_image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        comparison = self.analyzer.compare_xray_and_gamma_bone_analysis(xray_image, gamma_image, "TestBone")

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(comparison, dict)
        self.assertIn("tissue_name", comparison)
        self.assertIn("xray_analysis", comparison)
        self.assertIn("gamma_analysis", comparison)
        self.assertIn("differences", comparison)

if __name__ == "__main__":
    unittest.main()
