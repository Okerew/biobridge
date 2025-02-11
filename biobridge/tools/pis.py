import random
from typing import Union
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell, List
from biobridge.definitions.virus import Virus


class ProteinInteractionSimulator:
    def __init__(self, protein: Protein):
        self.protein = protein

    def calculate_binding_affinity(self, target: Union[Cell, Virus]) -> float:
        """
        Calculate the binding affinity of the protein to the target (cell or virus).
        Returns a value between 0 (no binding) and 1 (perfect binding).
        """
        binding_score = 0

        # Check for matching receptors or surface proteins
        if isinstance(target, Cell):
            matching_receptors = set(self.protein.bindings).intersection(target.receptors)
            matching_surface_proteins = set(self.protein.sequence).intersection(target.surface_proteins)
            binding_score += len(matching_receptors) * 0.2 + len(matching_surface_proteins) * 0.1
        elif isinstance(target, Virus):
            matching_proteins = set(self.protein.sequence).intersection([p.sequence for p in target.proteins])
            binding_score += len(matching_proteins) * 0.3

        # Consider protein activeness
        binding_score += self.protein.activeness() * 0.2

        # Normalize the binding score
        return min(binding_score, 1)

    def calculate_destructive_potential(self, target: Union[Cell, Virus]) -> float:
        """
        Calculate the destructive potential of the protein against the target.
        Returns a value between 0 (no destruction) and 1 (complete destruction).
        """
        destruction_score = 0

        # Consider protein activeness
        destruction_score += self.protein.activeness() * 0.3

        # Check for inhibitory interactions
        inhibitory_interactions = [i for i in self.protein.interactions if i['type'].lower() == 'inhibition']
        destruction_score += len(inhibitory_interactions) * 0.2

        # Consider target health (for cells) or virulence (for viruses)
        if isinstance(target, Cell):
            destruction_score += (100 - target.health) * 0.005  # Lower health increases susceptibility
        elif isinstance(target, Virus):
            destruction_score += target.virulence * 0.3

        # Normalize the destruction score
        return min(destruction_score, 1)

    def calculate_side_effects(self) -> List[str]:
        """
        Calculate potential side effects based on the protein's properties.
        Returns a list of potential side effects.
        """
        side_effects = []

        if self.protein.activeness() > 0.8:
            side_effects.append("Possible overactivation of cellular processes")

        if len(self.protein.interactions) > 5:
            side_effects.append("Potential for unintended interactions")

        if len(self.protein.bindings) > 3:
            side_effects.append("Risk of binding to unintended targets")

        return side_effects

    def calculate_success_chance(self, target: Union[Cell, Virus]) -> float:
        """
        Calculate the overall chance of successful interaction with the target.
        Returns a value between 0 (no chance of success) and 1 (guaranteed success).
        """
        binding_affinity = self.calculate_binding_affinity(target)
        destructive_potential = self.calculate_destructive_potential(target)

        # Consider the number of side effects as a negative factor
        side_effect_penalty = len(self.calculate_side_effects()) * 0.1

        success_chance = (binding_affinity * 0.4 + destructive_potential * 0.6) - side_effect_penalty

        return max(0, int(min(success_chance, 1.0)))  # Ensure the result is between 0 and 1

    def simulate_interaction(self, target: Union[Cell, Virus]) -> dict:
        """
        Simulate the interaction between the protein and the target.
        Returns a dictionary with the simulation results.
        """
        binding_affinity = self.calculate_binding_affinity(target)
        destructive_potential = self.calculate_destructive_potential(target)
        side_effects = self.calculate_side_effects()
        success_chance = self.calculate_success_chance(target)

        return {
            "binding_affinity": binding_affinity,
            "destructive_potential": destructive_potential,
            "side_effects": side_effects,
            "success_chance": success_chance,
            "outcome": "Success" if random.random() < success_chance else "Failure"
        }

    def __str__(self) -> str:
        return f"ProteinInteractionSimulator for {self.protein.name}"
    