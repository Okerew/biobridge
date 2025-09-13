import random
from biobridge.blocks.cell import Cell
from biobridge.blocks.protein import Protein
from biobridge.genes.dna import DNA
from biobridge.tools.orchestrator import Orchestrator, Tissue, NeuralNetwork, MetabolicNetwork, SignalingNetwork, GeneRegulatoryNetwork


# Helper function to create a sample DNA object
def create_sample_dna() -> DNA:
    sequence = "ATCGATCGATCGATCG"
    genes = [("gene1", 0, 4), ("gene2", 5, 9), ("gene3", 10, 14)]
    return DNA(sequence, genes)


# Helper function to create a sample protein
def create_sample_protein(name: str) -> Protein:
    return Protein(name, random.choice(["ATCG", "CGTA", "GATC", "TCGA"]))


# Helper function to create a sample cell
def create_sample_cell(name: str) -> Cell:
    return Cell(name, 'epithelial')


# Helper function to create a sample tissue
def create_sample_tissue(name: str, tissue_type: str, num_cells: int = 5) -> Tissue:
    cells = [create_sample_cell(f"Cell_{i}") for i in range(num_cells)]
    return Tissue(name, tissue_type, cells)


# Helper function to create a sample gene regulatory network
def create_sample_gene_network() -> GeneRegulatoryNetwork:
    receptors = [create_sample_protein(f"Receptor_{i}") for i in range(3)]
    proteins = [create_sample_protein(f"Protein_{i}") for i in range(5)]
    dna = create_sample_dna()
    interactions = {
        "Receptor_0": ["Protein_0", "Protein_1"],
        "Protein_0": ["Protein_2"],
        "Protein_1": ["Protein_3"],
        "Protein_2": ["Protein_4"]
    }
    binding_sites = {
        "Receptor_0": "ATCG",
        "Protein_0": "CGTA",
        "Protein_1": "GATC",
        "Protein_2": "TCGA",
        "Protein_3": "ATCG",
        "Protein_4": "CGTA"
    }
    return GeneRegulatoryNetwork(receptors, proteins, dna, interactions, binding_sites)


# Helper function to create a sample neural network
def create_sample_neural_network() -> NeuralNetwork:
    neural_network = NeuralNetwork()
    neural_network.add_neuron("Input_1", is_input=True)
    neural_network.add_neuron("Input_2", is_input=True)
    neural_network.add_neuron("Hidden_1")
    neural_network.add_neuron("Hidden_2")
    neural_network.add_neuron("Output_1", is_output=True)
    neural_network.add_synapse("Input_1", "Hidden_1", weight=0.5)
    neural_network.add_synapse("Input_2", "Hidden_1", weight=0.5)
    neural_network.add_synapse("Hidden_1", "Hidden_2", weight=0.5)
    neural_network.add_synapse("Hidden_2", "Output_1", weight=0.5)
    return neural_network


# Helper function to create a sample metabolic network
def create_sample_metabolic_network() -> MetabolicNetwork:
    metabolites = ["Metabolite_A", "Metabolite_B", "Metabolite_C", "Metabolite_D"]
    enzymes = ["Enzyme_1", "Enzyme_2"]
    reactions = [
        ("Enzyme_1", "Metabolite_A", "Metabolite_B"),
        ("Enzyme_2", "Metabolite_B", "Metabolite_C"),
        ("Enzyme_1", "Metabolite_C", "Metabolite_D")
    ]
    return MetabolicNetwork(metabolites, enzymes, reactions)


# Helper function to create a sample signaling network
def create_sample_signaling_network() -> SignalingNetwork:
    molecules = ["Molecule_A", "Molecule_B", "Molecule_C", "Molecule_D"]
    interactions = {
        "Molecule_A": ["Molecule_B"],
        "Molecule_B": ["Molecule_C"],
        "Molecule_C": ["Molecule_D"]
    }
    return SignalingNetwork(molecules, interactions)


# Main test function
def test_orchestrator():
    # Create sample tissues
    tissue1 = create_sample_tissue("Tissue_1", "epithelial")
    tissue2 = create_sample_tissue("Tissue_2", "connective")

    # Create sample networks
    gene_network = create_sample_gene_network()
    neural_network = create_sample_neural_network()
    metabolic_network = create_sample_metabolic_network()
    signaling_network = create_sample_signaling_network()

    # Create the orchestrator
    orchestrator = Orchestrator(
        tissues=[tissue1, tissue2],
        gene_networks=[gene_network],
        neural_networks=[neural_network],
        metabolic_networks=[metabolic_network],
        signaling_networks=[signaling_network]
    )
    orchestrator2 = Orchestrator(
        tissues=[tissue1, tissue2],
    )

    # Simulate tissues
    orchestrator2.simulate_tissues(external_factors=[("radiation", 0.2), ("nutrient", 0.5)])

    # Simulate gene networks
    orchestrator.simulate_gene_networks(inputs=["Input_Signal_1", "Input_Signal_2"])

    # Simulate neural networks
    orchestrator.simulate_neural_networks(input_signals={"Input_1": 0.8, "Input_2": 0.6})

    # Simulate metabolic networks
    orchestrator.simulate_metabolic_networks(input_metabolites={"Metabolite_A"}, steps=3)

    # Simulate signaling networks
    orchestrator.simulate_signaling_networks(molecule_list=["Molecule_A"], steps=3)

    # Visualize networks
    orchestrator.visualize_gene_networks()
    orchestrator.visualize_neural_networks()
    orchestrator.visualize_metabolic_networks()
    orchestrator.visualize_signaling_networks()
    print("Test completed successfully.")


if __name__ == "__main__":
    test_orchestrator()
