import json
import random
from typing import List, Optional

from biobridge.definitions.organ import Organ
from biobridge.enviromental.infection import Infection, InfectionType
from biobridge.genes.dna import DNA
from biobridge.networks.ims import ImmuneSystem
from biobridge.networks.system import Cell, System


class AdvancedOrganism:
    def __init__(
        self,
        name: str,
        dna: "DNA",
        age: Optional[int] = 0,
        max_age: Optional[int] = 100,
        maturity: Optional[int] = 10,
        sex: Optional[str] = None,
    ):
        self.name = name
        self.dna = dna
        self.systems: List[System] = []
        self.organs: List[Organ] = []
        self.health = 100.0
        self.energy = 100.0
        self.adaptation_rate = 0.1
        self.mutation_rate = 0.01
        self.beneficial_mutation_chance = 0.1
        self.age = age
        self.max_age = max_age
        self.maturity_age = maturity
        self.sex = sex
        self.immune_system = self._setup_immune_system()

    def _setup_immune_system(self):
        # Define initial immune cells based on DNA and organism characteristics
        initial_cells = self._generate_initial_immune_cells()
        return ImmuneSystem(Cell, initial_cells)

    def _generate_initial_immune_cells(self):
        cells = []
        dna_sequence = self.dna.get_sequence(1)

        # Use DNA to determine initial cell counts and strengths
        macrophage_count = dna_sequence.count("A") // 10 + 1
        tcell_count = dna_sequence.count("T") // 10 + 1
        bcell_count = dna_sequence.count("G") // 10 + 1

        # Calculate base strength from DNA
        base_strength = len(set(dna_sequence)) / len(dna_sequence)

        # Adjust strength based on age and health
        age_factor = 1 - (self.age / self.max_age) * 0.5
        health_factor = self.health / 100
        adjusted_strength = base_strength * age_factor * health_factor

        # Generate cells
        for i in range(macrophage_count):
            cells.append(
                (
                    f"Macrophage{i + 1}",
                    adjusted_strength * random.uniform(0.9, 1.1),
                    "Macrophage",
                )
            )
        for i in range(tcell_count):
            cells.append(
                (f"TCell{i + 1}", adjusted_strength * random.uniform(0.9, 1.1), "TCell")
            )
        for i in range(bcell_count):
            cells.append(
                (f"BCell{i + 1}", adjusted_strength * random.uniform(0.9, 1.1), "BCell")
            )

        return cells

    def _determine_input_neurons(self):
        # Determine input neurons based on the organism's sensors and state
        inputs = [
            ("health", lambda: self.get_health() / 100),
            ("energy", lambda: self.energy / 100),
        ]

        # Add inputs for each system
        for system in self.systems:
            inputs.append((f"system_{system.__class__.__name__}", system.get_status))

        # Add inputs for each organ
        for organ in self.organs:
            inputs.append((f"organ_{organ.name}", lambda o=organ: o.get_health() / 100))

        return inputs

    def _determine_hidden_neurons(self):
        # Determine the number of hidden neurons based on the organism's complexity
        return max(5, len(self.systems) + len(self.organs))

    def _determine_output_neurons(self):
        # Determine output neurons based on the organism's possible actions
        outputs = [
            ("rest", self._action_rest),
            ("eat", self._action_eat),
            ("move", self._action_move),
            ("reproduce", self._action_reproduce),
        ]

        # Add specific actions for each system
        for system in self.systems:
            outputs.append(
                (f"system_{system.__class__.__name__}", system.perform_action)
            )

        return outputs

    def add_system(self, system: System):
        self.systems.append(system)

    def add_organ(self, organ: Organ):
        self.organs.append(organ)

    def get_health(self) -> float:
        if not self.systems and not self.organs:
            return self.health
        system_health = (
            sum(system.get_average_system_health() for system in self.systems)
            / len(self.systems)
            if self.systems
            else 0
        )
        organ_health = (
            sum(organ.get_health() for organ in self.organs) / len(self.organs)
            if self.organs
            else 0
        )
        return (system_health + organ_health) / 2 if self.systems or self.organs else 0

    def _action_rest(self):
        self.energy = min(100, int(self.energy + 10))
        print(f"{self.name} is resting. Energy increased to {self.energy}")

    def _action_eat(self):
        self.energy = min(100, int(self.energy + 20))
        print(f"{self.name} is eating. Energy increased to {self.energy}")

    def _action_move(self):
        if self.energy >= 10:
            self.energy -= 10
            print(f"{self.name} is moving. Energy decreased to {self.energy}")
        else:
            print(f"{self.name} is too tired to move")

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
                    print(
                        f"Potentially harmful mutation occurred in organ {organ.name}"
                    )

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
            f"Age: {self.age}",
            "\nSystems:",
            *[system.get_system_status() for system in self.systems],
            "\nOrgans:",
            *[organ.describe() for organ in self.organs],
            "\nImmune System:",
            f"Total Immune Cells: {len(self.immune_system.getCells())}",
            *[
                f"{cell_type}: {count}"
                for cell_type, count in self._count_immune_cells().items()
            ],
        ]
        return "\n".join(description)

    def to_json(self) -> str:
        return json.dumps(
            {
                "name": self.name,
                "dna": self.dna.to_json(),
                "systems": [system.to_json() for system in self.systems],
                "organs": [organ.to_json() for organ in self.organs],
                "health": self.health,
                "energy": self.energy,
                "adaptation_rate": self.adaptation_rate,
                "mutation_rate": self.mutation_rate,
                "beneficial_mutation_chance": self.beneficial_mutation_chance,
                "age": self.age,
                "max_age": self.max_age,
                "maturity_age": self.maturity_age,
                "sex": self.sex,
            }
        )

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
        organism.age = data["age"]
        organism.max_age = data["max_age"]
        organism.maturity_age = data["maturity_age"]
        organism.sex = data["sex"]
        return organism

    def _action_reproduce(self):
        if self.can_reproduce():
            offspring = self.asexual_reproduce()
            self.reproduction_cooldown = 30  # Increased cooldown period
            return offspring
        else:
            print(f"{self.name} cannot reproduce at this time.")
        return None

    def can_reproduce(self) -> bool:
        if self.energy < 60:
            print(f"{self.name} doesn't have enough energy to reproduce")
            return False
        if self.get_health() <= 70:
            print(f"{self.name} is not healthy enough to reproduce")
            return False
        if self.age < self.maturity_age:
            print(f"{self.name} is too young to reproduce")
            return False
        if self.age > self.max_age:
            print(f"{self.name} is too old to reproduce")
            return False
        if self.reproduction_cooldown > 0:
            print(
                f"{self.name} is still in the reproduction cooldown period ({self.reproduction_cooldown} time units left)"
            )
            return False
        return True

    def asexual_reproduce(self) -> "AdvancedOrganism":
        self.energy -= 60
        print(
            f"{self.name} is reproducing asexually. Energy decreased to {self.energy}"
        )

        new_dna = self.dna
        new_dna.absolute_random_mutate(self.mutation_rate * 2)
        offspring = AdvancedOrganism(name=f"Clone of {self.name}", dna=new_dna)

        # Inherit traits from parent with variation
        offspring.adaptation_rate = max(
            0.01, min(0.5, self.adaptation_rate * random.uniform(0.8, 1.2))
        )
        offspring.mutation_rate = max(
            0.001, min(0.1, self.mutation_rate * random.uniform(0.8, 1.2))
        )
        offspring.beneficial_mutation_chance = max(
            0.01, min(0.5, self.beneficial_mutation_chance * random.uniform(0.8, 1.2))
        )

        # Inherit systems and organs with possible mutations
        for system in self.systems:
            new_system = system.__class__(system.name)
            if random.random() < self.mutation_rate:
                new_system.mutate()
            offspring.add_system(new_system)

        for organ in self.organs:
            new_organ = organ.__class__(organ.name, organ.tissues)
            if random.random() < self.mutation_rate:
                new_organ.mutate()
            offspring.add_organ(new_organ)

        print(
            f"New organism {offspring.name} has been born through asexual reproduction!"
        )
        return offspring

    def sexual_reproduce(
        self, partner: "AdvancedOrganism"
    ) -> Optional["AdvancedOrganism"]:
        if not self.can_reproduce() or not partner.can_reproduce():
            return None

        if self.sex == partner.sex:
            print(
                f"Sexual reproduction failed: {self.name} and {partner.name} are the same sex."
            )
            return None

        self.energy -= 60
        partner.energy -= 60
        print(
            f"{self.name} and {partner.name} are reproducing sexually. Both parents' energy decreased by 60."
        )

        new_dna = self.combine_dna(self.dna, partner.dna)
        new_dna.absolute_random_mutate(self.mutation_rate)
        offspring = AdvancedOrganism(
            name=f"Offspring of {self.name} and {partner.name}", dna=new_dna
        )

        # Inherit traits from parents with variation
        offspring.adaptation_rate = max(
            0.01,
            min(
                0.5,
                (self.adaptation_rate + partner.adaptation_rate)
                / 2
                * random.uniform(0.9, 1.1),
            ),
        )
        offspring.mutation_rate = max(
            0.001,
            min(
                0.1,
                (self.mutation_rate + partner.mutation_rate)
                / 2
                * random.uniform(0.9, 1.1),
            ),
        )
        offspring.beneficial_mutation_chance = max(
            0.01,
            min(
                0.5,
                (self.beneficial_mutation_chance + partner.beneficial_mutation_chance)
                / 2
                * random.uniform(0.9, 1.1),
            ),
        )

        # Inherit systems and organs with possible mutations and combinations
        self.inherit_systems_and_organs(offspring, partner)

        self.reproduction_cooldown = 30
        partner.reproduction_cooldown = 30

        print(
            f"New organism {offspring.name} has been born through sexual reproduction!"
        )
        return offspring

    def inherit_systems_and_organs(
        self, offspring: "AdvancedOrganism", partner: "AdvancedOrganism"
    ):
        # Inherit systems
        all_systems = set(
            type(system, system.name) for system in self.systems + partner.systems
        )
        for system_class in all_systems:
            if random.random() < 0.5:  # 50% chance to inherit each system
                new_system = system_class()
                if random.random() < self.mutation_rate:
                    new_system.mutate()
                offspring.add_system(new_system)

        # Inherit organs
        all_organs = set(
            (type(organ), organ.name, organ.tissues)
            for organ in self.organs + partner.organs
        )
        for organ_class, organ_name, organ_tissues in all_organs:
            if random.random() < 0.5:  # 50% chance to inherit each organ
                new_organ = organ_class(organ_name, organ_tissues)
                if random.random() < self.mutation_rate:
                    new_organ.mutate()
                offspring.add_organ(new_organ)

    @staticmethod
    def combine_dna(dna1: "DNA", dna2: "DNA") -> "DNA":
        sequence1 = dna1.get_sequence(1)
        sequence2 = dna2.get_sequence(1)
        crossover_point = random.randint(0, len(sequence1) - 1)
        new_sequence = sequence1[:crossover_point] + sequence2[crossover_point:]
        return DNA(new_sequence)

    def update(self, external_factors: Optional[List[tuple]] = None):
        for system in self.systems:
            system.simulate_time_step(external_factors)

        for organ in self.organs:
            if external_factors:
                for factor, intensity in external_factors:
                    if factor == "toxin":
                        organ.damage(intensity * 5)
                    elif factor == "nutrient":
                        organ.heal(intensity * 3)

        self.regulate_mutations()
        self.adapt()
        infection_strength = sum(
            intensity for factor, intensity in external_factors if factor == "toxin"
        )
        spread_rate = infection_strength * 0.1
        infection_type = random.choice(list(InfectionType))
        infection = Infection(
            name="Infection",
            infection_type=infection_type,
            spread_rate=spread_rate,
            genetic_code="",
        )

        for organ in self.organs:
            for tissue in organ.tissues:
                # Immune system response
                if external_factors:
                    self.immune_system.respond(infection, tissue.cells)

        self._maintain_immune_system()

        self.age += 1
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # Age-related effects
        if (
            self.age > self.max_age * 0.7
        ):  # Organism starts to deteriorate after 70% of max age
            self.health -= 0.1 * (self.age - self.max_age * 0.7)
            self.energy -= 0.1 * (self.age - self.max_age * 0.7)

    def _count_immune_cells(self):
        cell_counts = {"Macrophage": 0, "TCell": 0, "BCell": 0}
        for cell in self.immune_system.getCells():
            cell_type = cell.cell_type
            if cell_type in cell_counts:
                cell_counts[cell_type] += 1
        return cell_counts

    def _create_immune_cell(
        self, name, cell_type, strength: Optional[float] = random.uniform(0.5, 1.5)
    ):
        cell = {
            "name": name,
            "cell_type": cell_type,
            "strength": strength,
        }
        return cell

    def _maintain_immune_system(self):
        # Simulate cell lifecycle and replenishment
        cells_to_remove = []
        for cell in self.immune_system.getCells():
            # Age the cell
            cell.age = cell.age + 1

            # Check for cell death
            if cell.age <= 0 or cell.health <= 0:
                cells_to_remove.append(cell)

        # Remove dead cells
        for cell in cells_to_remove:
            self.immune_system.cells.remove(cell)

        # Maintain a minimum number of each cell type
        cell_counts = self._count_immune_cells()
        min_count = max(
            3, int(self.health / 20)
        )  # Minimum cell count based on overall health

        for cell_type, count in cell_counts.items():
            if count < min_count:
                for _ in range(min_count - count):
                    new_cell = self._create_immune_cell(
                        f"{cell_type}_{random.randint(1000, 9999)}", cell_type
                    )
                    cells = self.immune_system.getCells()
                    cell_tuple = (
                        new_cell["name"],
                        new_cell["strength"],
                        new_cell["cell_type"],
                    )
                    cells.append(cell_tuple)
                    self.immune_system = ImmuneSystem(Cell, cells)
