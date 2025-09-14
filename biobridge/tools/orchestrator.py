from typing import List, Set, Optional
import json
import pickle
from biobridge.blocks.tissue import Tissue
from biobridge.networks.mn import MetabolicNetwork
from biobridge.networks.grn import GeneRegulatoryNetwork
from biobridge.networks.sn import SignalingNetwork


class Orchestrator:
    def __init__(self, tissues: Optional[List[Tissue]] = None,
                 gene_networks: Optional[List[GeneRegulatoryNetwork]] = None,
                 metabolic_networks: Optional[List[MetabolicNetwork]] = None,
                 signaling_networks: Optional[List[SignalingNetwork]] = None):
        """
        Initialize the Orchestrator with various tissues and networks.

        :param tissues: List of Tissue objects
        :param gene_networks: List of GeneRegulatoryNetwork objects
        :param metabolic_networks: List of MetabolicNetwork objects
        :param signaling_networks: List of SignalingNetwork objects
        """
        self.tissues = tissues
        self.gene_networks = gene_networks
        self.metabolic_networks = metabolic_networks
        self.signaling_networks = signaling_networks

    def add_tissue(self, tissue: Tissue) -> None:
        """Add a tissue to the orchestrator."""
        self.tissues.append(tissue)

    def add_gene_network(self, gene_network: GeneRegulatoryNetwork) -> None:
        """Add a gene regulatory network to the orchestrator."""
        self.gene_networks.append(gene_network)

    def add_metabolic_network(self, metabolic_network: MetabolicNetwork) -> None:
        """Add a metabolic network to the orchestrator."""
        self.metabolic_networks.append(metabolic_network)

    def add_signaling_network(self, signaling_network: SignalingNetwork) -> None:
        """Add a signaling network to the orchestrator."""
        self.signaling_networks.append(signaling_network)

    def simulate_tissues(self, external_factors: List[tuple] = None) -> None:
        """
        Simulate one time step in all tissues' life, including growth, healing, and external factors.

        :param external_factors: List of tuples (factor, intensity) to apply to all tissues
        """
        for tissue in self.tissues:
            tissue.simulate_time_step(external_factors)

    def simulate_gene_networks(self, inputs: List[str]) -> None:
        """
        Simulate all gene regulatory networks with given inputs.

        :param inputs: List of input signals for the gene networks
        """
        for gene_network in self.gene_networks:
            gene_network.predict_output(inputs)

    def simulate_metabolic_networks(self, input_metabolites: Set[str], steps: int) -> None:
        """
        Simulate all metabolic networks with given input metabolites.

        :param input_metabolites: Set of initial input metabolites
        :param steps: Number of reaction steps to simulate
        """
        for metabolic_network in self.metabolic_networks:
            metabolic_network.predict_outputs(input_metabolites, steps)

    def simulate_signaling_networks(self, molecule_list: List[str], steps: int) -> None:
        """
        Simulate all signaling networks with given activated molecules.

        :param molecule_list: List of molecule names to activate
        :param steps: Number of propagation steps
        """
        for signaling_network in self.signaling_networks:
            signaling_network.activate_molecules(molecule_list)
            signaling_network.propagate_signals(steps)

    def visualize_gene_networks(self) -> None:
        """Visualize all gene regulatory networks."""
        for gene_network in self.gene_networks:
            gene_network.visualize_network(gene_network.regulate_genes())

    def visualize_metabolic_networks(self) -> None:
        """Visualize all metabolic networks."""
        for metabolic_network in self.metabolic_networks:
            metabolic_network.visualize_network("")

    def visualize_signaling_networks(self) -> None:
        """Visualize all signaling networks."""
        for signaling_network in self.signaling_networks:
            signaling_network.visualize_network()

    def save_state(self, file_path: str) -> None:
        """
        Save the current state of the orchestrator to a file.

        :param file_path: Path where the state should be saved
        """
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)
        print(f"Orchestrator state saved to {file_path}")

    @staticmethod
    def load_state(file_path: str) -> 'Orchestrator':
        """
        Load the orchestrator state from a file.

        :param file_path: Path from where the state should be loaded
        :return: An instance of Orchestrator
        """
        with open(file_path, 'rb') as f:
            orchestrator = pickle.load(f)
        print(f"Orchestrator state loaded from {file_path}")
        return orchestrator

    def to_json(self) -> str:
        """
        Convert the orchestrator to a JSON string representation.

        :return: JSON string representing the orchestrator
        """
        orchestrator_dict = {
            'tissues': [tissue.to_json() for tissue in self.tissues],
            'gene_networks': [gene_network.to_json() for gene_network in self.gene_networks],
            'metabolic_networks': [metabolic_network.to_json() for metabolic_network in self.metabolic_networks],
            'signaling_networks': [signaling_network.to_json() for signaling_network in self.signaling_networks]
        }
        return json.dumps(orchestrator_dict, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Orchestrator':
        """
        Create an Orchestrator instance from a JSON string.

        :param json_str: JSON string representing the orchestrator
        :return: An instance of Orchestrator
        """
        orchestrator_dict = json.loads(json_str)

        tissues = [Tissue.from_json(tissue_json) for tissue_json in orchestrator_dict['tissues']]
        gene_networks = [GeneRegulatoryNetwork.from_json(gene_network_json) for gene_network_json in orchestrator_dict['gene_networks']]
        metabolic_networks = [MetabolicNetwork.from_json(metabolic_network_json) for metabolic_network_json in orchestrator_dict['metabolic_networks']]
        signaling_networks = [SignalingNetwork.from_json(signaling_network_json) for signaling_network_json in orchestrator_dict['signaling_networks']]

        return cls(
            tissues=tissues,
            gene_networks=gene_networks,
            metabolic_networks=metabolic_networks,
            signaling_networks=signaling_networks
        )

    def simulate_network_evolution(self, num_steps: int) -> None:
        """
        Simulate the evolution of all networks over a given number of time steps.

        :param num_steps: Number of time steps to simulate
        """
        for _ in range(num_steps):
            self.simulate_tissues()
            self.simulate_gene_networks(["input_signal_1", "input_signal_2"])
            self.simulate_metabolic_networks({"glucose", "oxygen"}, 10)
            self.simulate_signaling_networks(["molecule_1", "molecule_2"], 5)

    def reset(self) -> None:
        """Reset all tissues and networks to their initial states."""
        for tissue in self.tissues:
            tissue.cells = []
        for gene_network in self.gene_networks:
            gene_network.reset_network()
        for metabolic_network in self.metabolic_networks:
            metabolic_network.reset()
        for signaling_network in self.signaling_networks:
            signaling_network.reset()
