# Biobridge

Showcase:
<a href="https://youtu.be/v-sujCAOxCQ">
<img src="biobridge.png" alt="Biobridge Logo">
</a>
Biobridge is a Python library for simulating biological processes and systems also analyzing them, visualising them, and interacting with them.

## Installation

Firstly you need to install pyrosetta

Then install biobridge

```sh
pip install biobridge
```

## Usage

To use Biobridge in your project, import it for example:

``` python
from biobridge import *
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
```

## The notable functions are:

```python
from biobridge import *

Cell()
DNA()
RNA()
Protein()
Chromosome()
Environment()
Tissue()
System()
ImageAnalyzer()
Orchestrator()
Virus()
Infection()
SQLDNAEncoder()
SurgicalSimulator()
```

To see more examples how to use biobridge see the test files, biobridge works well with jupyter notebooks.