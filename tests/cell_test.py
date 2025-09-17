from biobridge.blocks.cell import Cell, DNA, Protein, Chromosome, Organelle, Mitochondrion

# Create two proteins
protein1 = Protein("Protein A", "ACDEFGHIKLMNPQRSTVWY")
protein2 = Protein("Protein B", "YVWTSRQPNMLKIHGFEDCA")

# Define bindings for the proteins
protein1.add_binding("Site 1", "High")
protein2.add_binding("Site 3", "Medium")

# Create a cell with specific properties
cell1 = Cell(
    name="Cell X",
    cell_type="Epithelial Cell",
)

organelle = Mitochondrion(0.5, 100)

# Add organelles to the cell
cell1.add_organelle(organelle, quantity=10)
cell1.add_organelle(Organelle("Nucleus", 1), quantity=1)
cell1.add_organelle(Organelle("Ribosome", 100), quantity=100)
cell1.add_chromosome(Chromosome(DNA("ATCG" * 1000), "Chromosome 1"))

# Print cell details
print("Cell X Description:")
print(cell1)

# Simulate interactions between proteins and the cell
print("\nProtein A interacting with Cell X:")
cell1.interact_with_protein(protein1)

print("\nProtein B interacting with Cell X:")
cell1.interact_with_protein(protein2)

# Modify cell by adding another receptor and surface protein
cell1.add_receptor(Protein("Site 3", "YVWTSRQPNMLKIHGFEDCA"))
cell1.add_surface_protein(Protein("V", "YVWTSRQPNMLKIHGFEDCA"))

print("\nUpdated Cell X Description:")
print(cell1)

# Test interactions again after modifying the cell
print("\nProtein A interacting with Cell X after updates:")
cell1.interact_with_protein(protein1)

print("\nProtein B interacting with Cell X after updates:")
cell1.interact_with_protein(protein2)

cell = Cell("MyCell", cell_type="neuron", dna=DNA("ATCG" * 1000))
cell.add_chromosome(Chromosome(DNA("ATCG" * 1000), "Chromosome 1"))
cell.maintain_homeostasis()

# Simulate some cell processes
cell.add_receptor(Protein("Dopamine", "YVWTSRQPNMLKIHGFEDCA"))
cell.add_surface_protein(Protein("Ion channel", "YVWTSRQPNMLKIHGFEDCA"))
cell.add_organelle(organelle, 5)

cell.add_internal_protein(Protein("Protein A", "ACDEFGHIKLMNPQRSTVWY"))
cell.add_internal_protein(Protein("Protein B", "YVWTSRQPNMLKIHGFEDCA"))

# Remove an internal protein
cell.remove_internal_protein(Protein("Protein B", "YVWTSRQPNMLKIHGFEDCA"))

# Check the internal proteins
for i in range(len(cell.internal_proteins)):
    print(cell.internal_proteins[i].name)

# Simulate metabolism and division
for _ in range(10):
    cell.metabolize()

new_cell = cell.divide()
print(new_cell.describe())
new_cell.visualize_cell()

# Interact with a protein
protein = Protein("Growth factor", "ABCDEFG", [{"site": "Dopamine"}])
cell.interact_with_protein(protein)

# Describe the cell
print(cell)
cell.visualize_cell()

# Example usage
cell = Cell(name="ExampleCell", dna=DNA(sequence="ATCG"))
