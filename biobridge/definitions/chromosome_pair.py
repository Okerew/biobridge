from biobridge.genes.chromosome import Chromosome
import random


class ChromosomePair:
    def __init__(self, chromosome1: Chromosome, chromosome2: Chromosome):
        if chromosome1.name != chromosome2.name:
            raise ValueError("Chromosomes in a pair must have the same name")
        self.name = chromosome1.name
        self.chromosomes = [chromosome1, chromosome2]

    def __str__(self):
        return f"Chromosome Pair {self.name}: 2 chromosomes, each with {len(self.chromosomes[0])} base pairs"

    def mutate(self):
        for chromosome in self.chromosomes:
            if random.random() < 0.01:  # 1% chance of mutation for each chromosome
                chromosome.mutate()

    def replicate(self) -> 'ChromosomePair':
        return ChromosomePair(self.chromosomes[0].replicate(), self.chromosomes[1].replicate())

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'chromosomes': [chr.to_dict() for chr in self.chromosomes]
        }

    @classmethod
    def from_dict(cls, pair_dict: dict) -> 'ChromosomePair':
        chromosomes = [Chromosome.from_dict(c) for c in pair_dict['chromosomes']]
        return cls(chromosomes[0], chromosomes[1])
