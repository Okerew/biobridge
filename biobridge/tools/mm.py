import random
from typing import List, Union
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell
import json
import time


class MolecularMachinery:
    def __init__(self, name: str, components: List[Union[Protein, Cell]], function: str):
        self.name = name
        self.components = components
        self.function = function
        self.efficiency = random.uniform(0.5, 1.0)
        self.energy_level = 100.0
        self.energy_consumed = 0.0
        self.performance_history = []
        self.last_maintenance = time.time()
        self.age = 0
        self.mutation_rate = 0.001

    @classmethod
    def create_ribosome(cls):
        return cls("Ribosome",
                   [Protein("Small subunit", "AAGGCUAUGUUCGC"),
                    Protein("Large subunit", "UACCCGAAGACUAG")],
                   "Protein synthesis")

    @classmethod
    def create_atp_synthase(cls):
        return cls("ATP Synthase",
                   [Protein("F0 subunit", "MENLNMDLLYMAAAVMMGLAAIGAAIGIGILGGKFLEGAARQPDLIPLLRTQFFIVMGLVDAIPMIAVGLGLYVMFAVA"),
                    Protein("F1 subunit", "MQLNSTEISELIKQRIAQFNVVSEAHNEGTIVSVSDGVIRIHGLADCMQGEMISLPGNRYAIALNLERDSVGAVVMGPYADLAEGMKVKCTGRILEVPVGRGLLGRVVNTLGAPIDGKGPLDHDGFSAVEAIAPGVIERQSVDQPVQTGYKAVDSMIPIGRGQRELIIGDRQTGKTSIAIDTIINQKRFNDGTDEKKKLYCIYVAIGQKRSTVAQLVKRLTDADAMKYTIVVSATASDAAPLQYLAPYSGCSMGEYFRDNGKHALIIYDDLSKQAVAYRQMSLLLRRPPGREAYPGDVFYLHSRLLERAAKMNDAFGGGSLTALPVIETQAGDVSAYIPTNVISITDGQIFLETELFYKGIRPAINVGLSVSRVGSAAQTRAMKQVAGTMKLELAQYREVAAFAQFGSDLDAATQQLLSRGVRLTELLKQGQYSPMAIEEQVAVIYAGVRGYLDKLEPSKITKFENAFLSHVISQHQALLGKIRTDGKISEESDAKLKEIVTNFLAGFEA")],
                   "ATP synthesis")

    @classmethod
    def create_dna_polymerase(cls):
        return cls("DNA Polymerase",
                   [Protein("Catalytic subunit", "MIVSDIEANALLESVTKFHCGVIYDYSTAEYVSYRPSDFGAYLDALEAEVARGGLIVFHNGHKYDVPALTKLAKLQLNREFHLPRENCIDTLVLSRLIHSNLKDTDMGLLRSGKLPGKRFGSHALEAWGYRLGEMKGEYKDDFKRMLEEQGEEYVDGMEWWNFNEEMMDYNVQDVVVTKALLEKLLSDKHYFPPEIDFTDVGYTTFWSESLEAVDIEHRAAWLLAKQERNGFPFDTKAIEELYVELAARRSELLRKLTETFGSWYQPKGGTEMFCHPRTGKPLPKYPRIKTPKVGGIFKKPKNKAQREGREPCELDTREYVAGAPYTPVEHVVFNPSSRDHIQKKLQEAGWVPTKYTDKGAPVVDDEVLEGVRVDDPEKQAAIDLIKEYLMIQKRIGQSAEGDKAWLRYVAEDGKIHGSVNPNGAVTGRATHAFPNLAQIPGVRSPYGEQCRAAFGAEHHLDGITGKPWVQAGIDASGLELRCLAHFMARFDNGEYAHEILNGDIHTKNQIAAELPTRDNAKTFIYGFLYGAGDEKIGQIVGAGKERGKELKKKFLENTPAIAALRESIQQTLVESSQWVAGEQQVKWKRRWIKGLDGRKVHVRSPHAALNTLLQSAGALICKLWIIKTEEMLVEKGLKHGWDGDFAYMAWVHDEIQVGCRTEEIAQVVIETAQEAMRWVGDHWNFRCLLDTEGKMGPNWAICH")],
                   "DNA replication")

    @classmethod
    def create_custom(cls, name: str, components: List[Union[Protein, Cell]], function: str):
        return cls(name, components, function)

    def interact(self, target: Union[Protein, Cell]):
        interaction_strength = random.uniform(0, 1) * self.efficiency
        self.energy_level -= random.uniform(1, 5)

        if isinstance(target, Protein):
            return f"{self.name} interacts with protein {target.name} with strength {interaction_strength:.2f}"
        elif isinstance(target, Cell):
            return f"{self.name} interacts with cell {target.name} with strength {interaction_strength:.2f}"

    def perform_function(self):
        if self.energy_level < 10:
            return f"{self.name} is too low on energy to perform its function."

        success_probability = self.efficiency * (self.energy_level / 100)
        energy_used = random.uniform(5, 15)
        self.energy_level -= energy_used
        self.energy_consumed += energy_used  # Track energy consumption

        if random.random() < success_probability:
            return f"{self.name} successfully performs its function: {self.function}"
        else:
            return f"{self.name} fails to perform its function: {self.function}"

    def energy_consumption_report(self):
        return f"{self.name} has consumed {self.energy_consumed:.2f} units of energy."

    def recharge(self, amount: float):
        self.energy_level = min(100, int(self.energy_level + amount))
        return f"{self.name} recharged. New energy level: {self.energy_level:.2f}"

    def component_details(self):
        details = []
        for component in self.components:
            if isinstance(component, Protein):
                details.append(f"Protein: {component.name}, Sequence: {component.sequence}")
            elif isinstance(component, Cell):
                details.append(f"Cell: {component.name}, Type: {component.cell_type}")
        return "\n".join(details)

    def to_json(self):
        data = {
            "name": self.name,
            "components": [{"type": type(comp).__name__, "name": comp.name, "details": comp.__dict__} for comp in
                           self.components],
            "function": self.function,
            "efficiency": self.efficiency,
            "energy_level": self.energy_level,
            "age": self.age,
            "mutation_rate": self.mutation_rate,
            "performance_history": self.performance_history,
            "last_maintenance": self.last_maintenance
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        components = []
        for comp in data['components']:
            if comp['type'] == 'Protein':
                components.append(Protein(comp['name'], comp['details']['sequence']))
            elif comp['type'] == 'Cell':
                components.append(Cell(comp['name'], comp['details']['cell_type']))
        obj = cls(data['name'], components, data['function'])
        obj.efficiency = data['efficiency']
        obj.energy_level = data['energy_level']
        obj.age = data['age']
        obj.mutation_rate = data['mutation_rate']
        obj.performance_history = data['performance_history']
        obj.last_maintenance = data['last_maintenance']
        return obj

    def internal_interaction(self):
        if len(self.components) < 2:
            return "Not enough components for internal interaction."
        comp1, comp2 = random.sample(self.components, 2)
        interaction_strength = random.uniform(0, 1)
        return f"Component {comp1.name} interacts with {comp2.name} with strength {interaction_strength:.2f}"

    def add_component(self, component: Union[Protein, Cell]):
        if isinstance(component, (Protein, Cell)):
            self.components.append(component)
            return f"Component {component.name} added."
        else:
            return "Invalid component type."

    def remove_component(self, component_name: str):
        for component in self.components:
            if component.name == component_name:
                self.components.remove(component)
                return f"Component {component_name} removed."
        return "Component not found."

    def age_machinery(self, time_units: int):
        self.age += time_units
        self.efficiency *= (1 - 0.01 * time_units)  # Efficiency decreases with age
        return f"{self.name} aged by {time_units} units. New efficiency: {self.efficiency:.2f}"

    def mutate(self):
        if random.random() < self.mutation_rate:
            self.efficiency += random.uniform(-0.1, 0.1)
            self.efficiency = max(0, min(1, int(self.efficiency)))
            return f"{self.name} has mutated. New efficiency: {self.efficiency:.2f}"
        return f"{self.name} did not mutate."

    def perform_maintenance(self):
        current_time = time.time()
        time_since_last_maintenance = current_time - self.last_maintenance

        if time_since_last_maintenance > 86400:  # 24 hours in seconds
            self.efficiency += 0.1
            self.efficiency = min(1, int(self.efficiency))
            self.last_maintenance = current_time
            return f"Maintenance performed on {self.name}. Efficiency improved to {self.efficiency:.2f}"
        else:
            return f"Maintenance for {self.name} not yet needed."

    def analyze_performance(self):
        if not self.performance_history:
            return "No performance data available."

        success_rate = sum(self.performance_history) / len(self.performance_history)
        return f"Performance analysis for {self.name}:\nSuccess rate: {success_rate:.2f}\nTotal operations: {len(self.performance_history)}"

    def emergency_shutdown(self):
        self.energy_level = 0
        return f"{self.name} has been shut down for emergency maintenance."

    def consume_energy(self, amount: float):
        self.energy_level = max(0, int(self.energy_level - amount))
        self.energy_consumed += amount

    def optimize(self):
        if self.energy_level > 50:
            optimization_factor = random.uniform(0.01, 0.05)
            self.efficiency += optimization_factor
            self.efficiency = min(1, int(self.efficiency))
            self.consume_energy(10)
            return f"{self.name} optimized. Efficiency increased by {optimization_factor:.2f}"
        else:
            return f"{self.name} doesn't have enough energy for optimization."

    def __str__(self):
        return f"Molecular Machinery: {self.name}\nFunction: {self.function}\nEfficiency: {self.efficiency:.2f}\nEnergy Level: {self.energy_level:.2f}\nComponents: {', '.join(comp.name for comp in self.components)}"
