import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import Delaunay
from stl import mesh
from biobridge.tools.image_analyzer import ImageAnalyzer, os
import pyrosetta
import py3Dmol
import cv2
import matplotlib.pyplot as plt
import mediapipe as mp
import webbrowser
import tempfile


class BodyPartAnalyzer(ImageAnalyzer):
    def __init__(self):
        super().__init__()
        self.body_part_models = {}  # Dictionary to store 3D models of body parts
        pyrosetta.init()  # Initialize PyRosetta
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

    def analyze_body_part(self, image_path, part_name):
        """
        Analyze a specific body part from an image.

        :param image_path: Path to the image file
        :param part_name: Name of the body part (e.g., 'hand', 'foot', 'leg')
        :return: Dictionary containing analysis results
        """
        image = self.load_image(image_path)
        segmented_image, num_segments = self.segment_image(image)

        contours = self.extract_contours(segmented_image)
        landmarks = self.detect_landmarks(image_path)
        measurements = self.calculate_measurements(contours, landmarks)

        return {
            'part_name': part_name,
            'contours': contours,
            'landmarks': landmarks,
            'measurements': measurements,
            'image_path': image_path
        }

    def extract_contours(self, segmented_image):
        """
        Extract contours from the segmented image.

        :param segmented_image: Segmented image array
        :return: List of contours
        """
        contours, _ = cv2.findContours(segmented_image.astype(np.uint8),
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def detect_landmarks(self, image_path):
        """
        Detect specific landmarks on the body part using MediaPipe.

        :param image_path: Input image path
        :return: Dictionary of detected landmarks or an empty dictionary if no landmarks are found
        """
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image not found or unable to load.")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        landmarks = {}

        # Dynamically check for the correct attribute
        if results and hasattr(results, 'pose_landmarks') and results.pose_landmarks is not None:
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if landmark:
                    landmarks[f'landmark_{idx}'] = (landmark.x, landmark.y, landmark.z)
        elif results and hasattr(results, 'pose_world_landmarks') and results.pose_world_landmarks is not None:
            for idx, landmark in enumerate(results.pose_world_landmarks.landmark):
                if landmark:
                    landmarks[f'landmark_{idx}'] = (landmark.x, landmark.y, landmark.z)
        else:
            print("No landmarks found in the results.")

        return landmarks

    def calculate_measurements(self, contours, landmarks):
        """
        Calculate key measurements of the body part.

        :param contours: List of contours
        :param landmarks: Dictionary of landmarks
        :return: Dictionary of measurements
        """
        measurements = {
            'perimeter': cv2.arcLength(contours[0], True),
            'area': cv2.contourArea(contours[0]),
        }

        for i, (name1, point1) in enumerate(landmarks.items()):
            for name2, point2 in list(landmarks.items())[i + 1:]:
                distance = np.linalg.norm(np.array(point1) - np.array(point2))
                measurements[f'{name1}_to_{name2}'] = distance

        return measurements

    def generate_3d_model(self, analysis_result, resolution=100):
        """
        Generate a 3D model based on the analysis result.

        :param analysis_result: Result from analyze_body_part method
        :param resolution: Resolution of the 3D model
        :return: 3D mesh object
        """
        # Stack contours and ensure it's a 2D array
        points = np.vstack(analysis_result['contours']).squeeze()

        # Check if points array is empty or has insufficient dimensions
        if points.ndim != 2 or points.shape[0] == 0:
            raise ValueError("No valid contour points found in analysis result.")

        # Determine the number of clusters
        n_clusters = min(resolution, len(points))

        # Fit KMeans only if there are enough points
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(points)
        reduced_points = kmeans.cluster_centers_

        # Create a point cloud by adding a z-coordinate (0)
        z = np.zeros((reduced_points.shape[0], 1))
        point_cloud = np.hstack((reduced_points, z))

        # Create a Delaunay triangulation
        tri = Delaunay(reduced_points)

        # Create the mesh
        body_part_mesh = mesh.Mesh(np.zeros(tri.simplices.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(tri.simplices):
            for j in range(3):
                body_part_mesh.vectors[i][j] = point_cloud[f[j], :]

        # Store the mesh in the body part models dictionary
        self.body_part_models[analysis_result['part_name']] = body_part_mesh

        return body_part_mesh

    def design_prosthetic(self, analysis_result, attachment_type='socket'):
        """
        Design a prosthetic based on the analysis result.

        :param analysis_result: Result from analyze_body_part method
        :param attachment_type: Type of attachment (e.g., 'socket', 'osseointegration')
        :return: Dictionary containing prosthetic design parameters
        """
        measurements = analysis_result['measurements']

        prosthetic_length = max(measurements.values())
        socket_circumference = measurements['perimeter']

        if analysis_result['part_name'] in ['hand', 'arm']:
            material = 'carbon fiber'
        elif analysis_result['part_name'] in ['foot', 'leg']:
            material = 'titanium'
        else:
            material = 'plastic'

        if attachment_type == 'socket':
            attachment = {
                'type': 'socket',
                'circumference': socket_circumference,
                'depth': prosthetic_length * 0.2
            }
        elif attachment_type == 'osseointegration':
            attachment = {
                'type': 'osseointegration',
                'implant_length': prosthetic_length * 0.1
            }

        return {
            'part_name': analysis_result['part_name'],
            'length': prosthetic_length,
            'material': material,
            'attachment': attachment,
            '3d_model': self.generate_3d_model(analysis_result)
        }

    def visualize_body_part(self, analysis_result):
        """
        Visualize the analyzed body part with contours and landmarks.

        :param analysis_result: Result from analyze_body_part method
        """
        image = self.load_image(analysis_result['image_path'])
        img_array = self.ij.py.from_java(image)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_array, cmap='gray')

        for contour in analysis_result['contours']:
            plt.plot(contour[:, 0], contour[:, 1], 'r-')

        for name, (x, y, z) in analysis_result['landmarks'].items():
            plt.plot(x, y, 'bo')
            plt.text(x, y, name, color='white', fontsize=8,
                     bbox=dict(facecolor='blue', alpha=0.5))

        plt.title(f"Analyzed Body Part: {analysis_result['part_name']}")
        plt.axis('off')
        plt.show()

    def visualize_prosthetic(self, prosthetic_design):
        """
        Visualize the designed prosthetic using py3Dmol in a web browser.

        :param prosthetic_design: Result from design_prosthetic method
        """
        print(f"Prosthetic Design for {prosthetic_design['part_name']}:")
        print(f"Length: {prosthetic_design['length']:.2f}")
        print(f"Material: {prosthetic_design['material']}")
        print(f"Attachment Type: {prosthetic_design['attachment']['type']}")

        # Create PDB-like string from the mesh
        mesh = prosthetic_design['3d_model']
        pdb_str = "ATOM      1  CA  ALA A   1    "
        for vector in mesh.vectors:
            for point in vector:
                pdb_str += f"{point[0]:8.3f}{point[1]:8.3f}{point[2]:8.3f}\n"

        # Set up the py3Dmol viewer
        viewer = py3Dmol.view(width=400, height=400)
        viewer.addModel(pdb_str, "pdb")
        viewer.setStyle({'sphere': {}})
        viewer.zoomTo()

        # Generate the HTML content
        html_content = f"""
        <html>
        <head>
            <script src="https://3dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
            <style>
                #container {{ width: 400px; height: 400px; position: relative; }}
                #info {{ font-family: Arial, sans-serif; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div id="container"></div>
            <div id="info">
                <h2>Prosthetic Design for {prosthetic_design['part_name']}</h2>
                <p>Length: {prosthetic_design['length']:.2f}</p>
                <p>Material: {prosthetic_design['material']}</p>
                <p>Attachment Type: {prosthetic_design['attachment']['type']}</p>
            </div>
            <script>
                {viewer.js()}
                $3Dmol.viewers[0].render();
            </script>
        </body>
        </html>
        """

        # Create a temporary HTML file to display the 3D viewer
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name

        # Open the temporary HTML file in the default web browser
        webbrowser.open('file://' + temp_path)

        print(f"Prosthetic design opened in your default web browser. Close the browser tab when done.")
        input("Press Enter to close the temporary file and exit...")

        # Clean up the temporary file
        os.unlink(temp_path)

    def analyze_and_design_prosthetic(self, image_path, part_name, attachment_type='socket'):
        """
        Analyze a body part and design a prosthetic replacement.

        :param image_path: Path to the image file
        :param part_name: Name of the body part
        :param attachment_type: Type of prosthetic attachment
        :return: Tuple of (analysis_result, prosthetic_design)
        """
        analysis_result = self.analyze_body_part(image_path, part_name)
        prosthetic_design = self.design_prosthetic(analysis_result, attachment_type)

        self.visualize_body_part(analysis_result)
        self.visualize_prosthetic(prosthetic_design)

        return analysis_result, prosthetic_design
