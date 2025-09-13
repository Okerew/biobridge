from biobridge.networks.system import System, Tissue
# Create a new system
body = System("Human Body")

# Create and add tissues
skin = Tissue("Skin", "epithelial")
muscle = Tissue("Muscle", "muscle")
body.add_tissue(skin)
body.add_tissue(muscle)
skin.visualize_tissue()

# Simulate some time steps with varying conditions
for i in range(20):
    if i % 5 == 0:
        body.apply_system_wide_stress(0.1)  # Apply stress every 5 steps
    body.simulate_time_step()

    if i % 3 == 0:
        # Add a new tissue every 3 steps
        new_tissue = Tissue(f"Tissue_{i}", "connective")
        body.add_tissue(new_tissue)

    print(f"Step {i + 1}:")
    print(body.get_system_status())
    print("\n" + "=" * 50 + "\n")

body.visualize_network()
