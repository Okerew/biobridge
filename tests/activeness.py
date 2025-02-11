from biobridge.blocks.protein import Protein


def test_dynamic_activeness():
    # Create Protein instance
    protein = Protein(name="DynamicProtein", sequence="XYZ")

    # Add initial interactions and bindings
    protein.add_interaction(protein, "activation", "strong")
    protein.add_binding("SiteA", "medium")

    print(f"Initial activeness: {protein.activeness()}")

    # Update interaction and binding
    protein.update_interaction(protein, interaction_type="inhibition", strength="weak")
    protein.update_binding("SiteA", affinity="high")

    print(f"Updated activeness: {protein.activeness()}")

    # Remove interaction and binding
    protein.remove_interaction(protein)
    protein.remove_binding("SiteA")

    print(f"Activeness after removal: {protein.activeness()}")


# Run the dynamic activeness test
test_dynamic_activeness()
