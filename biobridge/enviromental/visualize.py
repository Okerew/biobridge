import time

import biobridge.enviromental.visualizer as visualizer
from biobridge.enviromental.environment import Environment


class VisualizerWrapper:
    def __init__(self, environment: Environment):
        self.environment = environment
        self.vis = visualizer.Visualizer(
            environment.width * 20, environment.height * 20
        )
        self.running = False
        self.vis.setMoveCell(
            self.move_cell
        )  # Use setMoveCell instead of direct assignment

    def start(self):
        self.running = True
        self.run_visualizer()

    def stop(self):
        self.running = False
        cell_positions = self.vis.getCellPositions()
        return cell_positions

    def run_visualizer(self):
        while self.running:
            cell_data = self.environment.get_cell_positions()
            self.vis.update(cell_data)
            if not self.vis.run_once():
                self.running = False
            time.sleep(0.1)  # Update every 100ms

    def move_cell(self, cell_id: int, new_x: int, new_y: int):
        self.environment.move_cell(cell_id, new_x, new_y)
