from biobridge.tools.image_analyzer import ImageAnalyzer

image_analyzer = ImageAnalyzer()

training_data = [
    {'features': [0.7, 0.1, -100, -60, -40], 'protein_type': 'alpha_helical'},
    {'features': [0.2, 0.6, -80, -120, 110], 'protein_type': 'beta_sheet'},
]

image_analyzer.train_protein_classifier(training_data)
