from typing import List, Optional
import json
import random
from biobridge.definitions.organ import Organ
from biobridge.networks.system import System
from biobridge.genes.dna import DNA


class Organism:
    def __init__(self, name: str, dna: 'DNA'):
        self.name = name
        self.dna = dna
        self.systems: List[System] = []
        self.organs: List[Organ] = []
        self.health = 100.0
        self.energy = 100.0
        self.adaptation_rate = 0.1
        self.mutation_rate = 0.01
        self.beneficial_mutation_chance = 0.1

    def add_system(self, system: System):
        self.systems.append(system)

    def add_organ(self, organ: Organ):
        self.organs.append(organ)

    def get_health(self) -> float:
        if not self.systems and not self.organs:
            return self.health
        system_health = sum(system.get_average_system_health() for system in self.systems) / len(self.systems) if self.systems else 0
        organ_health = sum(organ.get_health() for organ in self.organs) / len(self.organs) if self.organs else 0
        return (system_health + organ_health) / 2 if self.systems or self.organs else 0

    def update(self, external_factors: Optional[List[tuple]] = None):
        for system in self.systems:
            system.simulate_time_step(external_factors)

        for organ in self.organs:
            # Simple simulation for organs
            if external_factors:
                for factor, intensity in external_factors:
                    if factor == "toxin":
                        organ.damage(intensity * 5)
                    elif factor == "nutrient":
                        organ.heal(intensity * 3)

        self.regulate_mutations()
        self.adapt()

    def regulate_mutations(self):
        for system in self.systems:
            system.regulate_mutations()

        for organ in self.organs:
            if random.random() < self.mutation_rate:
                if random.random() < self.beneficial_mutation_chance:
                    benefit = random.uniform(0, 5)
                    organ.heal(benefit)
                    print(f"Beneficial mutation occurred in organ {organ.name}")
                else:
                    damage = random.uniform(0, 3)
                    organ.damage(damage)
                    print(f"Potentially harmful mutation occurred in organ {organ.name}")

    def adapt(self):
        current_health = self.get_health()
        if current_health < 50:
            self.adaptation_rate *= 1.1
        else:
            self.adaptation_rate *= 0.9
        self.adaptation_rate = max(0.05, min(0.2, self.adaptation_rate))

    def describe(self) -> str:
        description = [
            f"Organism Name: {self.name}",
            f"Overall Health: {self.get_health():.2f}",
            f"Energy: {self.energy:.2f}",
            f"Adaptation Rate: {self.adaptation_rate:.4f}",
            f"Mutation Rate: {self.mutation_rate:.4f}",
            "\nSystems:",
            *[system.get_system_status() for system in self.systems],
            "\nOrgans:",
            *[organ.describe() for organ in self.organs]
        ]
        return "\n".join(description)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "dna": self.dna.to_json(),
            "systems": [system.to_json() for system in self.systems],
            "organs": [organ.to_json() for organ in self.organs],
            "health": self.health,
            "energy": self.energy,
            "adaptation_rate": self.adaptation_rate,
            "mutation_rate": self.mutation_rate,
            "beneficial_mutation_chance": self.beneficial_mutation_chance
        })

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        dna_json = data["dna"]  

        organism = cls(name=data["name"], dna=DNA.from_json(json_str=dna_json))
        organism.systems = [System.from_json(system) for system in data["systems"]]
        organism.organs = [Organ.from_json(organ) for organ in data["organs"]]
        organism.health = data["health"]
        organism.energy = data["energy"]
        organism.adaptation_rate = data["adaptation_rate"]
        organism.mutation_rate = data["mutation_rate"]
        organism.beneficial_mutation_chance = data["beneficial_mutation_chance"]
        return organism

    def reproduce(self, partner: 'Organism') -> 'Organism':
        """
        Reproduce with another organism to create a new organism.

        :param partner: The partner organism to reproduce with
        :return: A new organism with combined DNA and random mutations
        """
        new_dna = self.combine_dna(self.dna, partner.dna)
        new_dna.random_mutate()
        new_organism = Organism(name=f"Offspring of {self.name} and {partner.name}", dna=new_dna)
        return new_organism

    @staticmethod
    def combine_dna(dna1: 'DNA', dna2: 'DNA') -> 'DNA':
        """
        Combine DNA from two organisms.

        :param dna1: DNA from the first organism
        :param dna2: DNA from the second organism
        :return: A new DNA object with combined sequences
        """
        sequence1 = dna1.get_sequence(1)
        sequence2 = dna2.get_sequence(1)
        combined_sequence = ''.join(
            random.choice([seq1, seq2]) for seq1, seq2 in zip(sequence1, sequence2)
        )
        new_dna = DNA(combined_sequence)
        return new_dna
