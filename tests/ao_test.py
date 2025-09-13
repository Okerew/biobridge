from biobridge.definitions.ao import AdvancedOrganism, DNA


def test_advanced_organism_neural_network():
    # Create an AdvancedOrganism object
    dna = DNA("ATCG")
    organism = AdvancedOrganism("Test Organism", dna)

    # Test setting up the neural network
    print(organism.describe())
    # Test preparing neural inputs
    inputs = organism.prepare_neural_inputs()
    print(inputs)

    # Test processing the neural network
    organism.process_neural_network()
    organism.adapt()
    organism.asexual_reproduce()
    print(organism.neural_network.getNeurons())


test_advanced_organism_neural_network()
