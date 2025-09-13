from biobridge.tools.image_analyzer import ImageAnalyzer, np

analyzer = ImageAnalyzer()
# Load an image
image = analyzer.load_image("image_examples/01_POS002_D.TIF")
image_sequence = [analyzer.load_image(f"image_examples/image_{i}.TIF") for i in range(2)]
tracked_cells = cell_trajectories = analyzer.track_cell_movement(image_sequence)
analyzer.plot_trajectories(tracked_cells, image)
segmented_image, num_labels = analyzer.segment_image(image)
analyzer.visualise_segmented_image(image, segmented_image, num_labels)
fluorescence_data = analyzer.measure_fluorescence(image)
# Identify primary objects
primary_objects = analyzer.identify_primary_objects(image)

# Identify secondary objects
secondary_objects = analyzer.identify_secondary_objects(primary_objects)

# Measure properties
primary_properties = analyzer.measure_object_properties(primary_objects, image)
analyzer.visualize_measured_properties(image, primary_properties)
secondary_properties = analyzer.measure_object_properties(secondary_objects, image)

grayscale_image = analyzer.grayscale_image(image)
analyzer.visualize_grayscale_image(grayscale_image)
nuclei_data = analyzer.analyze_nuclei(grayscale_image)
analyzer.visualize_nuclei(image, nuclei_data)
mitochondria_data = analyzer.analyze_mitochondria(grayscale_image)
analyzer.visualize_mitochondria(image, mitochondria_data)
potential_cancer_cells = analyzer.detect_potential_cancer(grayscale_image, nuclei_data)
analyzer.visualize_cancer_cells(image, potential_cancer_cells)
print(potential_cancer_cells)
# Print some results
print(f"Number of primary objects: {len(primary_properties)}")
print(f"Number of secondary objects: {len(secondary_properties)}")

analysis_results = analyzer.analyze_cellular_objects(image)

# Access the results
primary_objects = analysis_results['primary_objects']
analyzer.visualize_primary_objects(image, primary_objects)
secondary_objects = analysis_results['secondary_objects']
analyzer.visualize_secondary_objects(image, secondary_objects)
tertiary_objects = analysis_results['tertiary_objects']
analyzer.visualize_tertiary_objects(image, tertiary_objects)

# Example: Print the mean area of primary objects (e.g., nuclei)
mean_primary_area = np.mean([obj['area'] for obj in primary_objects])
print(f"Mean area of primary objects: {mean_primary_area}")

# Example: Print the mean intensity of secondary objects (e.g., cell bodies)
mean_secondary_intensity = np.mean([obj['mean_intensity'] for obj in secondary_objects])
print(f"Mean intensity of secondary objects: {mean_secondary_intensity}")

fluorescence_data = analyzer.measure_fluorescence(image)
analyzer.visualise_fluorescence(image, fluorescence_data)

analysis_result =analyzer.analyze_network_image("image_examples/myplot.png")
analyzer.visualize_network_image("image_examples/myplot.png", analysis_result)
print(analysis_result)
cells = analyzer.analyze_cells(image)
analyzer.display_cells(cells)

tissues = analyzer.analyze_and_create_tissues("image_examples/01_POS002_D.TIF")
print(tissues)
# Close the ImageJ instance
analyzer.close()
