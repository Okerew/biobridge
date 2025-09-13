from biobridge.definitions.mycelium import Mushroom, Hypha

# Create a mushroom
amanita = Mushroom("Amanita muscaria", "Amanita muscaria", cap_diameter=10, stem_height=15, is_edible=False, spore_color="white")

# Produce spores
spores = amanita.produce_spores(100)

# Simulate germination
germinated_hyphae = []
for spore in spores:
    if spore.germinate():
        germinated_hyphae.append(Hypha(f"{spore.name}_hypha"))

# Grow hyphae
for hypha in germinated_hyphae:
    hypha.grow(5.0)
    hypha.branch()

# Connect hyphae to the mushroom
for hypha in germinated_hyphae:
    amanita.connect_hypha(hypha)

# Describe the mushroom
print(amanita.describe())
