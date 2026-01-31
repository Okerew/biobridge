from biobridge.tools.image_analyzer import ImageAnalyzer, np

analyzer = ImageAnalyzer()

image = analyzer.load_image("image_examples/01_POS002_D.TIF")
image_sequence = [
    analyzer.load_image(f"image_examples/image_{i}.TIF") 
    for i in range(2)
]
tracked_cells = cell_trajectories = analyzer.track_cell_movement(
    image_sequence
)
analyzer.plot_trajectories(tracked_cells, image)
segmented_image, num_labels = analyzer.segment_image(image)
analyzer.visualise_segmented_image(image, segmented_image, num_labels)
fluorescence_data = analyzer.measure_fluorescence(image)

primary_objects = analyzer.identify_primary_objects(image)

secondary_objects = analyzer.identify_secondary_objects(primary_objects)

primary_properties = analyzer.measure_object_properties(
    primary_objects, image
)
analyzer.visualize_measured_properties(image, primary_properties)
secondary_properties = analyzer.measure_object_properties(
    secondary_objects, image
)
grayscale_image = analyzer.grayscale_image(image)
analyzer.visualize_grayscale_image(grayscale_image)
nuclei_data = analyzer.analyze_nuclei(grayscale_image)
analyzer.visualize_nuclei(image, nuclei_data)
mitochondria_data = analyzer.analyze_mitochondria(grayscale_image)
analyzer.visualize_mitochondria(image, mitochondria_data)
potential_cancer_cells = analyzer.detect_potential_cancer(
    grayscale_image, nuclei_data
)
analyzer.visualize_cancer_cells(image, potential_cancer_cells)
print(potential_cancer_cells)

print(f"Number of primary objects: {len(primary_properties)}")
print(f"Number of secondary objects: {len(secondary_properties)}")
analysis_results = analyzer.analyze_cellular_objects(image)

primary_objects = analysis_results['primary_objects']
analyzer.visualize_primary_objects(image, primary_objects)
secondary_objects = analysis_results['secondary_objects']
analyzer.visualize_secondary_objects(image, secondary_objects)
tertiary_objects = analysis_results['tertiary_objects']
analyzer.visualize_tertiary_objects(image, tertiary_objects)

mean_primary_area = np.mean([obj['area'] for obj in primary_objects])
print(f"Mean area of primary objects: {mean_primary_area}")

mean_secondary_intensity = np.mean(
    [obj['mean_intensity'] for obj in secondary_objects]
)
print(f"Mean intensity of secondary objects: {mean_secondary_intensity}")
fluorescence_data = analyzer.measure_fluorescence(image)
analyzer.visualise_fluorescence(image, fluorescence_data)
analysis_result = analyzer.analyze_network_image(
    "image_examples/myplot.png"
)
analyzer.visualize_network_image("image_examples/myplot.png", 
                                 analysis_result)
print(analysis_result)
cells = analyzer.analyze_cells(image)
analyzer.display_cells(cells)
tissues = analyzer.analyze_and_create_tissues(
    "image_examples/01_POS002_D.TIF"
)
print(tissues)

print("\nTesting Neuron Analysis Functionality")

neurons = [cell for cell in cells if hasattr(cell, 'soma_diameter')]
if neurons:
    print(f"\nFound {len(neurons)} neuron(s) in the image")
    
    for i, neuron in enumerate(neurons):
        print(f"\n--- Neuron {i+1} ---")
        print(f"Type: {neuron.cell_type}")
        print(f"Soma diameter: {neuron.soma_diameter:.2f}")
        print(f"Axon length: {neuron.axon_length:.2f}")
        print(f"Dendrite count: {neuron.dendrite_count}")
        print(f"Synapse count: {neuron.synapse_count}")
        print(f"Myelin thickness: {neuron.myelin_thickness:.2f}")
        print(f"Neurotransmitters: {neuron.neurotransmitter_types}")
        print(f"Health: {neuron.health}%")
