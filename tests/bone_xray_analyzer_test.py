import numpy as np
import cv2
from biobridge.tools.xray_analyzer import XrayAnalyzer
from biobridge.tools.image_analyzer import ImageAnalyzer
from biobridge.definitions.tissues.bone import BoneTissue


# Create a mock image (grayscale)
mock_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)

# Create an instance of XrayAnalyzer
image_analyzer = ImageAnalyzer()
xray_analyzer = XrayAnalyzer(image_analyzer)

# Analyze the mock image
analysis_results = xray_analyzer.analyze_xray(mock_image)

# Print the analysis results
print("Enhanced Image Shape:", analysis_results['enhanced_image'].shape)
print("Edges Shape:", analysis_results['edges'].shape)
print("Segmented Image Shape:", analysis_results['segmented_image'].shape)
print("Anomalies:", analysis_results['anomalies'])
print("Bone Density:", analysis_results['bone_density'])

# Visualize the analysis results
xray_analyzer.visualize_xray_analysis(mock_image, analysis_results)

# Create a BoneTissue object from the analysis results
tissue_name = "TestBoneTissue"
bone_tissue = xray_analyzer.create_bone_tissue_from_xray(analysis_results, tissue_name)

# Print the BoneTissue object details
print("Bone Tissue Name:", bone_tissue.name)
print("Bone Tissue Cells:", [cell.name for cell in bone_tissue.cells])
print("Bone Tissue Cancer Risk:", bone_tissue.cancer_risk)
print("Bone Tissue Mineral Density:", bone_tissue.mineral_density)
print("Bone Tissue Osteoclast Activity:", bone_tissue.osteoclast_activity)
print("Bone Tissue Osteoblast Activity:", bone_tissue.osteoblast_activity)
