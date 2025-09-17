import random
from typing import List, Optional
import matplotlib.pyplot as plt
from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
import json


class FatTissue(Tissue):
    def __init__(self, name: str, cells: Optional[List[Cell]] = None, cancer_risk: float = 0.001, 
                 lipid_content: float = 0.8, base_metabolic_rate: float = 0.02,
                 insulin_sensitivity: float = 0.7, leptin_production: float = 0.5):
        super().__init__(name, "adipose", cells, cancer_risk)
        self.lipid_content = lipid_content
        self.base_metabolic_rate = base_metabolic_rate
        self.insulin_sensitivity = insulin_sensitivity
        self.leptin_production = leptin_production
        self.glucose_level = 100  # mg/dL
        self.insulin_level = 10   # μIU/mL
        self.leptin_level = 10    # ng/mL
        self.energy_balance = 0   # kcal

    def store_fat(self, amount: float) -> None:
        """
        Increase the lipid content of the fat tissue.
        
        :param amount: The amount of fat to store (0.0 to 1.0)
        """
        self.lipid_content = min(1.0, self.lipid_content + amount)
        # Simulate cell growth when storing fat
        new_cells = int(self.get_cell_count() * (amount / 2))
        for _ in range(new_cells):
            new_cell = Cell(f"FatCell_{self.get_cell_count() + 1}", str(random.uniform(80, 100)))
            self.add_cell(new_cell)

    def burn_fat(self, amount: float) -> float:
        """
        Decrease the lipid content of the fat tissue and return the amount of energy released.
        
        :param amount: The amount of fat to burn (0.0 to 1.0)
        :return: The amount of energy released
        """
        actual_amount = min(self.lipid_content, amount)
        self.lipid_content -= actual_amount
        # Simulate cell reduction when burning fat
        cells_to_remove = int(self.get_cell_count() * (actual_amount / 2))
        for _ in range(cells_to_remove):
            if self.cells:
                self.remove_cell(self.cells[-1])
        return actual_amount * 9  # 1 gram of fat provides 9 calories of energy

    def simulate_metabolism(self, food_intake: float, physical_activity: float) -> None:
        # Simulate glucose uptake
        glucose_uptake = self.glucose_level * self.insulin_sensitivity * (self.insulin_level / 100)
        self.glucose_level -= glucose_uptake
        
        # Simulate insulin response
        if food_intake > 0:
            self.insulin_level += food_intake * 0.5
        self.insulin_level = max(0, int(self.insulin_level - 0.1 * self.insulin_level))  # Natural decay

        # Simulate leptin production
        self.leptin_level = self.lipid_content * self.leptin_production * 20

        # Calculate energy expenditure
        basal_expenditure = self.base_metabolic_rate * self.get_cell_count()
        activity_expenditure = physical_activity * 200  # Assume 200 kcal per unit of activity
        total_expenditure = basal_expenditure + activity_expenditure

        # Update energy balance
        energy_from_food = food_intake * 500  # Assume 500 kcal per unit of food
        self.energy_balance = energy_from_food - total_expenditure

        # Store or burn fat based on energy balance
        if self.energy_balance > 0:
            self.store_fat(self.energy_balance / 7700)  # Approx. 7700 kcal per kg of fat
        else:
            self.burn_fat(abs(self.energy_balance) / 7700)

    def simulate_time_step(self, food_intake: float = 0, physical_activity: float = 0, external_factors: List[tuple] = ()) -> None:
        super().simulate_time_step(external_factors)
        self.simulate_metabolism(food_intake, physical_activity)

    def get_state(self):
        return {
            "lipid_content": self.lipid_content,
            "glucose_level": self.glucose_level,
            "insulin_level": self.insulin_level,
            "leptin_level": self.leptin_level,
            "energy_balance": self.energy_balance,
            "cell_count": self.get_cell_count()
        }

    def to_json(self) -> str:
        json_dict = json.loads(super().to_json())
        json_dict.update({
            "lipid_content": self.lipid_content,
            "leptin_production": self.leptin_production,
            "base_metabolic_rate": self.base_metabolic_rate,
            "insulin_sensitivity": self.insulin_sensitivity
        })
        return json.dumps(json_dict)

    @classmethod
    def from_json(cls, json_str: str) -> 'FatTissue':
        tissue_dict = json.loads(json_str)
        cells = [Cell.from_json(cell_json) for cell_json in tissue_dict['cells']]
        fat_tissue = cls(
            name=tissue_dict['name'],
            cells=cells,
            cancer_risk=tissue_dict.get('cancer_risk', 0.001),
            lipid_content=tissue_dict['lipid_content'],
            base_metabolic_rate=tissue_dict['base_metabolic_rate'],
            insulin_sensitivity=tissue_dict['insulin_sensitivity'],
            leptin_production=tissue_dict['leptin_production'],
            )
        fat_tissue.growth_rate = tissue_dict['growth_rate']
        fat_tissue.healing_rate = tissue_dict['healing_rate']
        return fat_tissue

    def visualize_fat_tissue_metabolism(self, num_steps: int = 100):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
        lipid_content = []
        glucose_levels = []
        insulin_levels = []
        leptin_levels = []
        energy_balance = []
        cell_counts = []

        def update():
            food_intake = random.uniform(0, 2)  # Random food intake
            physical_activity = random.uniform(0, 1)  # Random physical activity
            self.simulate_time_step(food_intake, physical_activity)
        
            state = self.get_state()
            lipid_content.append(state["lipid_content"])
            glucose_levels.append(state["glucose_level"])
            insulin_levels.append(state["insulin_level"])
            leptin_levels.append(state["leptin_level"])
            energy_balance.append(state["energy_balance"])
            cell_counts.append(state["cell_count"])

            ax1.clear()
            ax1.plot(lipid_content, label="Lipid Content")
            ax1.plot(glucose_levels, label="Glucose Level")
            ax1.plot(insulin_levels, label="Insulin Level")
            ax1.plot(leptin_levels, label="Leptin Level")
            ax1.set_ylabel("Levels")
            ax1.legend()
            ax1.set_title("Metabolic Indicators Over Time")

            ax2.clear()
            ax2.plot(energy_balance, label="Energy Balance")
            ax2.plot(cell_counts, label="Cell Count")
            ax2.set_xlabel("Time Steps")
            ax2.set_ylabel("Values")
            ax2.legend()
            ax2.set_title("Energy Balance and Cell Count Over Time")

        for _ in range (num_steps):
            update()

        plt.tight_layout()
        plt.show()
