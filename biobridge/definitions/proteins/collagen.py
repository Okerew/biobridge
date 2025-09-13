from biobridge.blocks.protein import Protein
import random


class Collagen(Protein):
    def __init__(self, name, sequence, structure=None, secondary_structure=None):
        super().__init__(name, sequence, structure, secondary_structure)
        self.tensile_strength = random.uniform(0.7, 1.0)
        self.triple_helix_stability = random.uniform(0.8, 1.0)

    def form_fibrils(self):
        fibril_strength = self.tensile_strength * self.triple_helix_stability
        return fibril_strength

    def resist_tension(self, applied_force):
        resistance = min(applied_force, self.tensile_strength)
        return resistance