else:
    print("\nNo neurons detected in this image.")
    print("Testing neuron analysis with mock data...")
    
    if primary_properties and secondary_properties:
        test_nucleus = primary_properties[0]
        test_cell = secondary_properties[0]
        
        morphology = analyzer.analyze_neuron_morphology(
            image, test_nucleus, test_cell
        )
        print(f"\nNeuron Morphology Analysis:")
        print(f"  Soma diameter: {morphology['soma_diameter']:.2f}")
        print(f"  Process count: {morphology['process_count']}")
        print(
            f"  Total process length: "
            f"{morphology['total_process_length']:.2f}"
        )
        print(
            f"  Branch density: {morphology['branch_density']:.4f}"
        )
        
        myelination = analyzer.estimate_myelination(image, test_cell)
        print(f"\nMyelination Analysis:")
        print(f"  Is myelinated: {myelination['is_myelinated']}")
        print(
            f"  Myelin thickness: "
            f"{myelination['myelin_thickness']:.2f}"
        )
        print(
            f"  Myelination index: "
            f"{myelination['myelination_index']:.4f}"
        )
        
        synapse_data = analyzer.analyze_synaptic_markers(
            image, test_cell
        )
        print(f"\nSynaptic Analysis:")
        print(
            f"  Estimated synapse count: "
            f"{synapse_data['estimated_synapse_count']}"
        )
        print(
            f"  Synaptic density: "
            f"{synapse_data['synaptic_density']:.4f}"
        )
        print(f"  Puncta count: {synapse_data['puncta_count']}")
        
        neuron_type = analyzer.classify_neuron_type(
            morphology, synapse_data, myelination
        )
        print(f"\nClassified neuron type: {neuron_type}")
        
        neurotransmitters = analyzer.estimate_neurotransmitter_type(
            image, test_cell
        )
        print(f"Estimated neurotransmitters: {neurotransmitters}")
        
        mito_dist = analyzer.analyze_mitochondrial_distribution_neuron(
            image, test_cell
        )
        print(f"\nMitochondrial Distribution:")
        print(
            f"  Total mitochondria: "
            f"{mito_dist['total_mitochondria']}"
        )
        print(
            f"  Soma density: "
            f"{mito_dist['soma_mitochondrial_density']:.4f}"
        )
        print(
            f"  Process density: "
            f"{mito_dist['process_mitochondrial_density']:.4f}"
        )

neural_tissues = [t for t in tissues if hasattr(t, 'neural_density')]
if neural_tissues:
    print(f"\nNeural Tissue Analysis")
    print(f"Found {len(neural_tissues)} neural tissue(s)")
    
    for i, tissue in enumerate(neural_tissues):
        print(f"\n--- Neural Tissue {i+1} ---")
        print(f"Type: {tissue.tissue_type}")
        print(f"Neural density: {tissue.neural_density:.4f}")
        print(
            f"  Synaptic connectivity: "
            f"{tissue.synaptic_connectivity:.4f}"
        )
        print(
            f"  Myelination %: "
            f"{tissue.myelination_percentage * 100:.2f}%"
        )
        print(f"Vascularization: {tissue.vascularization:.2f}")
else:
    print("\nNo neural tissues detected in this image.")
    print("Testing with available tissue data...")
    
    if tissues and len(tissues) > 0:
        valid_tissues = [
            t for t in tissues if t.tissue_type != "undefined"
        ]
        print(f"\nFound {len(valid_tissues)} tissue(s) total")
        for i, tissue in enumerate(valid_tissues):
            print(f"\n--- Tissue {i+1} ---")
            print(f"Type: {tissue.tissue_type}")
            if hasattr(tissue, 'area'):
                print(f"Area: {tissue.area:.2f}")
            if hasattr(tissue, 'cell_count'):
                print(f"Cell count: {tissue.cell_count}")
            if hasattr(tissue, 'health'):
                print(f"Health: {tissue.health}%")

if len(cells) >= 2:
    print("\nNeural Connectivity Analysis")
    cell_props_for_connectivity = [
        {
            'centroid': (100 + i*50, 100 + i*50),
            'area': 500 + i*100
        }
        for i in range(min(5, len(cells)))
    ]
    
    connectivity = analyzer.analyze_neural_connectivity_patterns(
        cell_props_for_connectivity
    )
    
    if connectivity['network_metrics']:
        metrics = connectivity['network_metrics']
        print(
            f"Average connectivity: "
            f"{metrics['average_connectivity']:.4f}"
        )
        print(
            f"Average node degree: "
            f"{metrics['average_node_degree']:.2f}"
        )
        print(f"Network density: {metrics['network_density']:.4f}")
        print(f"Hub neuron indices: {metrics['hub_neuron_indices']}")

if neurons:
    print("\nNeural Health Assessment")
    health_markers = analyzer.assess_neural_health_markers(neurons)
    
    if health_markers:
        print(
            f"Average neuron health: "
            f"{health_markers['average_neuron_health']:.2f}%"
        )
        print(
            f"Synaptic health index: "
            f"{health_markers['synaptic_health_index']:.4f}"
        )
        print(
            f"Metabolic health index: "
            f"{health_markers['metabolic_health_index']:.4f}"
        )
        print(
            f"Myelination quality: "
            f"{health_markers['myelination_quality']:.4f}"
        )
        print(
            f"Overall neural health: "
            f"{health_markers['overall_neural_health']:.4f}"
        )
        print(
            f"Degeneration risk: "
            f"{health_markers['degeneration_risk']:.4f}"
        )

analyzer.close()
