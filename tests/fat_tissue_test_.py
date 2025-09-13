from biobridge.definitions.tissues.fat import FatTissue
import random
import numpy as np
import matplotlib.pyplot as plt

def test_fat_tissue_metabolism():
    # Initialize a fat tissue
    fat_tissue = FatTissue("Test Fat Tissue", lipid_content=0.6, base_metabolic_rate=0.03)

    # Run simulation for 30 days
    days = 30
    daily_states = []

    for day in range(days):
        # Simulate varying food intake and physical activity
        food_intake = random.uniform(0.5, 3)  # Between 0.5 and 3 units of food per day
        physical_activity = random.uniform(0, 2)  # Between 0 and 2 units of activity per day

        fat_tissue.simulate_time_step(food_intake, physical_activity)
        daily_states.append(fat_tissue.get_state())

    # Analyze results
    lipid_contents = [state["lipid_content"] for state in daily_states]
    glucose_levels = [state["glucose_level"] for state in daily_states]
    insulin_levels = [state["insulin_level"] for state in daily_states]
    leptin_levels = [state["leptin_level"] for state in daily_states]
    energy_balances = [state["energy_balance"] for state in daily_states]
    cell_counts = [state["cell_count"] for state in daily_states]

    # Print summary statistics
    print(f"Initial lipid content: {lipid_contents[0]:.2f}")
    print(f"Final lipid content: {lipid_contents[-1]:.2f}")
    print(f"Average glucose level: {np.mean(glucose_levels):.2f} mg/dL")
    print(f"Average insulin level: {np.mean(insulin_levels):.2f} μIU/mL")
    print(f"Average leptin level: {np.mean(leptin_levels):.2f} ng/mL")
    print(f"Total energy balance: {sum(energy_balances):.2f} kcal")
    print(f"Net cell change: {cell_counts[-1] - cell_counts[0]}")

    # Visualize results
    plt.figure(figsize=(12, 8))
    plt.plot(lipid_contents, label="Lipid Content")
    plt.plot(np.array(glucose_levels) / 100, label="Glucose Level (scaled)")
    plt.plot(np.array(insulin_levels) / 10, label="Insulin Level (scaled)")
    plt.plot(np.array(leptin_levels) / 10, label="Leptin Level (scaled)")
    plt.plot(np.array(energy_balances) / 1000, label="Energy Balance (scaled)")
    plt.plot(np.array(cell_counts) / max(cell_counts), label="Cell Count (normalized)")
    plt.xlabel("Days")
    plt.ylabel("Values")
    plt.title("Fat Tissue Metabolism Over 30 Days")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the test
test_fat_tissue_metabolism()

# Visualize metabolism in real-time
fat_tissue = FatTissue("Visualized Fat Tissue", lipid_content=0.7, base_metabolic_rate=0.025)
fat_tissue.visualize_fat_tissue_metabolism(num_steps=200)
