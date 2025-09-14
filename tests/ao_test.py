from biobridge.definitions.ao import AdvancedOrganism, DNA


def test_advanced_organism_neural_network():
    # Create an AdvancedOrganism object
    dna = DNA("ATCG")
    organism = AdvancedOrganism("Test Organism", dna)

    # Test setting up the neural network
    print(organism.describe())

    organism.adapt()
    organism.asexual_reproduce()


test_advanced_organism_neural_network()
