import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock
from biobridge.tools.endoscopy_analyzer import EndoscopyAnalyzer

class TestEndoscopyAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a mock image_analyzer
        self.mock_image_analyzer = MagicMock()
        self.mock_image_analyzer.ij.py.from_java.return_value = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

        # Initialize EndoscopyAnalyzer with the mock
        self.analyzer = EndoscopyAnalyzer(self.mock_image_analyzer)

        # Create a sample RGB endoscopy image
        self.sample_image = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    def test_analyze_endoscopy_image(self):
        result = self.analyzer.analyze_endoscopy_image(self.sample_image, endoscopy_type="gastric")
        self.assertIsInstance(result, dict)
        self.assertIn("original_image", result)
        self.assertIn("enhanced_image", result)
        self.assertIn("tissue_segmentation", result)
        self.assertIn("abnormalities", result)
        self.assertIn("severity_scores", result)

    def test_enhance_endoscopy_image(self):
        enhanced = self.analyzer.enhance_endoscopy_image(self.sample_image)
        self.assertIsInstance(enhanced, np.ndarray)
        self.assertEqual(enhanced.shape, self.sample_image.shape)

    def test_segment_endoscopy_tissues(self):
        hsv_image = cv2.cvtColor(self.sample_image, cv2.COLOR_RGB2HSV)
        segmentation = self.analyzer.segment_endoscopy_tissues(hsv_image)
        self.assertIsInstance(segmentation, dict)
        self.assertIn("healthy_mucosa", segmentation)
        self.assertIn("inflamed", segmentation)

    def test_detect_endoscopy_edges(self):
        edges = self.analyzer.detect_endoscopy_edges(self.sample_image)
        self.assertIsInstance(edges, np.ndarray)
        self.assertEqual(len(edges.shape), 2)

    def test_analyze_texture_patterns(self):
        texture_analysis = self.analyzer.analyze_texture_patterns(self.sample_image)
        self.assertIsInstance(texture_analysis, dict)
        self.assertIn("lbp_histogram", texture_analysis)
        self.assertIn("glcm_contrast_mean", texture_analysis)

    def test_detect_abnormalities(self):
        hsv_image = cv2.cvtColor(self.sample_image, cv2.COLOR_RGB2HSV)
        segmentation = self.analyzer.segment_endoscopy_tissues(hsv_image)
        texture_analysis = self.analyzer.analyze_texture_patterns(self.sample_image)
        abnormalities = self.analyzer.detect_abnormalities(self.sample_image, hsv_image)
        self.assertIsInstance(abnormalities, list)

    def test_measure_endoscopy_features(self):
        hsv_image = cv2.cvtColor(self.sample_image, cv2.COLOR_RGB2HSV)
        segmentation = self.analyzer.segment_endoscopy_tissues(hsv_image)
        measurements = self.analyzer.measure_endoscopy_features(segmentation, self.sample_image)
        self.assertIsInstance(measurements, dict)
        self.assertIn("healthy_mucosa", measurements)

    def test_classify_tissue_health(self):
        hsv_image = cv2.cvtColor(self.sample_image, cv2.COLOR_RGB2HSV)
        segmentation = self.analyzer.segment_endoscopy_tissues(hsv_image)
        texture_analysis = self.analyzer.analyze_texture_patterns(self.sample_image)
        tissue_health = self.analyzer.classify_tissue_health(self.sample_image, segmentation, texture_analysis)
        self.assertIsInstance(tissue_health, dict)
        self.assertIn("overall_health_score", tissue_health)

    def test_detect_specific_conditions(self):
        hsv_image = cv2.cvtColor(self.sample_image, cv2.COLOR_RGB2HSV)
        segmentation = self.analyzer.segment_endoscopy_tissues(hsv_image)
        specific_findings = self.analyzer.detect_specific_conditions(segmentation, "gastric")
        self.assertIsInstance(specific_findings, dict)

    def test_calculate_severity_scores(self):
        hsv_image = cv2.cvtColor(self.sample_image, cv2.COLOR_RGB2HSV)
        segmentation = self.analyzer.segment_endoscopy_tissues(hsv_image)
        texture_analysis = self.analyzer.analyze_texture_patterns(self.sample_image)
        abnormalities = self.analyzer.detect_abnormalities(self.sample_image, hsv_image)
        tissue_health = self.analyzer.classify_tissue_health(self.sample_image, segmentation, texture_analysis)
        severity_scores = self.analyzer.calculate_severity_scores(abnormalities, tissue_health)
        self.assertIsInstance(severity_scores, dict)
        self.assertIn("overall_severity", severity_scores)

if __name__ == "__main__":
    unittest.main()
