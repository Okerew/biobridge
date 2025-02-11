from typing import List, Dict, Set
import pandas as pd
from biobridge.blocks.protein import Protein, nx, plt, pickle, json
from biobridge.genes.dna import DNA


class GeneRegulatoryNetwork:
    def __init__(self, receptors: List[Protein], proteins: List[Protein], dna: DNA, interactions: Dict[str, List[str]], binding_sites):
        """
        Initialize the Gene Regulatory Network.

        :param receptors: List of receptor proteins that receive inputs
        :param proteins: List of proteins involved in the network
        :param dna: DNA object representing the cell's DNA
        :param interactions: Dictionary defining interactions between proteins (e.g., {"Protein A": ["Protein B"]})
        :param binding_sites: Dictionary defining binding sites for each protein (e.g., {"Protein A": "ACGT"})
        """
        self.receptors = {r.name: r for r in receptors}
        self.proteins = {p.name: p for p in proteins}
        self.dna = dna
        self.interactions = interactions
        self.binding_sites = binding_sites
        self.active_proteins: Set[str] = set()
        self.regulated_genes: List[str] = []

    def process_inputs(self, inputs: List[str]) -> None:
        for input_signal in inputs:
            for receptor_name, receptor in self.receptors.items():
                if receptor_name in input_signal:
                    receptor.active = True
                    self.active_proteins.add(receptor_name)
                    print(f"{receptor_name} activated by input {input_signal}.")

    def simulate_network(self, steps: int = 10) -> None:
        for step in range(steps):
            new_activations = set()
            for protein_name in self.active_proteins:
                if protein_name in self.interactions:
                    for target_protein in self.interactions[protein_name]:
                        if target_protein not in self.active_proteins:
                            new_activations.add(target_protein)
                            print(f"Step {step + 1}: {protein_name} activates {target_protein}.")

            if not new_activations:
                break

            self.active_proteins.update(new_activations)

    def regulate_genes(self):
        """
        Simulate the regulation of genes based on the active proteins and their binding sites.
        """
        regulated_genes = []
        for gene_name, start, end in self.dna.genes:
            gene_sequence = self.dna.sequence[start:end]
            for protein_name in self.active_proteins:
                if protein_name in self.binding_sites:
                    binding_site = self.binding_sites[protein_name]
                    if binding_site in gene_sequence:
                        regulated_genes.append(gene_name)
                        print(f"Gene {gene_name} regulated by {protein_name} (binding site: {binding_site}).")
        self.regulated_genes = regulated_genes
        return regulated_genes

    def visualize_network(self, regulated_genes):
        """
        Visualize the gene regulatory network and highlight the regulated genes and DNA.

        :param regulated_genes: List of genes that were regulated in the simulation
        """
        G = nx.DiGraph()

        # Add protein interactions to the graph
        for protein_name in self.interactions:
            for target_protein in self.interactions[protein_name]:
                G.add_edge(protein_name, target_protein)

        # Add DNA and gene nodes to the graph
        G.add_node("DNA", color='green', shape='rectangle')
        for gene_name in self.dna.genes:
            G.add_edge("DNA", gene_name[0], color='green')
            if gene_name[0] in regulated_genes:
                G.add_edge(gene_name[0], "Regulated by proteins")

        # Adjust positions to minimize overlap
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)  # `k` controls the distance between nodes
        colors = [G[u][v].get('color', 'black') for u, v in G.edges()]
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', font_weight='bold', edge_color=colors)

        # Highlight regulated genes in red
        regulated_nodes = [gene for gene in regulated_genes if gene in G.nodes]
        nx.draw_networkx_nodes(G, pos, nodelist=regulated_nodes, node_color='pink')

        # Highlight the DNA node in green
        nx.draw_networkx_nodes(G, pos, nodelist=["DNA"], node_color='lightgreen', node_shape='s')

        plt.title("Gene Regulatory Network with DNA")
        plt.axis('off')
        plt.show()

    def predict_output(self, inputs):
        """
        Predict the output of the gene regulatory network based on given inputs.

        :param inputs: List of input signals
        :return: List of regulated genes
        """
        print("Processing inputs...")
        self.process_inputs(inputs)

        print("Simulating network...")
        self.simulate_network()

        print("Regulating genes...")
        regulated_genes = self.regulate_genes()

        print("Visualizing network...")
        self.visualize_network(regulated_genes)

        return regulated_genes

    def reset_network(self) -> None:
        """Reset the network to its initial state."""
        self.active_proteins.clear()
        self.regulated_genes.clear()
        for protein in self.proteins.values():
            protein.active = False
        for receptor in self.receptors.values():
            receptor.active = False

    def get_network_stats(self) -> Dict[str, int]:
        """Get statistics about the network."""
        return {
            "total_proteins": len(self.proteins),
            "active_proteins": len(self.active_proteins),
            "total_interactions": sum(len(targets) for targets in self.interactions.values()),
            "regulated_genes": len(self.regulated_genes)
        }

    def load_interactions_from_json(self, file_path: str) -> None:
        """
        Load interactions from a JSON file.

        :param file_path: Path to the JSON file
        """
        with open(file_path, 'r') as f:
            self.interactions = json.load(f)

    def load_interactions_from_csv(self, file_path: str) -> None:
        """
        Load interactions from a CSV file.

        :param file_path: Path to the CSV file
        """
        df = pd.read_csv(file_path)
        self.interactions = df.set_index('Protein').T.to_dict('list')

    def save_network(self, file_path: str) -> None:
        """
        Save the current state of the gene regulatory network to a file.

        :param file_path: Path where the network should be saved
        """
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)
        print(f"Network saved to {file_path}")

    @staticmethod
    def load_network(file_path: str) -> 'GeneRegulatoryNetwork':
        """
        Load a gene regulatory network from a file.

        :param file_path: Path from where the network should be loaded
        :return: An instance of GeneRegulatoryNetwork
        """
        with open(file_path, 'rb') as f:
            network = pickle.load(f)
        print(f"Network loaded from {file_path}")
        return network

    def to_json(self) -> str:
        """
        Convert the network to a JSON string representation.

        :return: JSON string representing the network
        """
        network_dict = {
            'receptors': [r.to_dict() for r in self.receptors.values()],
            'proteins': [p.to_dict() for p in self.proteins.values()],
            'dna': self.dna.to_dict(),
            'interactions': self.interactions,
            'binding_sites': self.binding_sites,
            'active_proteins': list(self.active_proteins),
            'regulated_genes': self.regulated_genes
        }
        return json.dumps(network_dict, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'GeneRegulatoryNetwork':
        """
        Create a GeneRegulatoryNetwork instance from a JSON string.

        :param json_str: JSON string representing the network
        :return: An instance of GeneRegulatoryNetwork
        """
        network_dict = json.loads(json_str)

        receptors = [Protein.from_dict(r) for r in network_dict['receptors']]
        proteins = [Protein.from_dict(p) for p in network_dict['proteins']]
        dna = DNA.from_dict(network_dict['dna'])

        network = cls(
            receptors=receptors,
            proteins=proteins,
            dna=dna,
            interactions=network_dict['interactions'],
            binding_sites=network_dict['binding_sites']
        )

        network.active_proteins = set(network_dict['active_proteins'])
        network.regulated_genes = network_dict['regulated_genes']

        return network
