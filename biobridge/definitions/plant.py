from typing import List, Optional
import json
from biobridge.definitions.organ import Organ
from biobridge.genes.dna import DNA
from biobridge.definitions.organism import Organism


class Plant(Organism):
    def __init__(self, name: str, dna: 'DNA'):
        super().__init__(name, dna)
        self.sunlight_exposure = 0.0
        self.water_level = 50.0
        self.nutrients = 50.0
        self.growth_rate = 0.05

    def add_leaf(self, leaf: Organ):
        self.organs.append(leaf)

    def add_root(self, root: Organ):
        self.organs.append(root)

    def update(self, external_factors: Optional[List[tuple]] = None):
        super().update(external_factors)

        if external_factors:
            for factor, intensity in external_factors:
                if factor == "sunlight":
                    self.sunlight_exposure += intensity
                elif factor == "water":
                    self.water_level += intensity
                elif factor == "nutrients":
                    self.nutrients += intensity

        self.photosynthesize()
        self.grow()

    def photosynthesize(self):
        energy_produced = self.sunlight_exposure * 0.1 * len([organ for organ in self.organs if organ.name == "Leaf"])
        self.energy = min(100, self.energy + energy_produced)
        self.sunlight_exposure = 0

    def grow(self):
        if self.water_level > 20 and self.nutrients > 20 and self.energy > 30:
            growth = self.growth_rate * (self.water_level + self.nutrients) / 200
            self.water_level -= growth * 10
            self.nutrients -= growth * 10
            self.energy -= growth * 15
            print(f"{self.name} has grown by {growth:.2f} units")

    def describe(self) -> str:
        description = super().describe()
        additional_info = [
            f"\nSunlight Exposure: {self.sunlight_exposure:.2f}",
            f"Water Level: {self.water_level:.2f}",
            f"Nutrients: {self.nutrients:.2f}",
            f"Growth Rate: {self.growth_rate:.4f}"
        ]
        return description + "\n".join(additional_info)

    def to_json(self) -> str:
        data = json.loads(super().to_json())
        data.update({
            "sunlight_exposure": self.sunlight_exposure,
            "water_level": self.water_level,
            "nutrients": self.nutrients,
            "growth_rate": self.growth_rate
        })
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        plant = super().from_json(json_str)
        plant.sunlight_exposure = data["sunlight_exposure"]
        plant.water_level = data["water_level"]
        plant.nutrients = data["nutrients"]
        plant.growth_rate = data["growth_rate"]
        return plant
    