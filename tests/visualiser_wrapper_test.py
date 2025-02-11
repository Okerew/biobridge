# biobridge/visualizer_wrapper.py
from biobridge.enviromental.environment import Environment
from biobridge.enviromental.visualize import VisualizerWrapper


def visualize_environment(environment: Environment):
    wrapper = VisualizerWrapper(environment)
    wrapper.start()
    return wrapper


if __name__ == "__main__":
    env = Environment("Test Environment", 40, 30, 25, 60)

    # Add some cells for testing
    from biobridge.blocks.cell import Cell

    for _ in range(10):
        cell = Cell(name="blood")
        env.add_cell(cell, env._get_random_position())

    wrapper = visualize_environment(env)

    # Stop the visualizer and get the cell positions
    cell_positions = wrapper.stop()
    print("Final cell positions:", cell_positions)
