import biobridge.embryo_simulator as embryo_simulator

# Create a simulation with 1 initial cell
sim = embryo_simulator.EmbryoSimulation(1)

# Run the simulation for 100 steps
sim.run(100)

# Get the final state of cells and tissues
cells = sim.getCells()
tissues = sim.getTissues()
organs = sim.getOrgans()
systems = sim.getSystems()

# Print some information about the final state
print(f"Number of cells: {len(cells)}")
print(f"Number of tissues: {len(tissues)}")


for tissue in tissues:
    print(f"Tissue {tissue.name}: {len(tissue.cells)} cells")

for organ in organs:
    print(f"Organ {organ.name}: {len(organ.tissues)} tissues")

# Visualize the final state
sim.visualize()
