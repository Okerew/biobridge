import json
from typing import Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx


class MetabolicNetwork:
    def __init__(
        self,
        metabolites: List[str],
        enzymes: List[str],
        reactions: List[Tuple[str, str, str]],
    ):
        self.metabolites = set(metabolites)
        self.enzymes = set(enzymes)
        self.reactions = list(reactions)
        self.graph = nx.DiGraph()
        self.vertex_map = {}
        self.build_graph()

    def build_graph(self):
        # Adding metabolites and enzymes as nodes
        for metabolite in self.metabolites:
            self.add_vertex(metabolite, "metabolite")
        for enzyme in self.enzymes:
            self.add_vertex(enzyme, "enzyme")

        # Adding reactions as edges
        for enzyme, substrate, product in self.reactions:
            if (
                substrate in self.vertex_map
                and enzyme in self.vertex_map
                and product in self.vertex_map
            ):
                self.graph.add_edge(self.vertex_map[substrate], self.vertex_map[enzyme])
                self.graph.add_edge(self.vertex_map[enzyme], self.vertex_map[product])

    def add_vertex(self, name: str, node_type: str):
        self.graph.add_node(name, node_type=node_type)
        self.vertex_map[name] = name
        if node_type == "metabolite":
            self.metabolites.add(name)
        elif node_type == "enzyme":
            self.enzymes.add(name)

    def add_reaction(self, enzyme: str, substrate: str, product: str):
        self.reactions.append((enzyme, substrate, product))
        self.enzymes.add(enzyme)
        self.metabolites.add(substrate)
        self.metabolites.add(product)

        if substrate not in self.vertex_map:
            self.add_vertex(substrate, "metabolite")
        if enzyme not in self.vertex_map:
            self.add_vertex(enzyme, "enzyme")
        if product not in self.vertex_map:
            self.add_vertex(product, "metabolite")

        self.graph.add_edge(self.vertex_map[substrate], self.vertex_map[enzyme])
        self.graph.add_edge(self.vertex_map[enzyme], self.vertex_map[product])

    def remove_reaction(self, enzyme: str, substrate: str, product: str):
        reaction = (enzyme, substrate, product)
        if reaction in self.reactions:
            self.reactions.remove(reaction)
            self.graph.remove_edge(self.vertex_map[substrate], self.vertex_map[enzyme])
            self.graph.remove_edge(self.vertex_map[enzyme], self.vertex_map[product])

            # Remove isolated vertices
            isolated_vertices = [
                v for v in self.graph.nodes() if self.graph.degree(v) == 0
            ]
            for v in isolated_vertices:
                self.graph.remove_node(v)
                if v in self.metabolites:
                    self.metabolites.remove(v)
                if v in self.enzymes:
                    self.enzymes.remove(v)
                del self.vertex_map[v]

    def get_connected_components(self) -> List[Set[str]]:
        # Convert directed graph to undirected to get connected components
        undirected_graph = self.graph.to_undirected()
        components = list(nx.connected_components(undirected_graph))
        return [set(comp) for comp in components]

    def get_metabolite_degrees(self) -> Dict[str, Dict[str, int]]:
        degrees = {}
        for metabolite in self.metabolites:
            if metabolite in self.graph.nodes():
                in_degree = self.graph.in_degree(metabolite)
                out_degree = self.graph.out_degree(metabolite)
                degrees[metabolite] = {"in_degree": in_degree, "out_degree": out_degree}
        return degrees

    def to_json(self) -> str:
        data = {
            "metabolites": list(self.metabolites),
            "enzymes": list(self.enzymes),
            "reactions": self.reactions,
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def from_json(json_str: str) -> "MetabolicNetwork":
        data = json.loads(json_str)
        return MetabolicNetwork(
            metabolites=data["metabolites"],
            enzymes=data["enzymes"],
            reactions=data["reactions"],
        )

    def predict_outputs(self, input_metabolites: Set[str], steps: int) -> Set[str]:
        unknown_metabolites = input_metabolites - self.metabolites
        if unknown_metabolites:
            raise ValueError(f"Unknown metabolites: {', '.join(unknown_metabolites)}")

        current_metabolites = input_metabolites.copy()
        for _ in range(steps):
            new_metabolites = set()
            for metabolite in current_metabolites:
                for enzyme, substrate, product in self.reactions:
                    if metabolite == substrate:
                        new_metabolites.add(product)
            current_metabolites.update(new_metabolites)
        return current_metabolites

    def get_possible_pathways(
        self, start_metabolite: str, end_metabolite: str, max_steps: int
    ) -> List[List[str]]:
        if start_metabolite not in self.metabolites:
            raise ValueError(
                f"Start metabolite '{start_metabolite}' not found in the network"
            )
        if end_metabolite not in self.metabolites:
            raise ValueError(
                f"End metabolite '{end_metabolite}' not found in the network"
            )

        paths = []
        visited = set()
        current_path = []

        def dfs(current: str, depth: int):
            if depth > max_steps:
                return
            if current == end_metabolite:
                paths.append(current_path.copy())
                return
            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    current_path.append(neighbor)
                    dfs(neighbor, depth + 1)
                    current_path.pop()
                    visited.remove(neighbor)

        visited.add(start_metabolite)
        current_path.append(start_metabolite)
        dfs(start_metabolite, 0)
        return paths

    def reset(self):
        self.metabolites.clear()
        self.enzymes.clear()
        self.reactions.clear()
        self.graph.clear()
        self.vertex_map.clear()

    def visualize_network(self, save_path: Optional[str] = None):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)

        # Draw metabolites
        metabolite_nodes = [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["node_type"] == "metabolite"
        ]
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=metabolite_nodes,
            node_color="lightblue",
            node_size=500,
            alpha=0.8,
        )

        # Draw enzymes
        enzyme_nodes = [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["node_type"] == "enzyme"
        ]
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=enzyme_nodes,
            node_color="lightgreen",
            node_size=500,
            node_shape="s",
            alpha=0.8,
        )

        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, edge_color="gray", arrows=True)

        # Add labels
        nx.draw_networkx_labels(self.graph, pos, font_size=10)

        plt.title("Metabolic Network")
        plt.axis("off")

        if save_path:
            plt.savefig(save_path, format="png", dpi=300, bbox_inches="tight")
            print(f"Network visualization saved to {save_path}")
        else:
            plt.show()
