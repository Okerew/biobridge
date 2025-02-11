import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from biobridge.tools.bpa import BodyPartAnalyzer


class TestBodyPartAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = BodyPartAnalyzer()
        self.mock_image_path = 'mock_image_path.jpg'
        self.mock_part_name = 'hand'
        self.mock_image = np.zeros((100, 100))
        self.mock_segmented_image = np.zeros((100, 100))
        self.mock_contours = [np.array([[0, 0], [0, 1], [1, 1], [1, 0]])]
        self.mock_landmarks = {'landmark_1': (0, 0, 0), 'landmark_2': (1, 1, 1)}
        self.mock_measurements = {'perimeter': 4, 'area': 1, 'landmark_1_to_landmark_2': np.sqrt(3)}
        self.mock_analysis_result = {
            'part_name': self.mock_part_name,
            'contours': self.mock_contours,
            'landmarks': self.mock_landmarks,
            'measurements': self.mock_measurements,
            'image_path': self.mock_image_path
        }
        self.mock_prosthetic_design = {
            'part_name': self.mock_part_name,
            'length': 2,
            'material': 'carbon fiber',
            'attachment': {'type': 'socket', 'circumference': 4, 'depth': 0.4},
            '3d_model': None
        }
        self.mock_mesh = MagicMock()

    @patch('biobridge.tools.bpa.BodyPartAnalyzer.load_image')
    @patch('biobridge.tools.bpa.BodyPartAnalyzer.segment_image')
    def test_analyze_body_part(self, mock_segment_image, mock_load_image):
        mock_load_image.return_value = self.mock_image
        mock_segment_image.return_value = self.mock_segmented_image, 1
        self.analyzer.extract_contours = MagicMock(return_value=self.mock_contours)
        self.analyzer.detect_landmarks = MagicMock(return_value=self.mock_landmarks)
        self.analyzer.calculate_measurements = MagicMock(return_value=self.mock_measurements)

        result = self.analyzer.analyze_body_part(self.mock_image_path, self.mock_part_name)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['part_name'], self.mock_part_name)
        self.assertEqual(result['image_path'], self.mock_image_path)
        self.assertEqual(result['contours'], self.mock_contours)
        self.assertEqual(result['landmarks'], self.mock_landmarks)
        self.assertEqual(result['measurements'], self.mock_measurements)

    def test_extract_contours(self):
        contours = self.analyzer.extract_contours(self.mock_segmented_image)
        self.assertTrue(all(isinstance(contour, np.ndarray) for contour in contours))

    def test_calculate_measurements(self):
        measurements = self.analyzer.calculate_measurements(self.mock_contours, self.mock_landmarks)
        self.assertIsInstance(measurements, dict)
        self.assertIn('perimeter', measurements)
        self.assertIn('area', measurements)
        self.assertIn('landmark_1_to_landmark_2', measurements)

    def test_generate_3d_model(self):
        mesh = self.analyzer.generate_3d_model(self.mock_analysis_result)
        self.assertIsNotNone(mesh)

    def test_design_prosthetic(self):
        design = self.analyzer.design_prosthetic(self.mock_analysis_result)
        self.assertIsInstance(design, dict)
        self.assertEqual(design['part_name'], self.mock_part_name)
        self.assertEqual(design['length'], 4)
        self.assertEqual(design['material'], 'carbon fiber')
        self.assertEqual(design['attachment']['type'], 'socket')
        self.assertEqual(design['attachment']['circumference'], 4)
        self.assertEqual(design['attachment']['depth'], 0.8)

    @patch('biobridge.tools.bpa.BodyPartAnalyzer.load_image')
    @patch('matplotlib.pyplot.show')
    def test_visualize_body_part(self, mock_show, mock_load_image):
        mock_load_image.return_value = self.mock_image
        self.analyzer.visualize_body_part(self.mock_analysis_result)
        mock_show.assert_called_once()

    @patch('biobridge.tools.bpa.BodyPartAnalyzer.analyze_body_part')
    @patch('biobridge.tools.bpa.BodyPartAnalyzer.design_prosthetic')
    @patch('biobridge.tools.bpa.BodyPartAnalyzer.visualize_body_part')
    @patch('biobridge.tools.bpa.BodyPartAnalyzer.visualize_prosthetic')
    def test_analyze_and_design_prosthetic(self, mock_visualize_prosthetic, mock_visualize_body_part, mock_design_prosthetic, mock_analyze_body_part):
        mock_analyze_body_part.return_value = self.mock_analysis_result
        mock_design_prosthetic.return_value = self.mock_prosthetic_design
        analysis_result, prosthetic_design = self.analyzer.analyze_and_design_prosthetic(self.mock_image_path, self.mock_part_name)
        self.assertEqual(analysis_result, self.mock_analysis_result)
        self.assertEqual(prosthetic_design, self.mock_prosthetic_design)
        mock_visualize_body_part.assert_called_once_with(self.mock_analysis_result)
        mock_visualize_prosthetic.assert_called_once_with(self.mock_prosthetic_design)

    @patch('biobridge.tools.bpa.BodyPartAnalyzer.generate_3d_model')
    def test_visualize_prosthetic(self, mock_generate_3d_model):
        mock_generate_3d_model.return_value = self.mock_mesh
        design = self.analyzer.design_prosthetic(self.mock_analysis_result)
        self.analyzer.visualize_prosthetic(design)
        mock_generate_3d_model.assert_called_once_with(self.mock_analysis_result)
