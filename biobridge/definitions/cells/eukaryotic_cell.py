from typing import List, Dict, Optional, Tuple
from biobridge.blocks.cell import Cell, DNA, Protein
import matplotlib.pyplot as plt
import json
from biobridge.definitions.chromosome_pair import ChromosomePair


class CellCore:
    def __init__(self, chromosome_pairs: Optional[List[ChromosomePair]] = None):
        self.chromosome_pairs = chromosome_pairs or []

    def add_chromosome_pair(self, chromosome_pair: ChromosomePair):
        self.chromosome_pairs.append(chromosome_pair)

    def remove_chromosome_pair(self, pair_name: str):
        self.chromosome_pairs = [pair for pair in self.chromosome_pairs if pair.name != pair_name]

    def mutate(self):
        for pair in self.chromosome_pairs:
            pair.mutate()

    def replicate(self) -> 'CellCore':
        new_chromosome_pairs = [pair.replicate() for pair in self.chromosome_pairs]
        return CellCore(new_chromosome_pairs)

    def to_dict(self) -> dict:
        return {
            'chromosome_pairs': [pair.to_dict() for pair in self.chromosome_pairs]
        }

    @classmethod
    def from_dict(cls, core_dict: dict) -> 'CellCore':
        chromosome_pairs = [ChromosomePair.from_dict(pair) for pair in core_dict['chromosome_pairs']]
        return cls(chromosome_pairs)


class EukaryoticCell(Cell):
    def __init__(
        self,
        name: str,
        dna: Optional['DNA'] = None,
        cell_type: Optional[str] = None,
        receptors: Optional[List[Protein]] = None,
        surface_proteins: Optional[List[Protein]] = None,
        organelles: Optional[Dict[str, int]] = None,
        chromosome_pairs: Optional[List[ChromosomePair]] = None,
        health: Optional[int] = None,
        age: Optional[int] = 0,
        metabolism_rate: Optional[float] = 1.0,
        ph: float = 7.0,
        osmolarity: float = 300.0,
        ion_concentrations: Optional[Dict[str, float]] = None,
        id: Optional[int] = None,
        structural_integrity: float = 100.0,
        mutation_count: Optional[int] = 0,
        growth_rate: Optional[float] = 1.0,
        repair_rate: Optional[float] = 1.0,
        max_divisions: Optional[int] = 50
    ):

        super().__init__(
            name=name,
            cell_type=cell_type,
            receptors=receptors,
            surface_proteins=surface_proteins,
            dna=dna,
            health=health,
            age=age,
            metabolism_rate=metabolism_rate,
            ph=ph,
            osmolarity=osmolarity,
            ion_concentrations=ion_concentrations,
            id=id,
            chromosomes=None, 
            structural_integrity=structural_integrity,
            mutation_count=mutation_count,
            growth_rate=growth_rate,
            repair_rate=repair_rate,
            max_divisions=max_divisions
        )
        self.organelles = organelles or {}
        self.core = CellCore(chromosome_pairs)

    def add_chromosome_pair(self, chromosome_pair: ChromosomePair):
        self.core.add_chromosome_pair(chromosome_pair)

    def remove_chromosome_pair(self, pair_name: str):
        self.core.remove_chromosome_pair(pair_name)

    def mutate(self) -> None:
        super().mutate()
        self.core.mutate()

    def divide(self) -> 'EukaryoticCell':
        new_core = self.core.replicate()

        new_cell = EukaryoticCell(
            name=f"{self.name}_offspring",
            cell_type=self.cell_type,
            receptors=self.receptors.copy(),
            surface_proteins=self.surface_proteins.copy(),
            organelles=self.organelles.copy()
        )
        new_cell.core = new_core
        self.health -= 10  # Division takes energy
        return new_cell

    def describe(self) -> str:
        description = super().describe()
        description += "\nCell Core (Nucleus) - Chromosome Pairs:\n"
        for pair in self.core.chromosome_pairs:
            description += f"  {pair}\n"
        return description

    def to_dict(self) -> dict:
        cell_dict = super().to_dict()
        cell_dict['core'] = self.core.to_dict()
        cell_dict['cell_type'] = self.cell_type
        cell_dict['name'] = self.name
        cell_dict['receptors'] = self.receptors
        cell_dict['surface_proteins'] = self.surface_proteins
        cell_dict['organelles'] = self.organelles
        cell_dict['age'] = self.age
        cell_dict['metabolism_rate'] = self.metabolism_rate
        cell_dict['ph'] = self.ph
        cell_dict['osmolarity'] = self.osmolarity
        cell_dict['ion_concentrations'] = self.ion_concentrations
        cell_dict['structural_integrity'] = self.structural_integrity
        cell_dict['id'] = self.id
        cell_dict['dna'] = self.dna

        return cell_dict

    @classmethod
    def from_dict(cls, cell_dict: dict) -> 'EukaryoticCell':
        core = CellCore.from_dict(cell_dict['core'])
        cell = cls(
            name=cell_dict['name'],
            cell_type=cell_dict['cell_type'],
            receptors=cell_dict['receptors'],
            surface_proteins=cell_dict['surface_proteins'],
            organelles=cell_dict['organelles'],
            health=cell_dict['health'],
            age=cell_dict['age'],
            metabolism_rate=cell_dict['metabolism_rate'],
            ph=cell_dict['ph'],
            osmolarity=cell_dict['osmolarity'],
            ion_concentrations=cell_dict['ion_concentrations'],
            structural_integrity=cell_dict['structural_integrity'],
            id=cell_dict['id'],
            dna=cell_dict['dna']
        )
        cell.core = core
        return cell

    def find_genes(self) -> List[Tuple[str, int, int, str]]:
        """Find potential genes in all chromosomes."""
        genes = []
        for pair in self.core.chromosome_pairs:
            for chromosome in pair.chromosomes:
                chromosome_genes = chromosome.find_genes()
                genes.extend([(pair.name, start, end, seq) for start, end, seq in chromosome_genes])
        return genes

    def to_json(self) -> str:
        """Return a JSON representation of the cell, including chemical characteristics."""
        cell_dict = self.to_dict()
        return json.dumps(cell_dict)

    def from_json(self, json_str: str) -> 'Cell':
        """Create a Cell object from a JSON string."""
        cell_dict = json.loads(json_str)
        return self.from_dict(cell_dict)

    def visualize_cell(self):
        super().visualize_cell()
        # Add visualization for cell core (nucleus)
        plt.gca().add_patch(plt.Circle((0.5, 0.5), 0.2, fill=False, color='blue', label='Nucleus'))
        chromosome_pair_text = f"Chromosome Pairs: {len(self.core.chromosome_pairs)}"
        plt.text(0.1, 0.65, chromosome_pair_text, fontsize=10, ha='left', va='bottom', color='purple')
        plt.legend()
