import random
from typing import Union
from biobridge.blocks.cell import Cell, json
from biobridge.blocks.tissue import Tissue
from biobridge.networks.system import System
from biobridge.definitions.organ import Organ


class SurgicalSimulator:
    def __init__(self, precision: float = 0.9, robot_assisted: bool = False):
        self.precision = precision
        self.robot_assisted = robot_assisted
        if robot_assisted:
            self.precision = min(0.99, self.precision + 0.05)  # Robot assistance increases precision

    def operate(self, target: Union[Cell, Tissue, Organ, System], operation: str, **kwargs) -> dict:
        if isinstance(target, Cell):
            return self._operate_on_cell(target, operation, **kwargs)
        elif isinstance(target, Tissue):
            return self._operate_on_tissue(target, operation, **kwargs)
        elif isinstance(target, Organ):
            return self._operate_on_organ(target, operation, **kwargs)
        elif isinstance(target, System):
            return self._operate_on_system(target, operation, **kwargs)
        else:
            raise ValueError("Target must be either a Cell, Tissue, Organ, or System")

    def _operate_on_cell(self, cell: Cell, operation: str, **kwargs) -> dict:
        result = {"success": False, "message": ""}

        if operation == "repair":
            repair_amount = kwargs.get("repair_amount", 10)
            if random.random() < self.precision:
                cell.repair(repair_amount)
                result["success"] = True
                result["message"] = f"Successfully repaired cell. Health increased by {repair_amount}."
            else:
                cell.health -= repair_amount / 2
                result["message"] = "Operation failed. Cell slightly damaged."

        elif operation == "remove_organelle":
            organelle = kwargs.get("organelle", "")
            if organelle in cell.organelles:
                if random.random() < self.precision:
                    cell.remove_organelle(organelle)
                    result["success"] = True
                    result["message"] = f"Successfully removed {organelle} from cell."
                else:
                    cell.health -= 5
                    result["message"] = f"Failed to remove {organelle}. Cell slightly damaged."
            else:
                result["message"] = f"{organelle} not found in cell."

        else:
            result["message"] = f"Unknown operation: {operation}"

        return result

    def _operate_on_tissue(self, tissue: Tissue, operation: str, **kwargs) -> dict:
        result = {"success": False, "message": ""}

        if operation == "remove_cells":
            num_cells = kwargs.get("num_cells", 1)
            if num_cells <= len(tissue.cells):
                if random.random() < self.precision:
                    for _ in range(num_cells):
                        cell = random.choice(tissue.cells)
                        tissue.remove_cell(cell)
                    result["success"] = True
                    result["message"] = f"Successfully removed {num_cells} cells from tissue."
                else:
                    for _ in range(num_cells):
                        cell = random.choice(tissue.cells)
                        cell.health -= 10
                    result["message"] = f"Operation partially failed. {num_cells} cells damaged."
            else:
                result["message"] = f"Not enough cells in tissue. Current cell count: {len(tissue.cells)}"

        elif operation == "stimulate_growth":
            growth_factor = kwargs.get("growth_factor", 1.5)
            if random.random() < self.precision:
                tissue.growth_rate *= growth_factor
                result["success"] = True
                result["message"] = f"Successfully stimulated tissue growth. New growth rate: {tissue.growth_rate:.2%}"
            else:
                tissue.growth_rate *= 0.9
                result["message"] = "Failed to stimulate growth. Growth rate slightly decreased."

        else:
            result["message"] = f"Unknown operation: {operation}"

        return result

    def _operate_on_organ(self, organ: Organ, operation: str, **kwargs) -> dict:
        result = {"success": False, "message": ""}

        if operation == "transplant":
            if random.random() < self.precision:
                organ.health = 100.0
                result["success"] = True
                result["message"] = f"Successfully transplanted {organ.name}. Organ health reset to 100%."
            else:
                organ.health *= 0.8
                result["message"] = f"Transplant partially successful. {organ.name} health reduced to {organ.health:.2f}%."

        elif operation == "repair_tissue":
            tissue_index = kwargs.get("tissue_index", 0)
            if 0 <= tissue_index < len(organ.tissues):
                tissue_result = self._operate_on_tissue(organ.tissues[tissue_index], "stimulate_growth")
                if tissue_result["success"]:
                    result["success"] = True
                    result["message"] = f"Successfully repaired tissue in {organ.name}. {tissue_result['message']}"
                else:
                    result["message"] = f"Failed to repair tissue in {organ.name}. {tissue_result['message']}"
            else:
                result["message"] = f"Invalid tissue index for {organ.name}."

        else:
            result["message"] = f"Unknown operation: {operation}"

        return result

    def _operate_on_system(self, system: System, operation: str, **kwargs) -> dict:
        result = {"success": False, "message": ""}

        if operation == "reduce_stress":
            stress_reduction = kwargs.get("stress_reduction", 0.2)
            if random.random() < self.precision:
                system.stress_level = max(0, system.stress_level - stress_reduction)
                result["success"] = True
                result["message"] = f"Successfully reduced system stress. New stress level: {system.stress_level:.2f}"
            else:
                system.stress_level *= 1.1
                result["message"] = f"Failed to reduce stress. Stress level increased to {system.stress_level:.2f}"

        elif operation == "boost_immunity":
            immunity_boost = kwargs.get("immunity_boost", 0.1)
            if random.random() < self.precision:
                for tissue in system.tissues:
                    tissue.healing_rate *= (1 + immunity_boost)
                result["success"] = True
                result["message"] = f"Successfully boosted system immunity. Healing rates increased by {immunity_boost:.2%}"
            else:
                for tissue in system.tissues:
                    tissue.healing_rate *= 0.95
                result["message"] = "Failed to boost immunity. Healing rates slightly decreased."

        else:
            result["message"] = f"Unknown operation: {operation}"

        return result

    def change_precision(self, new_precision: float):
        self.precision = new_precision
        if self.robot_assisted:
            self.precision = min(0.99, self.precision + 0.05)

    def toggle_robot_assistance(self):
        self.robot_assisted = not self.robot_assisted
        if self.robot_assisted:
            self.precision = min(0.99, self.precision + 0.05)
        else:
            self.precision = max(0, int(self.precision - 0.05))

    def to_json(self) -> str:
        return json.dumps({
            "precision": self.precision,
            "robot_assisted": self.robot_assisted
        })

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(json_data["precision"], json_data["robot_assisted"])

    def __str__(self):
        return f"SurgicalSimulator(precision={self.precision:.2f}, robot_assisted={self.robot_assisted})"
