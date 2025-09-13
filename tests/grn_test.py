from biobridge.blocks.protein import Protein
from biobridge.networks.grn import GeneRegulatoryNetwork
from biobridge.genes.dna import DNA

receptor1 = Protein("Receptor A", "ACGT")
receptor2 = Protein("Receptor B", "TGCA")
protein21 = Protein("Protein C", "GATC")
protein2 = Protein("Protein D", "CTAG")
protein21.save_protein("proteinC.pt")
protein1 = Protein.load_protein("proteinC.pt")
# Define interactions
interactions = {
    "Receptor A": ["Protein C"],
    "Protein C": ["Protein D"],
    "Receptor B": ["Protein D"]
}

# Define binding sites
binding_sites = {
    "Receptor A": "ACGT",
    "Receptor B": "TGCA",
    "Protein C": "GATC",
    "Protein D": "CTAG"
}

# Create DNA with genes
dna_sequence = "ATGCGTACGTGATCGTACGATCGTAGCTAGCTAGCGTAGCTGATCGTACG"
dna = DNA(sequence=dna_sequence)
dna.add_gene("Gene 1", 0, 20)  # Contains ACGT (Receptor A binding site)
dna.add_gene("Gene 2", 21, 40)  # Contains GATC (Protein C binding site)

# Create the Gene Regulatory Network
grn = GeneRegulatoryNetwork(
    receptors=[receptor1, receptor2],
    proteins=[protein1, protein2],
    dna=dna,
    interactions=interactions,
    binding_sites=binding_sites
)

print(grn.__getattribute__('interactions'))

# Predict output based on input signals
inputs = ["Receptor A", "Receptor B"]
regulated_genes = grn.predict_output(inputs)

print(f"Regulated genes: {regulated_genes}")

# Save the network to a file
grn.save_network('network.pkl')

# Load the network from a file
loaded_network = GeneRegulatoryNetwork.load_network('network.pkl')

# Use the loaded network
loaded_network.predict_output(inputs)
print(grn.to_json())