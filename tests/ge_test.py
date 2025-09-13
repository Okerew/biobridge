from biobridge.tools.ge import GelElectrophoresis

gel = GelElectrophoresis(gel_length=100, voltage=120.0)

# Generate and load random DNA samples
for _ in range(5):
    dna_length = random.randint(50, 1000)
    gel.load_sample(generate_random_dna(dna_length))

# Run the electrophoresis
results = gel.run_electrophoresis(duration=60)

# Visualize the results
gel.visualize_results(results)