from biobridge.genes.dna import DNA
from biobridge.blocks.cell import Cell
from biobridge.blocks.cell import Organelle, Protein, Mitochondrion

# Create DNA for the cell
dna_sequence = "ATGCGTACTGATCGTACGATCGTAGCTAGCTAGCGTAGCTGATCGTACG"
dna = DNA(sequence=dna_sequence)
dna.add_gene("Gene 1","ATGATCGATCG", inheritance="dominant")
dna.add_gene("Gene 2","ATGATCGATCG", inheritance="mixed")

dna2 = DNA("ATGCGTACTGATCGTACGATCGTAGCTAGCTAGCGTAGCTGATCGTACG")
dna2.add_gene("Gene 1", "ATGATCGATCG", inheritance="recessive")
dna2.add_gene("Gene 2", "ATGATCGATCG", inheritance="mixed")
dna2.create_gene_heatmap()
dna.remove_gene("Gene 1")

# Create a cell with the DNA
cell1 = Cell(
    name="Cell X",
    cell_type="Epithelial Cell",
    receptors=[Protein("A", "ATGATCGATCG"), Protein("B", "ATGATCGATCG")],
    surface_proteins=[Protein("B", "ATGATCGATCG"), Protein("C", "ATGATCGATCG")],
    dna=dna
)

# Add organelles to the cell
cell1.add_organelle(Mitochondrion(0.5, 100), quantity=10)
cell1.add_organelle(Organelle("Nucleus", 1), quantity=1)
cell1.add_organelle(Organelle("Ribosome", 100), quantity=100)

# Print cell details including DNA
print("Cell X Description:")
print(cell1)

# Create two proteins
protein1 = Protein("Protein A", "ACDEFGHIKLMNPQRSTVWY")
protein2 = Protein("Protein B", "YVWTSRQPNMLKIHGFEDCA")

# Define bindings for the proteins
protein1.add_binding("Site 1", "High")
protein2.add_binding("Site 3", "Medium")

# Simulate interactions between proteins and the cell
print("\nProtein A interacting with Cell X:")
cell1.interact_with_protein(protein1)

print("\nProtein B interacting with Cell X:")
cell1.interact_with_protein(protein2)

# Modify DNA sequence
print("\nMutating DNA...")
cell1.dna.mutate(10, 'G')
cell1.dna.random_mutate()
cell1.dna.absolute_random_mutate(1)
print("Updated DNA Sequence:")
print(cell1.dna)

enzyme_sites = {'EcoRI': 'GAATTC', 'BamHI': 'GGATCC'}
dna.add_gene("Gene 1","ATGATCGATCG", inheritance="dominant")
print(dna.gc_content())
print(dna.find_repeats())
print(dna.find_palindromes())
print(dna.find_motif("ATC"))
print(dna.codon_usage())
print(dna.calculate_nucleotide_frequency())
print(dna.find_restriction_sites(enzyme_sites))
print(dna.find_orfs())
print(dna.hamming_distance(dna2))
print(dna.translate())
print(dna.describe())

# Store some binary data
binary_data = "1010101100110101"
dna.store_binary_data(binary_data)

print(f"DNA sequence: {dna.sequence}")

# Retrieve the binary data
retrieved_data = dna.retrieve_binary_data()
print(f"Retrieved binary data: {retrieved_data}")

# Verify that the retrieved data matches the original
print(f"Data matches: {binary_data == retrieved_data}")

print(dna.to_json())
