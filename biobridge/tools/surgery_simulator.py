import json
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
from biobridge.definitions.organ import Organ
from biobridge.networks.system import System


@dataclass
class OperationResult:
    success: bool
    message: str
    risk_score: float
    details: Optional[Dict] = None


class SurgicalError(Exception):
    """Base class for all surgical simulation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"SurgicalError: {self.message}"


class InvalidTargetError(SurgicalError):
    """Raised when the target of a surgical operation is not valid."""

    def __init__(self, message: str, target_type: type):
        self.target_type = target_type
        super().__init__(message)

    def __str__(self) -> str:
        return f"InvalidTargetError: {self.message} (got {self.target_type.__name__})"


class OperationFailedError(SurgicalError):
    """Raised when a surgical operation fails critically."""

    def __init__(self, message: str, operation: str, risk_score: float):
        self.operation = operation
        self.risk_score = risk_score
        super().__init__(message)

    def __str__(self) -> str:
        return f"OperationFailedError: {self.message} during '{self.operation}' operation (risk score: {self.risk_score:.2f})"


class SurgicalSimulator:
    OPERATION_DIFFICULTIES = {
        "repair": 0.1,
        "remove_organelle": 0.3,
        "remove_cells": 0.4,
        "stimulate_growth": 0.2,
        "transplant": 0.5,
        "repair_tissue": 0.3,
        "reduce_stress": 0.2,
        "boost_immunity": 0.3,
    }

    def __init__(self, precision: float = 0.9, robot_assisted: bool = False):
        self.precision = precision
        self.robot_assisted = robot_assisted
        self.operation_history = []
        self.emergency_mode = False
        if robot_assisted:
            self.precision = min(0.99, self.precision + 0.05)

    def operate(
        self,
        target: Union[
            Cell, Tissue, Organ, System, List[Union[Cell, Tissue, Organ, System]]
        ],
        operation: str,
        **kwargs,
    ) -> Union[OperationResult, List[OperationResult]]:
        if isinstance(target, list):
            return [self._operate_single(t, operation, **kwargs) for t in target]
        return self._operate_single(target, operation, **kwargs)

    def _operate_single(
        self, target: Union[Cell, Tissue, Organ, System], operation: str, **kwargs
    ) -> OperationResult:
        if not self._is_valid_target(target):
            raise InvalidTargetError(
                "Target must be a Cell, Tissue, Organ, or System", type(target)
            )

        difficulty = self.OPERATION_DIFFICULTIES.get(operation, 0.5)
        effective_precision = self._calculate_effective_precision(difficulty)

        try:
            if isinstance(target, Cell):
                return self._operate_on_cell(
                    target, operation, effective_precision, **kwargs
                )
            elif isinstance(target, Tissue):
                return self._operate_on_tissue(
                    target, operation, effective_precision, **kwargs
                )
            elif isinstance(target, Organ):
                return self._operate_on_organ(
                    target, operation, effective_precision, **kwargs
                )
            elif isinstance(target, System):
                return self._operate_on_system(
                    target, operation, effective_precision, **kwargs
                )
        except Exception as e:
            raise OperationFailedError(str(e), operation, 1.0)

    def _is_valid_target(self, target) -> bool:
        return isinstance(target, (Cell, Tissue, Organ, System))

    def _calculate_effective_precision(self, difficulty: float) -> float:
        precision = self.precision
        if self.robot_assisted:
            precision = min(0.99, precision + 0.05)
        if self.emergency_mode:
            precision = min(0.99, precision + 0.1)
        return max(0.01, precision - difficulty)

    def _log_operation(
        self,
        result: OperationResult,
        target: Union[Cell, Tissue, Organ, System],
        operation: str,
    ):
        self.operation_history.append(
            {
                "target": str(target),
                "operation": operation,
                "success": result.success,
                "risk_score": result.risk_score,
                "message": result.message,
            }
        )

    def _operate_on_cell(
        self, cell: Cell, operation: str, precision: float, **kwargs
    ) -> OperationResult:
        result = OperationResult(success=False, message="", risk_score=0.0)

        if operation == "repair":
            repair_amount = kwargs.get("repair_amount", 10)
            if random.random() < precision:
                cell.repair(repair_amount)
                result.success = True
                result.message = (
                    f"Successfully repaired cell. Health increased by {repair_amount}."
                )
                result.risk_score = 0.1
            else:
                cell.health -= repair_amount / 2
                result.message = "Operation failed. Cell slightly damaged."
                result.risk_score = 0.5

        elif operation == "remove_organelle":
            organelle = kwargs.get("organelle", "")
            if organelle in cell.organelles:
                if random.random() < precision:
                    cell.remove_organelle(organelle)
                    result.success = True
                    result.message = f"Successfully removed {organelle} from cell."
                    result.risk_score = 0.3
                else:
                    cell.health -= 5
                    result.message = (
                        f"Failed to remove {organelle}. Cell slightly damaged."
                    )
                    result.risk_score = 0.7
            else:
                result.message = f"{organelle} not found in cell."
                result.risk_score = 0.0

        else:
            result.message = f"Unknown operation: {operation}"
            result.risk_score = 1.0

        self._log_operation(result, cell, operation)
        return result

    def _operate_on_tissue(
        self, tissue: Tissue, operation: str, precision: float, **kwargs
    ) -> OperationResult:
        result = OperationResult(success=False, message="", risk_score=0.0)

        if operation == "remove_cells":
            num_cells = kwargs.get("num_cells", 1)
            if num_cells <= len(tissue.cells):
                if random.random() < precision:
                    for _ in range(num_cells):
                        cell = random.choice(tissue.cells)
                        tissue.remove_cell(cell)
                    result.success = True
                    result.message = (
                        f"Successfully removed {num_cells} cells from tissue."
                    )
                    result.risk_score = 0.2 * num_cells
                else:
                    for _ in range(num_cells):
                        cell = random.choice(tissue.cells)
                        cell.health -= 10
                    result.message = (
                        f"Operation partially failed. {num_cells} cells damaged."
                    )
                    result.risk_score = 0.6 * num_cells
            else:
                result.message = f"Not enough cells in tissue. Current cell count: {len(tissue.cells)}"
                result.risk_score = 0.0

        elif operation == "stimulate_growth":
            growth_factor = kwargs.get("growth_factor", 1.5)
            if random.random() < precision:
                tissue.growth_rate *= growth_factor
                result.success = True
                result.message = f"Successfully stimulated tissue growth. New growth rate: {tissue.growth_rate:.2%}"
                result.risk_score = 0.1
            else:
                tissue.growth_rate *= 0.9
                result.message = (
                    "Failed to stimulate growth. Growth rate slightly decreased."
                )
                result.risk_score = 0.4

        else:
            result.message = f"Unknown operation: {operation}"
            result.risk_score = 1.0

        self._log_operation(result, tissue, operation)
        return result

    def _operate_on_organ(
        self, organ: Organ, operation: str, precision: float, **kwargs
    ) -> OperationResult:
        result = OperationResult(success=False, message="", risk_score=0.0)

        if operation == "transplant":
            if random.random() < precision:
                organ.health = 100.0
                result.success = True
                result.message = f"Successfully transplanted {organ.name}. Organ health reset to 100%."
                result.risk_score = 0.2
            else:
                organ.health *= 0.8
                result.message = f"Transplant partially successful. {organ.name} health reduced to {organ.health:.2f}%."
                result.risk_score = 0.8

        elif operation == "repair_tissue":
            tissue_index = kwargs.get("tissue_index", 0)
            if 0 <= tissue_index < len(organ.tissues):
                tissue_result = self._operate_on_tissue(
                    organ.tissues[tissue_index], "stimulate_growth", precision
                )
                result.success = tissue_result.success
                result.message = f"{'Successfully' if tissue_result.success else 'Failed to'} repair tissue in {organ.name}. {tissue_result.message}"
                result.risk_score = tissue_result.risk_score + 0.1
            else:
                result.message = f"Invalid tissue index for {organ.name}."
                result.risk_score = 0.0

        else:
            result.message = f"Unknown operation: {operation}"
            result.risk_score = 1.0

        self._log_operation(result, organ, operation)
        return result

    def _operate_on_system(
        self, system: System, operation: str, precision: float, **kwargs
    ) -> OperationResult:
        result = OperationResult(success=False, message="", risk_score=0.0)

        if operation == "reduce_stress":
            stress_reduction = kwargs.get("stress_reduction", 0.2)
            if random.random() < precision:
                system.stress_level = max(0, system.stress_level - stress_reduction)
                result.success = True
                result.message = f"Successfully reduced system stress. New stress level: {system.stress_level:.2f}"
                result.risk_score = 0.1
            else:
                system.stress_level *= 1.1
                result.message = f"Failed to reduce stress. Stress level increased to {system.stress_level:.2f}"
                result.risk_score = 0.5

        elif operation == "boost_immunity":
            immunity_boost = kwargs.get("immunity_boost", 0.1)
            if random.random() < precision:
                for tissue in system.tissues:
                    tissue.healing_rate *= 1 + immunity_boost
                result.success = True
                result.message = f"Successfully boosted system immunity. Healing rates increased by {immunity_boost:.2%}"
                result.risk_score = 0.1
            else:
                for tissue in system.tissues:
                    tissue.healing_rate *= 0.95
                result.message = (
                    "Failed to boost immunity. Healing rates slightly decreased."
                )
                result.risk_score = 0.4

        else:
            result.message = f"Unknown operation: {operation}"
            result.risk_score = 1.0

        self._log_operation(result, system, operation)
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
            self.precision = max(0.01, self.precision - 0.05)

    def toggle_emergency_mode(self):
        self.emergency_mode = not self.emergency_mode
        if self.emergency_mode:
            self.precision = min(0.99, self.precision + 0.1)

    def to_json(self) -> str:
        return json.dumps(
            {
                "precision": self.precision,
                "robot_assisted": self.robot_assisted,
                "emergency_mode": self.emergency_mode,
                "operation_history": self.operation_history,
            }
        )

    @classmethod
    def from_json(cls, json_data: str):
        data = json.loads(json_data)
        simulator = cls(data["precision"], data["robot_assisted"])
        simulator.emergency_mode = data.get("emergency_mode", False)
        simulator.operation_history = data.get("operation_history", [])
        return simulator

    def __str__(self):
        return (
            f"SurgicalSimulator(precision={self.precision:.2f}, "
            f"robot_assisted={self.robot_assisted}, "
            f"emergency_mode={self.emergency_mode}, "
            f"operations_performed={len(self.operation_history)})"
        )
