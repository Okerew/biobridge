from biobridge.blocks.cell import Cell
from biobridge.genes.dna import DNA
from biobridge.tools.cloner import Cloner


initial_dna_sequence = "ATCGATCGATCGATCG"
initial_dna = DNA(initial_dna_sequence)

# Create an initial cell with the DNA
initial_cell = Cell(
    name="InitialCell",
    cell_type="StemCell",
    dna=initial_dna,
    health=100,
    ph=7.4,
    osmolarity=300,
    ion_concentrations={}
)

# Clone the initial cell to form a tissue
tissue = Cloner.grow_tissue_from_cell(initial_cell, num_cells=5, degradation_rate=0.01)

# Print tissue details
print("Tissue Details:")
print(f"Name: {tissue.name}")
print(f"Tissue Type: {tissue.tissue_type}")
print(f"Number of Cells: {len(tissue.cells)}")
for cell in tissue.cells:
    print(f"Cell Name: {cell.name}, DNA Sequence: {cell.dna.sequence}")

# Clone the tissue to form a system
system = Cloner.grow_system_from_tissue(tissue, num_tissues=3, degradation_rate=0.01)

# Print system details
print("\nSystem Details:")
print(f"Name: {system.name}")
print(f"Number of Tissues: {len(system.tissues)}")
for tissue in system.tissues:
    print(f"Tissue Name: {tissue.name}, Number of Cells: {len(tissue.cells)}")
    for cell in tissue.cells:
        print(f"  Cell Name: {cell.name}, DNA Sequence: {cell.dna.sequence}")

# Verify DNA degradation
print("\nVerifying DNA Degradation:")
for tissue in system.tissues:
    for cell in tissue.cells:
        print(f"Cell Name: {cell.name}, DNA Sequence: {cell.dna.sequence}")
