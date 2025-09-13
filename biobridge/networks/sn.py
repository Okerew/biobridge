import json
from typing import Dict, List, Set

import matplotlib.pyplot as plt
import networkx as nx


class SignalingNetwork:
    def __init__(self, molecules: List[str], interactions: Dict[str, List[str]]):
        self.molecules: Set[str] = set(molecules)
        self.interactions: Dict[str, List[str]] = interactions
        self.active_molecules: Set[str] = set()

    def activate_molecules(self, molecule_list: List[str]) -> None:
        for molecule in molecule_list:
            if molecule in self.molecules:
                self.active_molecules.add(molecule)
                print(f"Molecule {molecule} activated.")
            else:
                print(f"Molecule {molecule} is not in the network.")

    def propagate_signals(self, steps: int = 10) -> None:
        for step in range(steps):
            new_activations: Set[str] = set()
            for molecule in self.active_molecules:
                if molecule in self.interactions:
                    for target_molecule in self.interactions[molecule]:
                        if target_molecule not in self.active_molecules:
                            new_activations.add(target_molecule)
                            print(
                                f"Step {step + 1}: {molecule} signals {target_molecule}."
                            )
            if not new_activations:
                break
            self.active_molecules.update(new_activations)

    def visualize_network(self) -> None:
        G = nx.DiGraph()
        # Add molecules as nodes
        for molecule in self.molecules:
            G.add_node(molecule)
        # Add interactions as edges
        for molecule, targets in self.interactions.items():
            for target in targets:
                G.add_edge(molecule, target)

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(12, 8))
        node_colors = []
        for molecule in G.nodes():
            if molecule in self.active_molecules:
                node_colors.append("red")
            else:
                node_colors.append("lightblue")

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=node_colors,
            edge_color="gray",
            font_weight="bold",
        )
        plt.title("Signaling Network")
        plt.show()

    def save_network(self, file_path: str) -> None:
        data = {
            "molecules": list(self.molecules),
            "interactions": self.interactions,
            "active_molecules": list(self.active_molecules),
        }
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)
        print(f"Network saved to {file_path}")

    @staticmethod
    def load_network(file_path: str) -> "SignalingNetwork":
        with open(file_path, "r") as file:
            data = json.load(file)
        network = SignalingNetwork(data["molecules"], data["interactions"])
        network.active_molecules = set(data["active_molecules"])
        print(f"Network loaded from {file_path}")
        return network

    def to_json(self) -> str:
        data = {"molecules": list(self.molecules), "interactions": self.interactions}
        return json.dumps(data, indent=2)

    @staticmethod
    def from_json(json_str: str) -> "SignalingNetwork":
        data = json.loads(json_str)
        return SignalingNetwork(data["molecules"], data["interactions"])

    def reset(self) -> None:
        self.active_molecules.clear()
        self.interactions.clear()
