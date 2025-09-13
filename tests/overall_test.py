from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell, Mitochondrion, Organelle

# Define proteins
protein1 = Protein("Protein A", "ACDEFGHIKLMNPQRSTVWY", id=1)
print(protein1.get_id())
protein2 = Protein("Protein B", "YVWTSRQPNMLKIHGFEDCA")
protein1.predict_structure()
# Define interactions
protein1.add_interaction(protein2, "inhibition", "strong")
protein2.add_interaction(protein1, "activation", "moderate")

# Define bindings
protein1.add_binding("Site 1", "High")
protein2.add_binding("Site 2", "Medium")
protein1.display_3d_structure()

properties = protein1.calculate_properties()
print(f"Molecular Weight: {properties['molecular_weight']:.2f} Da")
print(f"Isoelectric Point: {properties['isoelectric_point']:.2f}")
print(str(protein1))

# Define a cell
cell = Cell("Cell X")
cell.add_receptor(Protein("Site 1", "ACDEFGHIKLMNPQRSTVWY"))
cell.add_receptor(Protein("Site 3", "YVWTSRQPNMLKIHGFEDCA"))
custom_weights = {
    'water': 1e12,  # 1 trillion Daltons
    'cell_membrane': 2e9,  # 2 billion Daltons
    'organelles': 5e11,  # 500 billion Daltons
    'cell_volume': 1e12,  # 1 trillion Daltons
}

organelle = Mitochondrion(0.5, 100)
cell.add_organelle(organelle, quantity=10)
organelle2 = Organelle("nucleus", 100)
cell.add_organelle(organelle2, quantity=10)
print(cell.organelles)
print(f"Molecular weight of the cell: {cell.calculate_molecular_weight(custom_weights)}")

# Simulate protein interaction with the cell
print(protein1.interact_with_cell(cell))
print(protein2.interact_with_cell(cell))

# Mutate sequence
print("Original Sequence:", protein1.sequence)
protein1.mutate_sequence(2, 'W')
print("Mutated Sequence:", protein1.sequence)

# Calculate properties
properties = protein1.calculate_properties()
print(f"Protein Length: {properties['length']}")
print(f"Molecular Weight: {properties['molecular_weight']:.2f} Da")

# Simulate interactions
protein1.simulate_interactions()
print(protein1.to_json())

print(cell.to_dict())
