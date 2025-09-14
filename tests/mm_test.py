from biobridge.tools.mm import MolecularMachinery, Cell, Protein

# Create common molecular machines
ribosome = MolecularMachinery.create_ribosome()
atp_synthase = MolecularMachinery.create_atp_synthase()


# Create a custom molecular machine
custom_protein = Protein("Custom Protein", "MGHTUIKLOPQRST")
custom_cell = Cell("Custom Cell", "stem cell")
custom_machine = MolecularMachinery.create_custom("Custom Machine", [custom_protein, custom_cell], "Custom function")
energy_report = MolecularMachinery.energy_consumption_report(custom_machine)
print(energy_report)
# Interact with a protein
protein_to_interact = Protein("Target Protein", "ABCDEFG")
print(ribosome.interact(protein_to_interact))

# Perform function
print(atp_synthase.perform_function())

# Recharge
print(custom_machine.recharge(50))

# Print machine details
print(custom_machine)

a = custom_machine.to_json()
print(a)
b = custom_machine.from_json(a)
