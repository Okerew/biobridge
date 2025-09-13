import biobridge.infection_simulator as infection_simulator
from biobridge.enviromental.infection import Infection

# Create a population
population = infection_simulator.Population(1000, 800, 600)

# Create a simulator
simulator = infection_simulator.Simulator(population, Infection)

# Create a visualizer
visualizer = infection_simulator.Visualizer(population, 800, 600)

# Infect a random person
simulator.infect(0)

# Run the simulation with visualization
while visualizer.is_open():
    simulator.update()
    visualizer.render(simulator)
    visualizer.handle_events()
    i = 0
    while i < 1000:
        simulator.infect(0)
        i = i + 1

    print(f"Infected count: {simulator.get_infected_count()}")
    print(f"Death count: {simulator.get_death_count()}")
    print(simulator.get_infection_risk(3))

# Get the final state of the population
final_state = simulator.get_population_state()
