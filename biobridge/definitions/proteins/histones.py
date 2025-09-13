from biobridge.blocks.protein import Protein
import random


class Histones(Protein):
    def __init__(self, name, sequence, structure=None, secondary_structure=None):
        super().__init__(name, sequence, structure, secondary_structure)
        self.dna_binding_affinity = random.uniform(0.8, 1.0)
        self.compaction_efficiency = random.uniform(0.7, 0.9)

    def bind_dna(self):
        binding_strength = self.dna_binding_affinity * random.uniform(0.9, 1.0)
        return binding_strength

    def compact_chromatin(self):
        compaction_level = self.compaction_efficiency * self.dna_binding_affinity
        return compaction_level