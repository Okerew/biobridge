from biobridge.networks.sn import SignalingNetwork

molecules = ["Molecule A", "Molecule B", "Molecule C", "Molecule D"]
interactions = {
    "Molecule A": ["Molecule B", "Molecule C"],
    "Molecule B": ["Molecule D"],
    "Molecule C": ["Molecule D"],
    "Molecule D": []
}

signaling_network = SignalingNetwork(molecules, interactions)
signaling_network.activate_molecules(["Molecule A"])
signaling_network.propagate_signals()
print(signaling_network.to_json())
def doc_string():
    '''
    {
        "molecules": [
            "Molecule C",
            "Molecule B",
            "Molecule A",
            "Molecule D"
        ],
        "interactions": {
            "Molecule A": [
                "Molecule B",
                "Molecule C"
            ],
            "Molecule B": [
                "Molecule D"
            ],
            "Molecule C": [
                "Molecule D"
            ],
            "Molecule D": []
        }
    }
    '''
    pass

signaling_network.from_json(doc_string.__doc__)
signaling_network.visualize_network()
