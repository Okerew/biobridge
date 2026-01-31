from biobridge.definitions.tissues.neural import NeuralTissue, Neuron

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_dict(data, indent=0):
    for key, value in data.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_dict(value, indent + 1)
        elif isinstance(value, list):
            if len(value) > 5:
                print("  " * indent + f"{key}: [{len(value)} items]")
            else:
                print("  " * indent + f"{key}: {value}")
        elif isinstance(value, float):
            print("  " * indent + f"{key}: {value:.4f}")
        else:
            print("  " * indent + f"{key}: {value}")


def test_neuron():
    print_section("NEURON CLASS TESTS")
    
    print("\n1. Creating a myelinated motor neuron...")
    motor_neuron = Neuron(
        name="Motor_Neuron_1",
        soma_diameter=25.0,
        axon_length=1500.0,
        axon_diameter=2.0,
        dendrite_count=7,
        dendrite_branch_density=0.8,
        myelin_thickness=1.5,
        synapse_count=1200,
        neurotransmitter_types=["acetylcholine"]
    )
    
    print(f"Created: {motor_neuron.name}")
    print(f"Cell type: {motor_neuron.cell_type}")
    print(f"Health: {motor_neuron.health}")
    print(f"Age: {motor_neuron.age}")
    
    print("\n2. Neuron Morphometry:")
    morphometry = motor_neuron.get_neuron_morphometry()
    print_dict(morphometry)
    
    print("\n3. Electrophysiological Properties:")
    electrophys = motor_neuron.get_electrophysiological_properties()
    print_dict(electrophys)
    
    print("\n4. Synaptic Properties:")
    synaptic = motor_neuron.get_synaptic_properties()
    print_dict(synaptic)
    
    print("\n5. Metabolic Rate:")
    metabolism = motor_neuron.neuron_metabolic_rate()
    print_dict(metabolism)
    
    print("\n6. Mitochondrial Distribution:")
    mito_dist = motor_neuron.calculate_mitochondrial_distribution()
    print_dict(mito_dist)
    
    print("\n7. Structural Protein Content:")
    proteins = motor_neuron.neuron_structural_protein_content()
    print_dict(proteins)
    
    print("\n8. Creating an unmyelinated interneuron...")
    interneuron = Neuron(
        name="Interneuron_1",
        soma_diameter=15.0,
        axon_length=300.0,
        axon_diameter=0.5,
        dendrite_count=12,
        dendrite_branch_density=0.9,
        myelin_thickness=0.0,
        synapse_count=800,
        neurotransmitter_types=["GABA"]
    )
    
    print(f"Created: {interneuron.name}")
    print(f"Conduction velocity: "
          f"{interneuron.calculate_conduction_velocity():.4f} m/s")
    print(f"Myelination index: {interneuron.myelination_index():.4f}")
    
    print("\n9. Simulating neuron aging (100 time steps)...")
    aging_result = motor_neuron.neuron_aging_simulation(100)
    print_dict(aging_result)
    
    print("\n10. Neurodegeneration Markers:")
    degen_markers = motor_neuron.assess_neurodegeneration_markers()
    print_dict(degen_markers)
    
    return motor_neuron, interneuron


