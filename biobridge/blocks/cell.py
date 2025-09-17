import random
from typing import List, Dict, Optional, Union
from biobridge.blocks.protein import Protein, json, plt
from biobridge.genes.dna import DNA
import math
import matplotlib.patches as patches
from biobridge.genes.chromosome import Chromosome


class Organelle:
    def __init__(self, name: str, efficiency: float = 1.0, health: int = 100):
        self.name = name
        self.efficiency = efficiency
        self.health = health

    def describe(self) -> str:
        return f"{self.name}: Efficiency: {self.efficiency:.2f}, Health: {self.health}"

    def __str__(self) -> str:
        return self.describe()


class Mitochondrion(Organelle):
    def __init__(self, efficiency: float = 1.0, health: int = 100):
        self.name = "mitochondrion"
        super().__init__(self.name, efficiency, health)
        self.atp_production = 0

    def produce_atp(self) -> int:
        self.atp_production = int(random.uniform(10, 20) * self.efficiency)
        self.health -= random.uniform(0, 1)  # Producing ATP causes some wear and tear
        self.health = max(0, min(100, self.health))
        return self.atp_production

    def repair(self, amount: float) -> None:
        self.health = min(100, int(self.health + amount))

    def describe(self) -> str:
        return f"{super().describe()}, ATP Production: {self.atp_production}"


