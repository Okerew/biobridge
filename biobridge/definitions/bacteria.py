from typing import List, Optional
from biobridge.blocks.cell import Cell, DNA, plt, patches
import numpy as np
import random


class Bacteria(Cell):
    def __init__(self, name: str, species: str, gram_stain: str, shape: str, motility: bool,
                 cell_wall_thickness: float, plasmids: Optional[List[DNA]] = None,
                 flagella: bool = False, pili: bool = False, capsule: bool = False,
                 antibiotic_resistance: Optional[List[str]] = None, **kwargs):
        super().__init__(name, cell_type="prokaryote", **kwargs)
        self.species = species
        self.gram_stain = gram_stain  # "positive" or "negative"
        self.shape = shape  # e.g., "rod", "spherical", "spiral"
        self.motility = motility
        self.cell_wall_thickness = cell_wall_thickness
        self.plasmids = plasmids or []
        self.flagella = flagella
        self.pili = pili
        self.capsule = capsule
        self.antibiotic_resistance = antibiotic_resistance or []
        self.binary_fission_count = 0

    def conjugate(self, recipient: 'Bacteria') -> bool:
        """Simulate bacterial conjugation (transfer of genetic material)."""
        if self.pili and len(self.plasmids) > 0:
            transferred_plasmid = random.choice(self.plasmids)
            recipient.plasmids.append(transferred_plasmid)
            return True
        return False

    def binary_fission(self) -> 'Bacteria':
        """Simulate binary fission (bacterial reproduction)."""
        self.binary_fission_count += 1
        daughter_cell = Bacteria(
            name=f"{self.name}_daughter_{self.binary_fission_count}",
            species=self.species,
            gram_stain=self.gram_stain,
            shape=self.shape,
            motility=self.motility,
            cell_wall_thickness=self.cell_wall_thickness,
            plasmids=[plasmid.replicate() for plasmid in self.plasmids],
            flagella=self.flagella,
            pili=self.pili,
            capsule=self.capsule,
            antibiotic_resistance=self.antibiotic_resistance.copy(),
            chromosomes=[chromosome.replicate() for chromosome in self.chromosomes],
            dna=self.dna.replicate() if self.dna else None,
            health=self.health,
            metabolism_rate=self.metabolism_rate,
            ph=self.ph,
            osmolarity=self.osmolarity,
            ion_concentrations=self.ion_concentrations.copy(),
            structural_integrity=self.structural_integrity,
            mutation_count=self.mutation_count,
            growth_rate=self.growth_rate,
            repair_rate=self.repair_rate
        )
        return daughter_cell

    def form_biofilm(self, surface: str) -> str:
        """Simulate biofilm formation on a given surface."""
        if self.pili:
            return f"{self.name} has formed a biofilm on the {surface}."
        return f"{self.name} cannot form a biofilm due to lack of pili."

    def respond_to_antibiotic(self, antibiotic: str) -> str:
        """Simulate the bacteria's response to an antibiotic."""
        if antibiotic in self.antibiotic_resistance:
            self.health -= 10  # Minor impact due to resistance
            return f"{self.name} is resistant to {antibiotic}. Minor health impact."
        else:
            self.health -= 50  # Major impact due to lack of resistance
            return f"{self.name} is not resistant to {antibiotic}. Major health impact."

    def describe(self) -> str:
        """Provide a detailed description of the bacteria."""
        description = super().describe()
        bacterial_info = f"""
        Species: {self.species}
        Gram Stain: {self.gram_stain}
        Shape: {self.shape}
        Motility: {"Yes" if self.motility else "No"}
        Cell Wall Thickness: {self.cell_wall_thickness} nm
        Plasmids: {len(self.plasmids)}
        Flagella: {"Present" if self.flagella else "Absent"}
        Pili: {"Present" if self.pili else "Absent"}
        Capsule: {"Present" if self.capsule else "Absent"}
        Antibiotic Resistance: {", ".join(self.antibiotic_resistance) if self.antibiotic_resistance else "None"}
        Binary Fission Count: {self.binary_fission_count}
        """
        return description + bacterial_info

    def to_dict(self) -> dict:
        """Return a dictionary representation of the bacteria."""
        bacteria_dict = super().to_dict()
        bacteria_dict.update({
            'species': self.species,
            'gram_stain': self.gram_stain,
            'shape': self.shape,
            'motility': self.motility,
            'cell_wall_thickness': self.cell_wall_thickness,
            'plasmids': [plasmid.to_dict() for plasmid in self.plasmids],
            'flagella': self.flagella,
            'pili': self.pili,
            'capsule': self.capsule,
            'antibiotic_resistance': self.antibiotic_resistance,
            'binary_fission_count': self.binary_fission_count
        })
        return bacteria_dict

    @classmethod
    def from_dict(cls, bacteria_dict: dict) -> 'Bacteria':
        """Create a Bacteria object from a dictionary."""
        cell_dict = {k: v for k, v in bacteria_dict.items() if k in Cell.__init__.__code__.co_varnames and k != 'name' and k != 'cell_type'}
        bacteria = cls(
            name=bacteria_dict['name'],
            species=bacteria_dict['species'],
            gram_stain=bacteria_dict['gram_stain'],
            shape=bacteria_dict['shape'],
            motility=bacteria_dict['motility'],
            cell_wall_thickness=bacteria_dict['cell_wall_thickness'],
            plasmids=[DNA.from_dict(plasmid_dict) for plasmid_dict in bacteria_dict['plasmids']],
            flagella=bacteria_dict['flagella'],
            pili=bacteria_dict['pili'],
            capsule=bacteria_dict['capsule'],
            antibiotic_resistance=bacteria_dict['antibiotic_resistance'],
            **cell_dict
        )
        bacteria.binary_fission_count = bacteria_dict['binary_fission_count']
        return bacteria

    def mutate(self) -> None:
        """Simulate a random mutation in the bacteria."""
        super().mutate()
        if random.random() < 0.1:  # 10% chance of gaining antibiotic resistance
            new_resistance = random.choice(["penicillin", "ampicillin", "tetracycline", "streptomycin"])
            if new_resistance not in self.antibiotic_resistance:
                self.antibiotic_resistance.append(new_resistance)
                print(f"{self.name} has gained resistance to {new_resistance}.")

    def visualize_bacteria(self):
        """Create a 2D visual representation of the bacteria."""
        fig, ax = plt.subplots(figsize=(10, 8))

        # Draw cell membrane
        if self.shape == "rod":
            cell_body = patches.Ellipse((0.5, 0.5), 0.8, 0.4, edgecolor='black', facecolor='lightgray', linewidth=2)
        elif self.shape == "spherical":
            cell_body = patches.Circle((0.5, 0.5), 0.4, edgecolor='black', facecolor='lightgray', linewidth=2)
        elif self.shape == "spiral":
            theta = np.linspace(0, 4*np.pi, 100)
            r = 0.2 + 0.05 * theta
            x = 0.5 + r * np.cos(theta)
            y = 0.5 + r * np.sin(theta)
            cell_body = plt.plot(x, y, 'black', linewidth=2)[0]
        else:
            cell_body = patches.Circle((0.5, 0.5), 0.4, edgecolor='black', facecolor='lightgray', linewidth=2)

        ax.add_patch(cell_body) if isinstance(cell_body, patches.Patch) else None

        # Draw flagella if present
        if self.flagella:
            flagella = patches.Arc((0.5, 0.1), 0.4, 0.4, edgecolor='blue', linewidth=2)
            ax.add_patch(flagella)

        # Draw pili if present
        if self.pili:
            for i in range(5):
                angle = np.random.uniform(0, 2*np.pi)
                length = np.random.uniform(0.05, 0.1)
                dx, dy = length * np.cos(angle), length * np.sin(angle)
                ax.arrow(0.5, 0.5, dx, dy, head_width=0.02, head_length=0.02, fc='green', ec='green')

        # Draw plasmids
        for i, plasmid in enumerate(self.plasmids):
            plasmid_circle = patches.Circle((0.3 + i*0.2, 0.7), 0.05, edgecolor='purple', facecolor='none', linewidth=2)
            ax.add_patch(plasmid_circle)

        # Display bacterial information
        info_text = f"""
        Species: {self.species}
        Gram Stain: {self.gram_stain}
        Shape: {self.shape}
        Motility: {"Yes" if self.motility else "No"}
        Antibiotic Resistance: {", ".join(self.antibiotic_resistance) if self.antibiotic_resistance else "None"}
        """
        ax.text(0.05, 0.05, info_text, fontsize=10, va='bottom', ha='left')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(f"Bacteria: {self.name}")
        ax.axis('off')

        plt.show()