def test_neural_tissue():
    print_section("NEURAL TISSUE CLASS TESTS")
    
    print("\n1. Creating neural tissue with multiple neurons...")
    neural_tissue = NeuralTissue(
        name="Cortical_Layer_III",
        neural_density=1.2,
        synaptic_connectivity=0.75,
        myelination_percentage=0.6,
        vascularization=0.85
    )
    
    print(f"Created tissue: {neural_tissue.name}")
    print(f"Tissue type: {neural_tissue.tissue_type}")
    
    print("\n2. Adding neurons to the tissue...")
    for i in range(50):
        if i % 5 == 0:
            neuron = Neuron(
                name=f"Pyramidal_Neuron_{i}",
                soma_diameter=20.0,
                axon_length=2000.0,
                axon_diameter=1.5,
                dendrite_count=8,
                dendrite_branch_density=0.85,
                myelin_thickness=1.2,
                synapse_count=1500,
                neurotransmitter_types=["glutamate"]
            )
        else:
            neuron = Neuron(
                name=f"Neuron_{i}",
                soma_diameter=15.0,
                axon_length=500.0,
                axon_diameter=0.8,
                dendrite_count=6,
                dendrite_branch_density=0.7,
                myelin_thickness=0.5,
                synapse_count=900,
                neurotransmitter_types=["glutamate", "GABA"]
            )
        neural_tissue.add_cell(neuron)
    
    print(f"Total neurons in tissue: {neural_tissue.get_cell_count()}")
    print(f"Average cell health: "
          f"{neural_tissue.get_average_cell_health():.2f}")
    
    print("\n3. Network Connectivity Analysis:")
    connectivity = neural_tissue.calculate_network_connectivity()
    print_dict(connectivity)
    
    print("\n4. Gray Matter Density:")
    gray_matter = neural_tissue.calculate_gray_matter_density()
    print_dict(gray_matter)
    
    print("\n5. White Matter Integrity:")
    white_matter = neural_tissue.assess_white_matter_integrity()
    print_dict(white_matter)
    
    print("\n6. Myelination Coverage:")
    myelination = neural_tissue.calculate_myelination_coverage()
    print_dict(myelination)
    
    print("\n7. Simulating wave propagation...")
    wave_result = neural_tissue.propagate_wave(
        initiation_site=0,
        wave_type="excitatory",
        intensity=1.0
    )
    print(f"Wave type: {wave_result['wave_type']}")
    print(f"Initiation site: {wave_result['initiation_site']}")
    print(f"Affected neurons: {wave_result['affected_neuron_count']}")
    print(f"Max distance: {wave_result['max_distance']}")
    print(f"Average intensity: {wave_result['average_intensity']:.4f}")
    
    print("\n8. Simulating oscillatory activity (40 Hz, gamma band)...")
    oscillation = neural_tissue.simulate_oscillatory_activity(
        frequency=40.0,
        duration=50,
        synchronization=0.7
    )
    print(f"Frequency: {oscillation['frequency']} Hz")
    print(f"Duration: {oscillation['duration']} ms")
    print(f"Participating neurons: {oscillation['participating_neurons']}")
    print(f"Coherence: {oscillation['coherence']:.4f}")
    print(f"Power: {oscillation['power']:.4f}")
    
    print("\n9. Neurotransmitter System Analysis:")
    nt_systems = neural_tissue.neurotransmitter_system_analysis()
    print_dict(nt_systems)
    
    print("\n10. Glial Cell Distribution:")
    glial = neural_tissue.glial_cell_distribution()
    print_dict(glial)
    
    print("\n11. Blood-Brain Barrier Assessment:")
    bbb = neural_tissue.blood_brain_barrier_assessment()
    print_dict(bbb)
    
    print("\n12. Neural Tissue Metabolism:")
    metabolism = neural_tissue.neural_tissue_metabolism()
    print_dict(metabolism)
    
    print("\n13. Neuroplasticity Assessment:")
    plasticity = neural_tissue.neuroplasticity_assessment()
    print_dict(plasticity)
    
    print("\n14. Axonal Transport Efficiency:")
    transport = neural_tissue.axonal_transport_efficiency()
    print_dict(transport)
    
    print("\n15. Neuroinflammation Markers:")
    inflammation = neural_tissue.neuroinflammation_markers()
    print_dict(inflammation)
    
    print("\n16. Neurodegenerative Pathology:")
    pathology = neural_tissue.neurodegenerative_pathology()
    print_dict(pathology)
    
    print("\n17. Tissue Biomechanics:")
    biomechanics = neural_tissue.tissue_biomechanics()
    print_dict(biomechanics)
    
    print("\n18. Comprehensive Neural Assessment:")
    assessment = neural_tissue.comprehensive_neural_assessment()
    print("\nMorphology Summary:")
    print(f"  Gray matter volume: "
          f"{assessment['morphology']['gray_matter']['total_gray_matter_volume']:.2f}")
    print(f"  White matter integrity: "
          f"{assessment['morphology']['white_matter']['axonal_integrity']:.2f}")
    print(f"  Myelination coverage: "
          f"{assessment['morphology']['myelination']['coverage_percentage']:.2f}%")
    
    print("\nConnectivity Summary:")
    print(f"  Network density: "
          f"{assessment['connectivity']['network']['connectivity_density']:.6f}")
    print(f"  Synaptic density: "
          f"{assessment['connectivity']['synaptic_density']:.4f}")
    print(f"  Conduction velocity: "
          f"{assessment['connectivity']['conduction_velocity']:.2f} m/s")
    
    print("\nMetabolism Summary:")
    print(f"  Total ATP demand: "
          f"{assessment['metabolism']['total_atp_demand']:.2f}")
    print(f"  Glucose consumption: "
          f"{assessment['metabolism']['glucose_consumption']:.2f}")
    print(f"  Oxygen consumption: "
          f"{assessment['metabolism']['oxygen_consumption']:.2f}")
    
    print("\nCellular Health Summary:")
    print(f"  Average health: "
          f"{assessment['cellular_health']['average_health']:.2f}")
    print(f"  Overall degeneration: "
          f"{assessment['cellular_health']['degeneration']['overall_degeneration']:.4f}")
    print(f"  Inflammation index: "
          f"{assessment['cellular_health']['inflammation']['inflammation_index']:.4f}")
    
    return neural_tissue


def main():
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  NEURON AND NEURAL TISSUE TEST SUITE".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    try:
        motor_neuron, interneuron = test_neuron()
        
        neural_tissue = test_neural_tissue()
        
        print_section("TEST SUMMARY")
        print("\nAll tests completed successfully!")
        print(f"\nCreated objects:")
        print(f"  - {motor_neuron.name} (myelinated motor neuron)")
        print(f"  - {interneuron.name} (unmyelinated interneuron)")
        print(f"  - {neural_tissue.name} (tissue with "
              f"{neural_tissue.get_cell_count()} neurons)")
        
        print("\nKey findings:")
        print(f"  - Motor neuron conduction velocity: "
              f"{motor_neuron.calculate_conduction_velocity():.2f} m/s")
        print(f"  - Interneuron conduction velocity: "
              f"{interneuron.calculate_conduction_velocity():.2f} m/s")
        print(f"  - Tissue average health: "
              f"{neural_tissue.get_average_cell_health():.2f}%")
        print(f"  - Total synapses in tissue: "
              f"{neural_tissue.calculate_total_synapses():,}")
        
    except Exception as e:
        print(f"\nERROR during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
