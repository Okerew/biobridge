import random

import numpy as np

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
from biobridge.definitions.organ import Organ
from biobridge.networks.system import System
from biobridge.tools.surgery_simulator import OperationResult, SurgicalSimulator

random.seed(42)
np.random.seed(42)


def test_surgical_simulator_operations():
    # Properly initialize Cell
    cell = Cell(
        name="TestCell",
        health=50,
        age=1,
        metabolism_rate=1.0,
        ph=7.0,
        osmolarity=300.0,
        structural_integrity=100.0,
        growth_rate=1.0,
        repair_rate=1.0,
        max_divisions=50,
    )

    # Properly initialize Tissue with one Cell
    tissue = Tissue(
        name="TestTissue",
        tissue_type="epithelial",
        cells=[cell],
        cancer_risk=0.001,
        mutation_rate=0.05,
    )

    # Properly initialize Organ with one Tissue
    organ = Organ(name="TestOrgan", tissues=[tissue], health=100.0)

    # Properly initialize System
    system = System(name="TestSystem")
    system.tissues.append(tissue)
    system.organs.append(organ)
    system.individual_cells.append(cell)
    system.stress_level = 0.5

    # Create simulator
    simulator = SurgicalSimulator(precision=0.9)

    # Operate on each object using your exact operate pattern
    cell_result = simulator.operate(cell, "repair", repair_amount=10)
    tissue_result = simulator.operate(tissue, "stimulate_growth", growth_factor=1.2)
    organ_result = simulator.operate(organ, "transplant")
    system_result = simulator.operate(system, "reduce_stress", stress_reduction=0.1)

    # Assertions
    for result in [cell_result, tissue_result, organ_result, system_result]:
        assert isinstance(result, OperationResult)
        assert 0 <= result.risk_score <= 1.0

    # Ensure operation history is logged
    assert len(simulator.operation_history) == 4

    # Test JSON serialization
    json_data = simulator.to_json()
    simulator2 = SurgicalSimulator.from_json(json_data)
    assert simulator2.precision == simulator.precision
    assert simulator2.operation_history == simulator.operation_history
