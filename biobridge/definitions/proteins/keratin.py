from biobridge.blocks.protein import Protein
import random


class Keratin(Protein):
    def __init__(self, name, sequence, structure=None, secondary_structure=None):
        super().__init__(name, sequence, structure, secondary_structure)
        self.mechanical_strength = random.uniform(0.6, 1.0)
        self.water_resistance = random.uniform(0.7, 0.9)

    def form_filaments(self):
        filament_strength = self.mechanical_strength * self.water_resistance
        return filament_strength

    def protect_tissue(self, external_stress):
        protection_level = min(external_stress, self.mechanical_strength)
        return protection_level
