import unittest
import numpy as np
from unittest.mock import MagicMock
from biobridge.tools.angiography_analyzer import AngiographyAnalyzer

class TestAngiographyAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a mock image_analyzer
        self.mock_image_analyzer = MagicMock()
        self.mock_image_analyzer.ij.py.from_java.return_value = np.random.randint(0, 255, (128, 128), dtype=np.uint8)

        # Initialize AngiographyAnalyzer with the mock
        self.analyzer = AngiographyAnalyzer(self.mock_image_analyzer)

        # Create a sample angiography image (2D)
        self.sample_image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)

    def test_analyze_angiogram(self):
        # Test the analyze_angiogram method
        result = self.analyzer.analyze_angiogram(self.sample_image)

        # Check if the result is a dictionary and contains expected keys
        self.assertIsInstance(result, dict)
        self.assertIn("enhanced_image", result)
        self.assertIn("vessel_centerlines", result)
        self.assertIn("vessel_mask", result)
        self.assertIn("vessel_measurements", result)
        self.assertIn("stenosis_analysis", result)
        self.assertIn("aneurysm_analysis", result)
        self.assertIn("vascular_density", result)
        self.assertIn("collateral_vessels", result)

    def test_enhance_vessel_contrast(self):
        # Test the enhance_vessel_contrast method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(enhanced, np.ndarray)
        self.assertEqual(enhanced.shape, self.sample_image.shape)

    def test_detect_vessel_centerlines(self):
        # Test the detect_vessel_centerlines method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        centerlines = self.analyzer.detect_vessel_centerlines(enhanced)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(centerlines, np.ndarray)
        self.assertEqual(centerlines.shape, self.sample_image.shape)

    def test_segment_vessels(self):
        # Test the segment_vessels method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        vessel_mask = self.analyzer.segment_vessels(enhanced)

        # Check if the output is a NumPy array and has the same shape as the input
        self.assertIsInstance(vessel_mask, np.ndarray)
        self.assertEqual(vessel_mask.shape, self.sample_image.shape)

    def test_measure_vessel_parameters(self):
        # Test the measure_vessel_parameters method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        vessel_mask = self.analyzer.segment_vessels(enhanced)
        centerlines = self.analyzer.detect_vessel_centerlines(enhanced)
        measurements = self.analyzer.measure_vessel_parameters(vessel_mask, centerlines)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(measurements, dict)
        self.assertIn("vessel_count", measurements)
        self.assertIn("total_vessel_length", measurements)
        self.assertIn("vessel_segments", measurements)

    def test_detect_stenosis(self):
        # Test the detect_stenosis method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        vessel_mask = self.analyzer.segment_vessels(enhanced)
        centerlines = self.analyzer.detect_vessel_centerlines(enhanced)
        measurements = self.analyzer.measure_vessel_parameters(vessel_mask, centerlines)
        stenosis = self.analyzer.detect_stenosis(measurements)

        # Check if the output is a list
        self.assertIsInstance(stenosis, list)

    def test_detect_aneurysms(self):
        # Test the detect_aneurysms method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        vessel_mask = self.analyzer.segment_vessels(enhanced)
        aneurysms = self.analyzer.detect_aneurysms(vessel_mask)

        # Check if the output is a list
        self.assertIsInstance(aneurysms, list)

    def test_calculate_vascular_density(self):
        # Test the calculate_vascular_density method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        vessel_mask = self.analyzer.segment_vessels(enhanced)
        density = self.analyzer.calculate_vascular_density(vessel_mask)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(density, dict)
        self.assertIn("vessel_density_ratio", density)
        self.assertIn("vessel_pixel_count", density)
        self.assertIn("total_pixel_count", density)

    def test_detect_collateral_circulation(self):
        # Test the detect_collateral_circulation method
        enhanced = self.analyzer.enhance_vessel_contrast(self.sample_image)
        centerlines = self.analyzer.detect_vessel_centerlines(enhanced)
        collaterals = self.analyzer.detect_collateral_circulation(centerlines)

        # Check if the output is a dictionary and contains expected keys
        self.assertIsInstance(collaterals, dict)
        self.assertIn("network_clusters", collaterals)
        self.assertIn("potential_collaterals", collaterals)
        self.assertIn("clustering_labels", collaterals)

    def test_create_vascular_tissue_from_angiogram(self):
        # Test the create_vascular_tissue_from_angiogram method
        vascular_tissue = self.analyzer.create_vascular_tissue_from_angiogram(self.sample_image, "TestVascularTissue")

        # Check if the output is a VascularTissue object
        from biobridge.definitions.tissues.vascular import VascularTissue
        self.assertIsInstance(vascular_tissue, VascularTissue)
        self.assertEqual(vascular_tissue.name, "TestVascularTissue")

if __name__ == "__main__":
    unittest.main()
