from typing import List, Optional, Dict
import json
from biobridge.definitions.organ import Organ
from biobridge.genes.dna import DNA
from biobridge.definitions.organism import Organism
from biobridge.definitions.cells.plant import PlantCell


class Plant(Organism):
    def __init__(self, name: str, dna: DNA, species: str = "Unknown"):
        super().__init__(name, dna)
        self.species = species
        self.sunlight_exposure = 0.0
        self.water_level = 50.0
        self.nutrients = 50.0
        self.growth_rate = 0.05
        self.height = 10.0
        self.leaf_area = 0.0
        self.root_depth = 0.0
        self.flowering_stage = "vegetative"
        self.seasonal_adaptation = 1.0
        
        self.plant_cells = []
        self.tissues = {"leaf": [], "stem": [], "root": []}

    def add_plant_cell(self, tissue_type: str = "leaf") -> None:
        cell_name = f"{self.name}_{tissue_type}_cell_{len(self.plant_cells)}"
        new_cell = PlantCell(cell_name, dna=self.dna)
        self.plant_cells.append(new_cell)
        
        if tissue_type in self.tissues:
            self.tissues[tissue_type].append(new_cell)

    def add_leaf(self, leaf: Organ) -> None:
        self.organs.append(leaf)
        self.leaf_area += getattr(leaf, 'surface_area', 10.0)
        
        for _ in range(5):
            self.add_plant_cell("leaf")

    def add_root(self, root: Organ) -> None:
        self.organs.append(root)
        self.root_depth += getattr(root, 'length', 5.0)
        
        for _ in range(3):
            self.add_plant_cell("root")

    def add_stem(self, stem: Organ) -> None:
        self.organs.append(stem)
        self.height += getattr(stem, 'length', 2.0)
        
        for _ in range(2):
            self.add_plant_cell("stem")

    def update(self, external_factors: Optional[List[tuple]] = None) -> None:
        super().update(external_factors)
        
        if external_factors:
            for factor, intensity in external_factors:
                if factor == "sunlight":
                    self.sunlight_exposure += intensity
                elif factor == "water":
                    self.water_level = max(0, min(100, self.water_level + intensity))
                elif factor == "nutrients":
                    self.nutrients = max(0, min(100, self.nutrients + intensity))
                elif factor == "temperature":
                    self.adapt_to_temperature(intensity)
                elif factor == "co2":
                    self.respond_to_co2(intensity)
        
        self.photosynthesize()
        self.grow()
        self.maintain_water_balance()
        self.update_plant_cells()

    def photosynthesize(self) -> float:
        if self.sunlight_exposure <= 0:
            return 0.0
        
        total_glucose = 0
        leaf_cells = self.tissues.get("leaf", [])
        
        for cell in leaf_cells:
            if hasattr(cell, 'photosynthesize'):
                light_per_cell = self.sunlight_exposure / max(1, len(leaf_cells))
                glucose = cell.photosynthesize(light_per_cell, 0.04)
                total_glucose += glucose
        
        energy_produced = total_glucose * 10
        self.energy = min(100, self.energy + energy_produced)
        self.sunlight_exposure = 0
        
        return total_glucose

    def grow(self) -> None:
        if (self.water_level > 20 and self.nutrients > 20 and 
            self.energy > 30):
            
            growth_factor = (self.water_level + self.nutrients) / 200
            growth = self.growth_rate * growth_factor * self.seasonal_adaptation
            
            self.height += growth * 2
            self.leaf_area += growth * 1.5
            self.root_depth += growth
            
            self.water_level -= growth * 10
            self.nutrients -= growth * 10
            self.energy -= growth * 15
            
            if growth > 0.01:
                print(f"{self.name} has grown by {growth:.3f} units")
                
                if len(self.plant_cells) < 50:
                    self.add_plant_cell("leaf" if self.leaf_area > self.root_depth 
                                      else "root")

    def maintain_water_balance(self) -> None:
        water_loss = self.leaf_area * 0.1
        water_uptake = min(self.root_depth * 0.2, self.water_level)
        
        net_water_change = water_uptake - water_loss
        self.water_level = max(0, min(100, self.water_level + net_water_change))
        
        for cell in self.plant_cells:
            if hasattr(cell, 'water_uptake'):
                cell.water_uptake(net_water_change / len(self.plant_cells))

    def adapt_to_temperature(self, temperature: float) -> None:
        optimal_temp = 25.0
        temp_deviation = abs(temperature - optimal_temp)
        
        if temp_deviation > 15:
            self.seasonal_adaptation = 0.5
            self.health -= temp_deviation * 0.5
        elif temp_deviation > 10:
            self.seasonal_adaptation = 0.8
        else:
            self.seasonal_adaptation = 1.0

    def respond_to_co2(self, co2_level: float) -> None:
        if co2_level > 0.1:
            self.growth_rate *= 1.1
        elif co2_level < 0.02:
            self.growth_rate *= 0.9

    def update_plant_cells(self) -> None:
        for cell in self.plant_cells:
            if self.health < 30:
                cell.health = max(0, cell.health - 5)
            elif self.health > 70:
                cell.health = min(100, cell.health + 2)

    def enter_flowering_stage(self) -> None:
        if self.height > 50 and self.energy > 60:
            self.flowering_stage = "flowering"
            self.growth_rate *= 0.7
            print(f"{self.name} has entered the flowering stage!")

    def produce_seeds(self) -> int:
        if self.flowering_stage == "flowering" and self.energy > 80:
            seed_count = int(self.leaf_area / 10)
            self.energy -= seed_count * 2
            print(f"{self.name} has produced {seed_count} seeds!")
            return seed_count
        return 0

    def seasonal_dormancy(self) -> None:
        self.flowering_stage = "dormant"
        self.growth_rate *= 0.1
        self.seasonal_adaptation = 0.3
        
        for cell in self.plant_cells:
            cell.health = max(20, cell.health * 0.8)

    def cellular_stress_response(self, stress_type: str, intensity: float) -> None:
        for cell in self.plant_cells:
            if stress_type == "drought":
                if hasattr(cell, 'central_vacuole'):
                    cell.central_vacuole.adjust_turgor_pressure(-intensity * 0.1)
            elif stress_type == "heat":
                if hasattr(cell, 'respond_to_light_stress'):
                    cell.respond_to_light_stress(intensity)
            elif stress_type == "pathogen":
                cell.health -= intensity * 5

    def describe(self) -> str:
        description = super().describe()
        plant_specific = f"""

Plant-Specific Information:
    Species: {self.species}
    Height: {self.height:.2f} cm
    Leaf Area: {self.leaf_area:.2f} cm²
    Root Depth: {self.root_depth:.2f} cm
    Sunlight Exposure: {self.sunlight_exposure:.2f} lux
    Water Level: {self.water_level:.2f}%
    Nutrients: {self.nutrients:.2f}%
    Growth Rate: {self.growth_rate:.4f}
    Flowering Stage: {self.flowering_stage}
    Seasonal Adaptation: {self.seasonal_adaptation:.2f}
    Plant Cells: {len(self.plant_cells)}

Tissue Distribution:
    Leaf cells: {len(self.tissues.get('leaf', []))}
    Stem cells: {len(self.tissues.get('stem', []))}
    Root cells: {len(self.tissues.get('root', []))}
        """
        return description + plant_specific

    def to_json(self) -> str:
        data = json.loads(super().to_json())
        data.update({
            "species": self.species,
            "sunlight_exposure": self.sunlight_exposure,
            "water_level": self.water_level,
            "nutrients": self.nutrients,
            "growth_rate": self.growth_rate,
            "height": self.height,
            "leaf_area": self.leaf_area,
            "root_depth": self.root_depth,
            "flowering_stage": self.flowering_stage,
            "seasonal_adaptation": self.seasonal_adaptation,
            "plant_cells_count": len(self.plant_cells),
            "tissue_distribution": {
                tissue: len(cells) for tissue, cells in self.tissues.items()
            }
        })
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Plant':
        data = json.loads(json_str)
        
        plant = cls(data["name"], DNA.from_dict(data["dna"]), data["species"])
        
        plant.sunlight_exposure = data["sunlight_exposure"]
        plant.water_level = data["water_level"]
        plant.nutrients = data["nutrients"]
        plant.growth_rate = data["growth_rate"]
        plant.height = data["height"]
        plant.leaf_area = data["leaf_area"]
        plant.root_depth = data["root_depth"]
        plant.flowering_stage = data["flowering_stage"]
        plant.seasonal_adaptation = data["seasonal_adaptation"]
        plant.energy = data["energy"]
        plant.health = data["health"]
        
        for _ in range(data.get("plant_cells_count", 0)):
            plant.add_plant_cell("leaf")
        
        return plant

    def graft_with(self, other_plant: 'Plant') -> bool:
        """Simulate plant grafting - combining parts of two plants."""
        if self.species != other_plant.species:
            return False
        
        if self.health < 50 or other_plant.health < 50:
            return False
        
        graft_success_rate = min(self.health, other_plant.health) / 100
        
        if graft_success_rate > 0.7:
            self.growth_rate = (self.growth_rate + other_plant.growth_rate) / 2
            self.height = max(self.height, other_plant.height)
            
            other_cells = other_plant.plant_cells[:len(other_plant.plant_cells)//2]
            self.plant_cells.extend(other_cells)
            
            for tissue_type, cells in other_plant.tissues.items():
                if tissue_type in self.tissues:
                    self.tissues[tissue_type].extend(cells[:len(cells)//2])
            
            self.health -= 10
            other_plant.health -= 20
            
            return True
        
        return False

    def simulate_ecosystem_interaction(self, other_organisms: List) -> Dict[str, float]:
        """Simulate interactions with other organisms in the ecosystem."""
        interactions = {
            "competition": 0.0,
            "mutualism": 0.0,
            "herbivory_damage": 0.0,
            "pollination_benefit": 0.0
        }
        
        for organism in other_organisms:
            if hasattr(organism, 'species'):
                if organism.species.startswith("Plant"):
                    distance = abs(getattr(organism, 'height', 0) - self.height)
                    if distance < 20:
                        competition = max(0, 10 - distance)
                        interactions["competition"] += competition
                        self.nutrients -= competition * 0.1
                
                elif organism.species.startswith("Bee"):
                    if self.flowering_stage == "flowering":
                        pollination = min(10, self.leaf_area * 0.1)
                        interactions["pollination_benefit"] += pollination
                        self.energy += pollination
                
                elif organism.species.startswith("Bacteria"):
                    if hasattr(organism, 'gram_stain'):
                        if "nitrogen" in organism.species.lower():
                            nitrogen_fixation = 5.0
                            interactions["mutualism"] += nitrogen_fixation
                            self.nutrients += nitrogen_fixation
        
        return interactions

    def respond_to_disease(self, pathogen_name: str, severity: float) -> str:
        """Simulate plant response to disease."""
        if severity > 8:
            self.health -= severity * 3
            self.cellular_stress_response("pathogen", severity)
            return f"{self.name} severely affected by {pathogen_name}"
        elif severity > 4:
            self.health -= severity * 1.5
            self.growth_rate *= 0.8
            return f"{self.name} moderately affected by {pathogen_name}"
        else:
            self.health -= severity
            return f"{self.name} shows mild symptoms from {pathogen_name}"

    def chemical_defense(self, herbivore_pressure: float) -> float:
        """Produce chemical compounds for defense against herbivores."""
        if herbivore_pressure > 5 and self.energy > 20:
            defense_compounds = min(self.energy * 0.2, herbivore_pressure * 2)
            self.energy -= defense_compounds
            
            for cell in self.tissues.get("leaf", []):
                if hasattr(cell, 'central_vacuole'):
                    cell.central_vacuole.store_metabolite("tannins", 0.02)
            
            return defense_compounds
        return 0.0

