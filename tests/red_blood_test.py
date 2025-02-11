from biobridge.definitions.cells.red_blood_cell import RedBloodCell
from biobridge.definitions.cells.platelet import Platelet

# Create a new Red Blood Cell
rbc = RedBloodCell()

# Check the oxygen saturation (initially 0)
print(rbc.check_oxygen_saturation())  # Output: 0.0

# Bind 3 oxygen molecules to hemoglobin
print(rbc.oxygen_transport(3))  # Output: Bound 3 oxygen molecules.

# Check oxygen saturation (should now be 75%)
print(rbc.check_oxygen_saturation())  # Output: 75.0

# Release all oxygen
print(rbc.release_oxygen())  # Output: Released 3 oxygen molecules.

# Mutate the hemoglobin protein (e.g., sickle cell mutation)
rbc.mutate_hemoglobin(position=6, new_amino_acid='V')

# Display the Red Blood Cell state
print(rbc)

# Create a platelet
platelet = Platelet()

# Attempt to bind red blood cell before activation
platelet.bind_red_blood_cell(rbc)  # Should give a warning

# Activate the platelet
platelet.activate()

# Bind the red blood cell after activation
platelet.bind_red_blood_cell(rbc)

# Form a clot
platelet.form_clot()

# Check the status after clot formation
print(platelet)