class Cell:
    def __init__(self, name: str, cell_type: Optional[str] = None, receptors: Optional[List[Protein]] = None,
                 surface_proteins: Optional[List[Protein]] = None,
                 dna: Optional['DNA'] = None, health: Optional[int] = None, age: Optional[int] = 0, metabolism_rate: Optional[float] = 1.0,
                 ph: float = 7.0, osmolarity: float = 300.0, ion_concentrations: Optional[Dict[str, float]] = None, id: Optional[int] = None, chromosomes: Optional[List[Chromosome]] = None,
                 structural_integrity: float = 100.0, mutation_count: Optional[int] = 0, growth_rate: Optional[float] = 1.0, repair_rate: Optional[float] = 1.0,
                 max_divisions: Optional[int] = 50):
        """
        Initialize a new Cell object.

        :param name: Name of the cell
        :param cell_type: Type of the cell (e.g., "neuron", "muscle cell", "epithelial cell")
        :param receptors: List of Protein objects representing receptor binding sites on the cell
        :param surface_proteins: List of Protein objects expressed on the cell surface
        :param dna: DNA object representing the cell's DNA
        :param health: Health of the cell
        :param age: Age of the cell
        :param metabolism_rate: Metabolism rate of the cell
        :param ph: pH of the cell
        :param osmolarity: Osmolarity of the cell
        :param ion_concentrations: Dictionary of ion concentrations
        :param id: ID of the cell
        :param chromosomes: List of chromosomes
        :param structural_integrity: Structural integrity of the cell
        :param mutation_count: Number of mutations in the cell
        :param growth_rate: Growth rate of the cell
        :param repair_rate: Repair rate of the cell
        :param max_divisions: Maximum number of divisions allowed
        """
        self.name = name
        self.cell_type = cell_type
        self.receptors = receptors or []
        self.surface_proteins = surface_proteins or []
        self.internal_proteins = []
        self.organelles = {}
        self.dna = dna
        self.age = age
        self.health = 100 if health is None else health
        self.metabolism_rate = metabolism_rate
        self.ph = ph
        self.osmolarity = osmolarity
        self.ion_concentrations = ion_concentrations or {
            "Na+": 12.0,
            "K+": 140.0,
            "Cl-": 4.0,
            "Ca2+": 0.0001
        }
        self.id = id
        self.chromosomes = chromosomes or []
        self.molecules = []
        self.structural_integrity = structural_integrity
        self.mutation_count = mutation_count
        self.growth_rate = growth_rate
        self.repair_rate = repair_rate
        self.division_count = 0
        self.max_divisions = max_divisions

    def add_receptor(self, receptor: Protein) -> None:
        """Add a receptor to the cell."""
        if isinstance(receptor, Protein):
            self.receptors.append(receptor)
        else:
            raise TypeError("Receptor must be a Protein object")

    def add_surface_protein(self, protein: Protein) -> None:
        """Add a surface protein to the cell."""
        if isinstance(protein, Protein):
            self.surface_proteins.append(protein)
        else:
            raise TypeError("Surface protein must be a Protein object")

    def remove_surface_protein(self, protein: Protein) -> None:
        """Remove a surface protein from the cell."""
        self.surface_proteins = [p for p in self.surface_proteins if p != protein]

    def add_organelle(self, organelle: Organelle, quantity: int = 1) -> None:
        """
        Add an organelle to the cell, or increase the quantity if it already exists.

        :param organelle: The Organelle object to add
        :param quantity: Number of organelles to add (default is 1)
        """
        organelle_type = type(organelle).__name__
        if organelle_type not in self.organelles:
            self.organelles[organelle_type] = []
        self.organelles[organelle_type].extend([organelle] * quantity)

    def remove_organelle(self, organelle_type: str, quantity: int = 1) -> None:
        """
        Remove an organelle from the cell, or decrease the quantity if it exists.

        :param organelle_type: The type of organelle to remove (e.g., "Mitochondrion")
        :param quantity: Number of organelles to remove (default is 1)
        """
        if organelle_type in self.organelles:
            for _ in range(min(quantity, len(self.organelles[organelle_type]))):
                self.organelles[organelle_type].pop()
            if not self.organelles[organelle_type]:
                del self.organelles[organelle_type]

    def add_chromosome(self, chromosome: Chromosome):
        """Add a chromosome to the cell."""
        self.chromosomes.append(chromosome)

    def remove_chromosome(self, chromosome_name: str):
        """Remove a chromosome from the cell by its name."""
        self.chromosomes = [c for c in self.chromosomes if c.name != chromosome_name]

    def describe(self) -> str:
        """Provide a detailed description of the cell, including proteins."""
        description = [
            f"Cell Name: {self.name}",
            f"Cell Type: {self.cell_type or 'Not specified'}",
            f"Age: {self.age}",
            f"Health: {self.health}",
            f"Metabolism Rate: {self.metabolism_rate}",
            f"Chromosomes: {len(self.chromosomes)}",
            f"Receptors: {len(self.receptors)}",
            f"Surface Proteins: {len(self.surface_proteins)}",
            f"Internal Proteins: {len(self.internal_proteins)}",
            f"Division Count: {self.division_count}",
            f"Divisions Remaining: {self.max_divisions - self.division_count}",
        ]

        if self.receptors:
            description.append("Receptors:")
            for receptor in self.receptors:
                description.append(f"  {receptor.name}")

        if self.surface_proteins:
            description.append("Surface Proteins:")
            for protein in self.surface_proteins:
                description.append(f"  {protein.name}")

        if self.internal_proteins:
            description.append("Internal Proteins:")
            for protein in self.internal_proteins:
                description.append(f"  {protein.name}")

        if self.organelles:
            description.append("Organelles:")
            for organelle_list in self.organelles.values():
                if organelle_list:
                    organelle_name = organelle_list[0].name
                    quantity = len(organelle_list)
                    description.append(f"  {organelle_name}: {quantity}")
                else:
                    description.append("  Unknown organelle: 0")
        else:
            description.append("Organelles: None")

        chemical_description = [
            f"\nChemical Characteristics:",
            f"  pH: {self.ph:.2f}",
            f"  Osmolarity: {self.osmolarity:.2f} mOsm/L",
            "  Ion Concentrations (mmol/L):"
        ]
        for ion, concentration in self.ion_concentrations.items():
            chemical_description.append(f"    {ion}: {concentration:.4f}")

        description.append(f"Structural Integrity: {self.structural_integrity:.2f}")

        mutation_info = [
            f"Mutation Count: {self.mutation_count}",
            f"Growth Rate: {self.growth_rate:.2f}",
            f"Repair Rate: {self.repair_rate:.2f}"
        ]

        description.append("\n".join(mutation_info))
        return "\n".join(description + chemical_description)

    def interact_with_protein(self, protein: Protein) -> None:
        """
        Simulate the interaction between this cell and a protein, focusing on surface receptors and proteins.

        :param protein: The protein interacting with the cell
        """
        interaction_result = [f"{protein.name} interacts with {self.name}."]

        # Check for receptor binding
        bound_receptors = [receptor for receptor in self.receptors if any(binding['site'] == receptor.name for binding in protein.bindings)]
        if bound_receptors:
            interaction_result.append(f"Binding occurs at receptors: {', '.join([r.name for r in bound_receptors])}.")
        else:
            interaction_result.append("No specific receptor binding detected.")

        # Check for surface protein interaction
        interacting_surface_proteins = [sp for sp in self.surface_proteins if protein.sequence in sp.sequence]
        if interacting_surface_proteins:
            interaction_result.append(f"Interaction occurs with surface proteins: {', '.join([sp.name for sp in interacting_surface_proteins])}.")
        else:
            interaction_result.append("No specific surface protein interaction detected.")

        print(" ".join(interaction_result))

    def metabolize(self) -> int:
        """Simulate the cell's metabolism, affecting its health and age."""
        self.age += 1
        self.health -= random.uniform(0, 2) * self.metabolism_rate
        self.health = max(0, min(100, self.health))

        total_atp = 0

        for organelle_list in self.organelles.values():
            for organelle in organelle_list:
                if isinstance(organelle, Mitochondrion):
                    total_atp += organelle.produce_atp()  # Produce ATP and accumulate

        print(f"Total ATP produced: {total_atp}")
        return total_atp

    def calculate_structural_integrity(self) -> float:
        """
        Calculate the structural integrity of the cell based on various factors.
        Returns a value between 0 (completely compromised) and 100 (perfect integrity).
        """
        base_integrity = self.structural_integrity

        # Factor in cell age
        age_factor = max(0, int(1 - (self.age / 1000)))  # Assuming a cell can live up to 1000 time units

        # Factor in health
        health_factor = self.health / 100

        # Factor in osmolarity (assuming ideal osmolarity is 300 mOsm/L)
        osmolarity_factor = 1 - abs(self.osmolarity - 300) / 300

        # Factor in pH (assuming ideal pH is 7.0)
        ph_factor = 1 - abs(self.ph - 7.0) / 7.0

        # Calculate overall structural integrity
        overall_integrity = base_integrity * age_factor * health_factor * osmolarity_factor * ph_factor

        # Ensure the result is between 0 and 100
        return max(0, min(100, int(overall_integrity)))

    def update_structural_integrity(self) -> None:
        """
        Update the cell's structural integrity based on current conditions.
        """
        self.structural_integrity = self.calculate_structural_integrity()

    def mitosis(self) -> 'Cell':
        """
        Simulate mitotic cell division, creating an identical daughter cell.

        :return: A new Cell object (daughter cell)
        """
        # Replicate chromosomes
        new_chromosomes = [chromosome.replicate() for chromosome in self.chromosomes]

        # Create daughter cell with identical attributes
        daughter_cell = Cell(
            name=f"{self.name}_daughter",
            cell_type=self.cell_type,
            chromosomes=new_chromosomes,
            receptors=self.receptors.copy(),
            surface_proteins=self.surface_proteins.copy(),
            dna=self.dna.replicate() if self.dna else None,
            health=self.health,
            age=0,  # Reset age for the new cell
            metabolism_rate=self.metabolism_rate,
            ph=self.ph,
            osmolarity=self.osmolarity,
            ion_concentrations=self.ion_concentrations.copy(),
            structural_integrity=self.structural_integrity,
            mutation_count=self.mutation_count // 2,  # Distribute mutations among daughter cells
            growth_rate=self.growth_rate,
            repair_rate=self.repair_rate,
            max_divisions=self.max_divisions
        )
        daughter_cell.division_count = self.division_count
        daughter_cell.organelles = self.organelles

        # Simulate energy expenditure for the parent cell
        self.health -= 10
        self.structural_integrity *= 0.9

        return daughter_cell

    def meiosis(self) -> List['Cell']:
        """
        Simulate meiotic cell division, creating four haploid daughter cells.

        :return: A list of four new Cell objects (haploid daughter cells)
        """
        if len(self.chromosomes) % 2 != 0:
            raise ValueError("Meiosis requires an even number of chromosomes")

        haploid_chromosome_sets = []

        # Simulate crossing over and chromosome separation
        for _ in range(4):
            haploid_set = []
            for i in range(0, len(self.chromosomes), 2):
                # Randomly choose one chromosome from each pair
                chosen_chromosome = random.choice([self.chromosomes[i], self.chromosomes[i + 1]])
                haploid_set.append(chosen_chromosome.replicate())
            haploid_chromosome_sets.append(haploid_set)

        # Create four haploid daughter cells
        daughter_cells = []
        for i, haploid_set in enumerate(haploid_chromosome_sets):
            daughter_cell = Cell(
                name=f"{self.name}_haploid_daughter_{i + 1}",
                cell_type="haploid_" + self.cell_type if self.cell_type else "haploid",
                chromosomes=haploid_set,
                receptors=self.receptors.copy(),
                surface_proteins=self.surface_proteins.copy(),
                dna=None,  # Haploid cells don't have the full DNA
                health=self.health,
                age=0,  # Reset age for the new cells
                metabolism_rate=self.metabolism_rate,
                ph=self.ph,
                osmolarity=self.osmolarity,
                ion_concentrations=self.ion_concentrations.copy(),
                structural_integrity=self.structural_integrity * 0.9,  # Slightly reduce integrity
                mutation_count=self.mutation_count,
                growth_rate=self.growth_rate,
                repair_rate=self.repair_rate,
                max_divisions=self.max_divisions
            )
            daughter_cell.division_count = self.division_count
            daughter_cell.organelles = self.organelles
            daughter_cells.append(daughter_cell)

        # Simulate energy expenditure for the parent cell
        self.health -= 20
        self.structural_integrity *= 0.8

        return daughter_cells

    def can_divide(self) -> bool:
        """Check if the cell can still divide."""
        return self.division_count < self.max_divisions

    def divide(self) -> Union['Cell', List['Cell'], None]:
        """
        General method to divide the cell, choosing between mitosis and meiosis based on cell type.
        Now checks if the cell can divide before proceeding.

        :return: Either a single Cell object (for mitosis), a list of four Cell objects (for meiosis), or None if division is not possible
        """
        if not self.can_divide():
            print(f"{self.name} has reached its division limit and cannot divide further.")
            return None

        self.division_count += 1
        remaining_divisions = self.max_divisions - self.division_count
        print(f"{self.name} is dividing. Divisions remaining: {remaining_divisions}")

        if self.cell_type and "germ" in self.cell_type.lower():
            return self.meiosis()
        else:
            return self.mitosis()

    def repair(self, amount: float) -> None:
        """
        Repair the cell, increasing its health.

        :param amount: The amount of health to restore
        """
        self.structural_integrity = min(100, int(self.structural_integrity + amount / 2))
        self.health = min(100, math.floor(self.health + amount))

    def mutate(self) -> None:
        """Simulate a random mutation in the cell."""
        self.mutation_count += 1
        mutation_type = random.choice(["growth", "repair", "metabolism"])

        if mutation_type == "growth":
            self.growth_rate *= random.uniform(0.9, 1.1)  # 10% change in growth rate
        elif mutation_type == "repair":
            self.repair_rate *= random.uniform(0.9, 1.1)  # 10% change in repair rate
        elif mutation_type == "metabolism":
            self.metabolism_rate *= random.uniform(0.9, 1.1)  # 10% change in metabolism rate

        self.structural_integrity *= random.uniform(0.95, 1.05)
        self.structural_integrity = max(0, min(100, int(self.structural_integrity)))

        if self.chromosomes:
            chromosome = random.choice(self.chromosomes)
            chromosome.dna.random_mutate()

    def to_json(self) -> str:
        """Return a JSON representation of the cell, including chemical characteristics."""
        cell_dict = self.to_dict()
        return json.dumps(cell_dict)

    def reset(self):
        """Reset the cell."""
        self.health = 100
        self.age = 0
        self.metabolism_rate = 0.5
        self.dna = None
        self.receptors = []
        self.surface_proteins = []
        self.organelles = {}
        self.ph = 7.0
        self.osmolarity = 300.0
        self.ion_concentrations = {
            "Na+": 12.0,
            "K+": 140.0,
            "Cl-": 4.0,
            "Ca2+": 0.0001
        }
        self.chromosomes = []
        self.growth_rate = 0.5
        self.repair_rate = 0.5
        self.mutation_count = 0
        self.division_count = 0

    def adjust_ph(self, delta: float) -> None:
        """
        Adjust the pH of the cell.

        :param delta: Change in pH value
        """
        self.ph += delta
        self.ph = max(0, min(14, int(self.ph)))  # Ensure pH stays within valid range

    def adjust_osmolarity(self, delta: float) -> None:
        """
        Adjust the osmolarity of the cell.

        :param delta: Change in osmolarity (mOsm/L)
        """
        self.osmolarity += delta
        self.osmolarity = max(0, int(self.osmolarity))  # Ensure osmolarity doesn't go negative

    def adjust_ion_concentration(self, ion: str, delta: float) -> None:
        """
        Adjust the concentration of a specific ion in the cell.

        :param ion: The ion to adjust (e.g., "Na+", "K+", "Cl-", "Ca2+")
        :param delta: Change in ion concentration (mmol/L)
        """
        if ion in self.ion_concentrations:
            self.ion_concentrations[ion] += delta
            self.ion_concentrations[ion] = max(0,
                                               int(self.ion_concentrations[ion]))  # Ensure concentration doesn't go negative
        else:
            raise ValueError(f"Ion {ion} not found in cell's ion concentration list")

    def add_mitochondrion(self, efficiency: float = 1.0, health: int = 100, quantity: int = 1) -> None:
        """
        Add a mitochondrion to the cell.

        :param efficiency: Efficiency of the mitochondrion in producing ATP
        :param health: Health of the mitochondrion
        :param quantity: Quantity of the mitochondrion
        """
        mitochondrion = Mitochondrion(efficiency, health)
        self.add_organelle(mitochondrion, quantity)

    def remove_mitochondrion(self, quantity: int = 1) -> None:
        """
        Remove a mitochondrion from the cell.
        :param quantity: Quantity of mitochondria to remove
        """
        self.remove_organelle("Mitochondrion", quantity)

    @classmethod
    def from_json(self, json_str: str) -> 'Cell':
        """Create a Cell object from a JSON string."""
        cell_dict = json.loads(json_str)
        return self.from_dict(cell_dict)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the cell, including chromosomes."""
        return {
            'name': self.name,
            'cell_type': self.cell_type,
            'chromosomes': [{'name': c.name, 'dna': c.dna.to_dict()} for c in self.chromosomes],
            'receptors': self.receptors,
            'surface_proteins': self.surface_proteins,
            'health': self.health,
            'age': self.age,
            'metabolism_rate': self.metabolism_rate,
            'ph': self.ph,
            'osmolarity': self.osmolarity,
            'ion_concentrations': self.ion_concentrations,
            'structural_integrity': self.structural_integrity,
            'mutation_count': self.mutation_count,
            'id': self.id,
            'dna': self.dna.to_dict() if self.dna else None,
            'growth_rate': self.growth_rate,
            'repair_rate': self.repair_rate,
            'organelles': self.organelles,
            'division_count': self.division_count,
            'max_divisions': self.max_divisions
        }

    @classmethod
    def from_dict(cls, cell_dict: dict) -> 'Cell':
        """Create a Cell object from a dictionary, including chromosomes."""
        chromosomes = [Chromosome(DNA.from_dict(c['dna']), c['name']) for c in cell_dict['chromosomes']]
        cell = cls(
            name=cell_dict['name'],
            cell_type=cell_dict['cell_type'],
            chromosomes=chromosomes,
            receptors=cell_dict['receptors'],
            surface_proteins=cell_dict['surface_proteins'],
            health=cell_dict['health'],
            age=cell_dict['age'],
            metabolism_rate=cell_dict['metabolism_rate'],
            ph=cell_dict['ph'],
            osmolarity=cell_dict['osmolarity'],
            ion_concentrations=cell_dict['ion_concentrations'],
            structural_integrity=cell_dict['structural_integrity'],
            mutation_count=cell_dict['mutation_count'],
            id=cell_dict['id'],
            dna=cell_dict['dna'],
            growth_rate=cell_dict['growth_rate'],
            repair_rate=cell_dict['repair_rate'],
            max_divisions=cell_dict['max_divisions'],
        )
        cell.division_count = cell_dict.get('division_count', 0)
        cell.organelles = cell_dict.get('organelles', {})
        return cell

    def visualize_cell(self):
        """
        Create a 2D visual representation of the cell.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Draw cell membrane
        cell_membrane = patches.Circle((0.5, 0.5), 0.4, edgecolor='black', facecolor='none', linewidth=2)
        ax.add_patch(cell_membrane)

        # Draw nucleus
        nucleus = patches.Circle((0.5, 0.5), 0.2, edgecolor='blue', facecolor='lightblue', linewidth=2)
        ax.add_patch(nucleus)

        # Draw surface proteins
        num_proteins = len(self.surface_proteins)
        for i, protein in enumerate(self.surface_proteins):
            angle = 2 * i * math.pi / num_proteins
            x = 0.5 + 0.4 * math.cos(angle)
            y = 0.5 + 0.4 * math.sin(angle)
            ax.plot(x, y, 'ro')  # Red dot for surface proteins
            ax.text(x, y, protein.name, fontsize=8, ha='center', va='center')

        # Draw mitochondria
        num_mitochondria = len(self.organelles)
        for i, mitochondrion in enumerate(self.organelles):
            angle = 2 * i * math.pi / num_mitochondria
            x = 0.5 + 0.3 * math.cos(angle)
            y = 0.5 + 0.3 * math.sin(angle)
            mito = patches.Ellipse((x, y), 0.1, 0.05, angle=0, edgecolor='green', facecolor='lightgreen', linewidth=2)
            ax.add_patch(mito)
            ax.text(x, y, f'Mito {i + 1}', fontsize=8, ha='center', va='center')

        # Draw DNA sequence
        if self.dna:
            dna_text = f"DNA: {self.dna.sequence[:20]}..." if len(self.dna.sequence) > 20 else self.dna.sequence
            ax.text(0.5, 0.5, dna_text, fontsize=10, ha='center', va='center', color='purple')

        if self.chromosomes:
            chromosome_text = f"Chromosomes: {', '.join([c.name for c in self.chromosomes])}"
            ax.text(0.1, 0.05, chromosome_text, fontsize=12, ha='left', va='bottom', color='gray')

        # Display health and age
        health_text = f"Health: {self.health}"
        age_text = f"Age: {self.age}"
        type_text = f"Type: {self.cell_type}"
        osmolarity_text = f"Osmolarity: {self.osmolarity}"
        ph_text = f"pH: {self.ph}"
        ax.text(-0.2, 1, type_text, fontsize=12, ha='left', va='bottom', color='gray')
        ax.text(-0.2, 0.95, health_text, fontsize=12, ha='left', va='bottom', color='red')
        ax.text(-0.2, 0.9, age_text, fontsize=12, ha='left', va='bottom', color='gray')
        ax.text(-0.2, 0.85, osmolarity_text, fontsize=12, ha='left', va='bottom', color='blue')
        ax.text(-0.2, 0.8, ph_text, fontsize=12, ha='left', va='bottom', color='gray')
        integrity_text = f"Structural Integrity: {self.structural_integrity:.2f}"
        ax.text(-0.2, 0.75, integrity_text, fontsize=12, ha='left', va='bottom', color='purple')

        # Display ion concentrations
        ion_text = "\n".join([f"{ion}: {conc:.4f} mmol/L" for ion, conc in self.ion_concentrations.items()])
        ax.text(0.8, 0.9, ion_text, fontsize=10, ha='right', va='bottom', color='blue')

        mutation_text = f"Mutations: {self.mutation_count}"
        ax.text(-0.2, 0.7, mutation_text, fontsize=12, ha='left', va='bottom', color='orange')
        division_text = f"Divisions: {self.division_count}/{self.max_divisions}"
        ax.text(-0.2, 0.65, division_text, fontsize=12, ha='left', va='bottom', color='green')
        # Set plot limits and title
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(f"Cell: {self.name}")
        ax.axis('off')

        plt.show()

    def add_internal_protein(self, protein: Protein) -> None:
        """Add an internal protein to the cell."""
        if isinstance(protein, Protein):
            self.internal_proteins.append(protein)
        else:
            raise TypeError("Internal protein must be a Protein object")

    def remove_internal_protein(self, protein: Protein) -> None:
        """Remove an internal protein from the cell."""
        self.internal_proteins = [p for p in self.internal_proteins if p != protein]

    def receive_signal(self, signal: str, intensity: float = 1.0) -> str:
        """
        Receive and process an external signal.

        :param signal: The type of signal being received (e.g., "growth_factor", "neurotransmitter", "hormone")
        :param intensity: The intensity of the signal (default is 1.0)
        :return: A string describing the cell's response to the signal
        """
        response = f"Cell {self.name} received a {signal} signal with intensity {intensity}. "

        if signal in self.receptors:
            response += f"The cell has a receptor for this signal. "

            # Different responses based on signal type
            if signal == "growth_factor":
                self.health = min(100, int(self.health + 5 * intensity))
                response += f"Cell health increased to {self.health}. "
            elif signal == "apoptosis_signal":
                self.health = max(0, int(self.health - 10 * intensity))
                response += f"Cell health decreased to {self.health}. Apoptosis may be initiated. "
            elif signal == "differentiation_signal":
                if self.cell_type is None:
                    self.cell_type = "differentiated"
                    response += "Cell has differentiated. "
                else:
                    response += "Cell is already differentiated. "
            else:
                response += "General cellular activity increased. "
                self.metabolism_rate *= (1 + 0.1 * intensity)

            # Adjust ion concentrations based on signal
            for ion in self.ion_concentrations:
                self.ion_concentrations[ion] *= (1 + 0.05 * intensity)
            response += "Ion concentrations slightly adjusted. "

        else:
            response += f"The cell does not have a receptor for this signal. No direct effect. "

        # Update structural integrity after receiving the signal
        self.update_structural_integrity()
        response += f"Structural integrity is now {self.structural_integrity:.2f}. "

        return response

    def getATPProduction(self):
        total_atp_production = 0

        for organelle_list in self.organelles.values():
            for organelle in organelle_list:
                if isinstance(organelle, Mitochondrion):
                    organelle.produce_atp()
                    total_atp_production += organelle.atp_production

        return total_atp_production

    ORGANELLE_WEIGHTS = {
        "mitochondrion": 1e9,  # ~1 billion Da
        "nucleus": 1e11,  # ~100 billion Da
        "ribosome": 2.5e6,  # ~2.5 million Da
        "endoplasmic_reticulum": 2e10,  # ~20 billion Da
        "golgi_apparatus": 1e10,  # ~10 billion Da
        "lysosome": 3.5e9,  # ~3.5 billion Da
        "peroxisome": 1e9,  # ~1 billion Da
        "chloroplast": 5e10,  # ~50 billion Da (for plant cells)
        "vacuole": 1e9,  # ~1 billion Da (mainly for plant cells)
    }

    def calculate_organelle_weight(self) -> float:
        """
        Calculate the total weight of all organelles in the cell.

        :return: The total weight of organelles in Daltons
        """
        total_organelle_weight = 0.0

        # Iterate over organelles
        for organelle_list in self.organelles.values():
            # Iterate over each organelle object in the list
            for organelle in organelle_list:
                organelle_name = organelle.name

                if organelle_name in self.ORGANELLE_WEIGHTS:
                    total_organelle_weight += self.ORGANELLE_WEIGHTS[organelle_name]
                else:
                    raise KeyError(f"Organism type '{organelle_name}' not found in ORGANELLE_WEIGHTS")

        return total_organelle_weight

    def calculate_molecular_weight(self, custom_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate the total molecular weight of the cell, including proteins, DNA, organelles, and other components.

        :param custom_weights: Optional dictionary with custom weights for cell components
        :return: The total molecular weight of the cell in Daltons
        """
        total_weight = 0.0
        weights = custom_weights or {}

        for protein in self.surface_proteins:
            total_weight += protein.calculate_properties()['molecular_weight']

        for protein in self.internal_proteins:
            total_weight += protein.calculate_properties()['molecular_weight']

        for receptor in self.receptors:
            total_weight += receptor.calculate_properties()['molecular_weight']

        if self.dna:
            total_weight += self.dna.calculate_molecular_weight()

        for chromosome in self.chromosomes:
            total_weight += chromosome.satellite_dna.calculate_molecular_weight()

        total_weight += weights.get('organelles', self.calculate_organelle_weight())

        total_weight += weights.get('cell_membrane', 1e9)  # Default: 1 billion Daltons

        cell_volume = weights.get('cell_volume', 4 / 3 * math.pi * (10e-6) ** 3)
        total_weight += weights.get('water', cell_volume * 0.7 * 1000 / 18 * 6.022e23)

        total_weight += weights.get('small_molecules', cell_volume * 0.05 * 1000 * 6.022e23)

        return total_weight

    def get_molecular_weight_breakdown(self, custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Get a breakdown of the molecular weight of different components of the cell.

        :param custom_weights: Optional dictionary with custom weights for cell components
        :return: A dictionary with the weight of different cell components
        """
        weights = custom_weights or {}
        breakdown = {}

        breakdown['surface_proteins'] = sum(protein.calculate_properties()['molecular_weight'] for protein in self.surface_proteins)

        breakdown['internal_proteins'] = sum(protein.calculate_properties()['molecular_weight'] for protein in self.internal_proteins)

        breakdown['receptors'] = sum(receptor.calculate_properties()['molecular_weight'] for receptor in self.receptors)

        breakdown['dna'] = self.dna.calculate_molecular_weight() if self.dna else 0

        breakdown['chromosomes'] = sum(c.satellite_dna.calculate_molecular_weight() for c in self.chromosomes)

        breakdown['organelles'] = self.calculate_organelle_weight()

        breakdown['cell_membrane'] = weights.get('cell_membrane', 1e9)  # Default: 1 billion Daltons

        cell_volume = 4 / 3 * math.pi * (10e-6) ** 3
        breakdown['water'] = weights.get('water', cell_volume * 0.7 * 1000 / 18 * 6.022e23)

        breakdown['small_molecules'] = weights.get('small_molecules', cell_volume * 0.05 * 1000 * 6.022e23)

        return breakdown

    def maintain_homeostasis(self) -> Dict[str, str]:
        """
        Maintain cellular homeostasis by regulating internal conditions.
        """
        homeostasis_report = {}
        
        if self.ph < 6.8:
            self.ph = min(7.2, self.ph + 0.2)
            homeostasis_report['ph'] = "Increased pH to maintain balance"
        elif self.ph > 7.4:
            self.ph = max(6.8, self.ph - 0.2)
            homeostasis_report['ph'] = "Decreased pH to maintain balance"
        
        if self.osmolarity < 280:
            self.osmolarity = min(320, self.osmolarity + 20)
            homeostasis_report['osmolarity'] = "Increased osmolarity"
        elif self.osmolarity > 320:
            self.osmolarity = max(280, self.osmolarity - 20)
            homeostasis_report['osmolarity'] = "Decreased osmolarity"
        
        if self.ion_concentrations['Na+'] > 15:
            self.ion_concentrations['Na+'] = max(10, 
                                               self.ion_concentrations['Na+'] - 2)
            homeostasis_report['sodium'] = "Reduced sodium levels"
        elif self.ion_concentrations['Na+'] < 8:
            self.ion_concentrations['Na+'] = min(15, 
                                               self.ion_concentrations['Na+'] + 2)
            homeostasis_report['sodium'] = "Increased sodium levels"
        
        if self.ion_concentrations['K+'] < 130:
            self.ion_concentrations['K+'] = min(150, 
                                              self.ion_concentrations['K+'] + 10)
            homeostasis_report['potassium'] = "Increased potassium levels"
        elif self.ion_concentrations['K+'] > 150:
            self.ion_concentrations['K+'] = max(130, 
                                              self.ion_concentrations['K+'] - 10)
            homeostasis_report['potassium'] = "Decreased potassium levels"
        
        if self.health < 50:
            repair_amount = min(10, 100 - self.health)
            self.health += repair_amount
            homeostasis_report['health'] = f"Emergency repair: +{repair_amount} health"
        
        return homeostasis_report

    def autophagy(self) -> Dict[str, int]:
        """
        Simulate autophagy - cellular cleanup and recycling process.
        """
        recycled_components = {'damaged_proteins': 0, 'damaged_organelles': 0}
        
        damaged_proteins = [p for p in self.internal_proteins 
                           if hasattr(p, 'damaged') and p.damaged]
        if damaged_proteins:
            recycled_components['damaged_proteins'] = len(damaged_proteins)
            self.internal_proteins = [p for p in self.internal_proteins 
                                    if not (hasattr(p, 'damaged') and p.damaged)]
        
        for organelle_type, organelle_list in self.organelles.items():
            damaged_organelles = [o for o in organelle_list if o.health < 30]
            if damaged_organelles:
                recycled_components['damaged_organelles'] += len(damaged_organelles)
                self.organelles[organelle_type] = [o for o in organelle_list 
                                                 if o.health >= 30]
        
        atp_gain = sum(recycled_components.values()) * 5
        if atp_gain > 0:
            self.health = min(100, self.health + atp_gain // 2)
        
        return recycled_components

    def apoptosis_check(self) -> bool:
        """
        Check if cell should undergo programmed cell death (apoptosis).
        """
        apoptosis_signals = 0
        
        if self.health < 20:
            apoptosis_signals += 2
        if self.structural_integrity < 30:
            apoptosis_signals += 2
        if self.mutation_count > 10:
            apoptosis_signals += 1
        if self.division_count >= self.max_divisions:
            apoptosis_signals += 1
        if self.age > 800:
            apoptosis_signals += 1
        
        return apoptosis_signals >= 3

    def stress_response(self, stressor: str, intensity: float = 1.0) -> str:
        """
        Respond to cellular stress conditions.
        """
        response = f"Cell experiencing {stressor} stress (intensity: {intensity}). "
        
        if stressor == "oxidative":
            self.health -= int(5 * intensity)
            self.structural_integrity -= int(3 * intensity)
            response += "Producing antioxidant enzymes. "
        elif stressor == "heat":
            self.metabolism_rate *= (1 - 0.1 * intensity)
            response += "Producing heat shock proteins. "
        elif stressor == "osmotic":
            self.adjust_osmolarity(10 * intensity)
            response += "Adjusting osmolarity and ion transport. "
        elif stressor == "nutrient_deprivation":
            self.health -= int(3 * intensity)
            autophagy_result = self.autophagy()
            response += f"Activated autophagy: recycled {autophagy_result}. "
        elif stressor == "dna_damage":
            self.mutation_count += int(intensity)
            self.health -= int(2 * intensity)
            response += "Activating DNA repair mechanisms. "
        
        self.maintain_homeostasis()
        response += "Homeostasis mechanisms activated."
        
        return response

    def protein_synthesis(self, amino_acids: List[str] = None) -> Protein:
        """
        Simulate protein synthesis based on DNA/mRNA template.
        """
        if not amino_acids:
            amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 
                          'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']
        
        sequence_length = random.randint(50, 300)
        protein_sequence = ''.join(random.choices(amino_acids, k=sequence_length))
        
        new_protein = Protein(f"synthesized_protein_{len(self.internal_proteins)}", 
                             protein_sequence)
        self.add_internal_protein(new_protein)
        
        energy_cost = sequence_length * 4
        self.health = max(0, self.health - energy_cost // 10)
        
        return new_protein

    def cellular_respiration(self, glucose: float = 1.0, oxygen: float = 1.0) -> Dict[str, float]:
        """
        Simulate cellular respiration process.
        """
        if glucose <= 0 or oxygen <= 0:
            return {'atp': 0, 'co2': 0, 'h2o': 0, 'efficiency': 0}
        
        base_atp = 38
        efficiency = min(glucose, oxygen) * self.metabolism_rate
        
        atp_produced = base_atp * efficiency
        co2_produced = 6 * efficiency
        h2o_produced = 6 * efficiency
        
        mitochondria_count = len(self.organelles.get('Mitochondrion', []))
        if mitochondria_count > 0:
            atp_produced *= (1 + mitochondria_count * 0.1)
        
        self.health = min(100, self.health + int(atp_produced // 10))
        
        return {
            'atp': atp_produced,
            'co2': co2_produced,
            'h2o': h2o_produced,
            'efficiency': efficiency
        }

    def endocytosis(self, material: str, size: float = 1.0) -> str:
        """
        Simulate endocytosis - uptake of external materials.
        """
        energy_cost = int(size * 5)
        
        if self.health < energy_cost:
            return f"Insufficient energy for endocytosis of {material}"
        
        self.health -= energy_cost
        
        if material == "nutrients":
            self.health = min(100, self.health + int(size * 3))
            result = f"Successfully absorbed {material} via endocytosis"
        elif material == "pathogens":
            self.health -= int(size * 2)
            result = f"Engulfed {material} - immune response activated"
        else:
            result = f"Internalized {material} via endocytosis"
        
        return result

    def exocytosis(self, material: str, quantity: float = 1.0) -> str:
        """
        Simulate exocytosis - secretion of materials from the cell.
        """
        energy_cost = int(quantity * 3)
        
        if self.health < energy_cost:
            return f"Insufficient energy for exocytosis of {material}"
        
        self.health -= energy_cost
        
        if material == "waste":
            self.health = min(100, self.health + int(quantity * 2))
            result = f"Successfully expelled {quantity} units of {material}"
        elif material == "hormones":
            result = f"Secreted {quantity} units of {material} for signaling"
        elif material == "enzymes":
            result = f"Released {quantity} units of {material} for extracellular activity"
        else:
            result = f"Exported {quantity} units of {material}"
        
        return result

    def dna_repair(self) -> Dict[str, int]:
        """
        Simulate DNA repair mechanisms.
        """
        repairs = {'base_excision': 0, 'nucleotide_excision': 0, 'mismatch': 0}
        
        if self.dna and hasattr(self.dna, 'damage_count'):
            damage_count = self.dna.damage_count
            
            repairs['base_excision'] = min(damage_count, 
                                         int(random.uniform(1, 3) * self.repair_rate))
            damage_count -= repairs['base_excision']
            
            repairs['nucleotide_excision'] = min(damage_count, 
                                               int(random.uniform(0, 2) * self.repair_rate))
            damage_count -= repairs['nucleotide_excision']
            
            repairs['mismatch'] = min(damage_count, 
                                    int(random.uniform(0, 1) * self.repair_rate))
            
            total_repairs = sum(repairs.values())
            self.dna.damage_count = max(0, self.dna.damage_count - total_repairs)
            self.mutation_count = max(0, self.mutation_count - total_repairs // 2)
        
        for chromosome in self.chromosomes:
            if hasattr(chromosome.dna, 'damage_count') and chromosome.dna.damage_count > 0:
                repair_amount = int(random.uniform(0, 2) * self.repair_rate)
                chromosome.dna.damage_count = max(0, 
                                                chromosome.dna.damage_count - repair_amount)
        
        return repairs

    def cell_cycle_checkpoint(self, phase: str) -> bool:
        """
        Check if cell can proceed through cell cycle checkpoints.
        """
        if phase == "G1_S":
            return (self.health > 70 and 
                    self.structural_integrity > 60 and
                    len(self.chromosomes) > 0)
        elif phase == "G2_M":
            return (self.health > 60 and
                    self.structural_integrity > 50 and
                    self.mutation_count < 8)
        elif phase == "spindle":
            return (self.health > 50 and
                    all(hasattr(c, 'replicated') and c.replicated 
                        for c in self.chromosomes))
        
        return False

    def quorum_sensing(self, cell_density: float, signal_molecule: str = "AHL") -> str:
        """
        Simulate quorum sensing - density-dependent gene regulation.
        """
        threshold_density = 0.6
        
        if cell_density < threshold_density:
            return f"Cell density ({cell_density:.2f}) below threshold. Individual behavior maintained."
        
        response = f"Quorum reached! Density: {cell_density:.2f}. "
        
        if signal_molecule == "AHL":
            self.metabolism_rate *= 1.2
            response += "Increased metabolic activity. "
        elif signal_molecule == "AI2":
            if hasattr(self, 'virulence_factors'):
                self.virulence_factors = True
            response += "Activated virulence factors. "
        
        self.growth_rate *= 0.8
        response += "Coordinated group behavior initiated."
        
        return response

    def differentiate(self, target_type: str, growth_factors: List[str] = None) -> str:
        """
        Simulate cellular differentiation into specialized cell types.
        """
        if self.cell_type and "differentiated" in self.cell_type:
            return f"Cell already differentiated as {self.cell_type}"
        
        growth_factors = growth_factors or []
        
        differentiation_map = {
            "neuron": {"growth_factors": ["NGF", "BDNF"], "proteins": ["neurofilament", "synapsin"]},
            "muscle": {"growth_factors": ["IGF1", "FGF"], "proteins": ["actin", "myosin"]},
            "bone": {"growth_factors": ["BMP", "TGF-beta"], "proteins": ["collagen", "osteocalcin"]},
            "immune": {"growth_factors": ["IL2", "IL7"], "proteins": ["CD4", "CD8"]}
        }
        
        if target_type not in differentiation_map:
            return f"Unknown differentiation target: {target_type}"
        
        required_factors = differentiation_map[target_type]["growth_factors"]
        if not all(factor in growth_factors for factor in required_factors):
            return f"Missing required growth factors: {required_factors}"
        
        self.cell_type = f"differentiated_{target_type}"
        self.metabolism_rate *= 0.7
        self.growth_rate *= 0.5
        
        specialized_proteins = differentiation_map[target_type]["proteins"]
        for protein_name in specialized_proteins:
            specialized_protein = Protein(protein_name, "SPECIALIZED_SEQUENCE")
            self.add_surface_protein(specialized_protein)
        
        return f"Successfully differentiated into {target_type} cell"

    def calculate_fitness(self) -> float:
        """
        Calculate overall cellular fitness score.
        """
        health_score = self.health / 100
        integrity_score = self.structural_integrity / 100
        age_penalty = max(0, 1 - self.age / 1000)
        mutation_penalty = max(0, 1 - self.mutation_count / 20)
        division_potential = (self.max_divisions - self.division_count) / self.max_divisions
        
        organelle_bonus = min(1.0, len(self.organelles) * 0.1)
        protein_bonus = min(1.0, (len(self.surface_proteins) + len(self.internal_proteins)) * 0.01)
        
        fitness = (health_score * 0.3 + 
                   integrity_score * 0.25 + 
                   age_penalty * 0.15 + 
                   mutation_penalty * 0.15 + 
                   division_potential * 0.15 + 
                   organelle_bonus * 0.05 + 
                   protein_bonus * 0.05)
        
        return max(0, min(1, fitness))

    def environmental_adaptation(self, environment: Dict[str, float]) -> str:
        """
        Adapt to environmental conditions.
        """
        adaptation_response = []
        
        temperature = environment.get('temperature', 37.0)
        if temperature < 30:
            self.metabolism_rate *= 0.8
            adaptation_response.append("Slowed metabolism for cold adaptation")
        elif temperature > 42:
            self.metabolism_rate *= 0.9
            adaptation_response.append("Heat shock response activated")
        
        ph_env = environment.get('ph', 7.4)
        if abs(ph_env - self.ph) > 1.0:
            self.adjust_ph((ph_env - self.ph) * 0.3)
            adaptation_response.append("pH homeostasis adjustment")
        
        oxygen = environment.get('oxygen', 1.0)
        if oxygen < 0.5:
            self.metabolism_rate *= 0.7
            adaptation_response.append("Anaerobic metabolism activated")
        
        toxins = environment.get('toxins', 0.0)
        if toxins > 0.1:
            self.health -= int(toxins * 10)
            adaptation_response.append("Detoxification mechanisms activated")
        
        nutrients = environment.get('nutrients', 1.0)
        if nutrients < 0.5:
            adaptation_response.append("Starvation response - autophagy increased")
        
        return "; ".join(adaptation_response) if adaptation_response else "No adaptation needed"

    def __str__(self) -> str:
        """Return a string representation of the cell."""
        return self.describe()

    def __len__(self) -> int:
        """Return the length of the cell."""
        return len(self.receptors) + len(self.surface_proteins) + len(self.internal_proteins) + len(self.chromosomes) + len(self.organelles)

    def __getitem__(self):
        return Cell.from_dict(self.to_dict())

    def __iter__(self):
        """
        Iterate over collections in the cell (proteins, chromosomes, and organelles).
        """
        yield from iter(self.receptors)
        yield from iter(self.surface_proteins)
        yield from iter(self.internal_proteins)
        yield from iter(self.chromosomes)
        yield from iter(self.organelles.items())
