from typing import Optional
from biobridge.blocks.tissue import Tissue, List
import json


class Organ:
    def __init__(self, name: str, tissues: List[Tissue], health: Optional[float] = 100.0):
        self.name = name
        self.tissues = tissues
        self.health = health

    def get_health(self) -> float:
        return self.health

    def mutate(self):
        for tissue in self.tissues:
            tissue.mutate()

    def damage(self, amount: float):
        self.health = max(0, int(self.health - amount))

    def heal(self, amount: float):
        self.health = min(100, int(self.health + amount))

    def describe(self) -> str:
        description = [
            f"Organ Name: {self.name}",
            f"Health: {self.health}",
            f"Tissues: {', '.join([tissue.name for tissue in self.tissues])}"
        ]
        return "\n".join(description)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "tissues": [tissue.to_json() for tissue in self.tissues],
            "health": self.health
        })

    @classmethod
    def from_json(cls, json_str: str):
        json_data = json.loads(json_str)
        return cls(
            name=json_data["name"],
            tissues=[Tissue.from_json(tissue) for tissue in json_data["tissues"]],
            health=json_data["health"]
        )
