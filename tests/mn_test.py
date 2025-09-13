from biobridge.metabolic_network import MetabolicNetwork

metabolites = ["Metabolite A", "Metabolite B", "Metabolite C"]
enzymes = ["Enzyme 1", "Enzyme 2"]
reactions = [("Enzyme 1", "Metabolite A", "Metabolite B"), ("Enzyme 2", "Metabolite B", "Metabolite C")]

metabolic_network = MetabolicNetwork(metabolites, enzymes, reactions)
metabolic_network.visualize_network("")
print(metabolic_network.to_json())

# Create a MetabolicNetwork instance
network = MetabolicNetwork(metabolites, enzymes, reactions)

# Predict outputs
input_metabolites = {"Metabolite A", "Metabolite C"}
steps = 3
outputs = network.predict_outputs(input_metabolites, steps)
print(f"Predicted outputs after {steps} steps: {outputs}")

# Find possible pathways
start = "Metabolite A"
end = "Metabolite C"
max_steps = 5
pathways = network.get_possible_pathways(start, end, max_steps)
print(f"Possible pathways from {start} to {end}:")
for path in pathways:
    print(" -> ".join(path))

def docstring():
    '''{
      "metabolites": [
        "Metabolite A",
        "Metabolite C",
        "Metabolite B"
      ],
      "enzymes": [
        "Enzyme 2",
        "Enzyme 1"
      ],
      "reactions": [
        [
          "Enzyme 1",
          "Metabolite A",
          "Metabolite B"
        ],
        [
          "Enzyme 2",
          "Metabolite B",
          "Metabolite C"
        ]
      ]
    }
    '''
    pass

metabolic_network.reset()
metabolic_network.from_json(docstring.__doc__)