import matplotlib.pyplot as plt
import networkx as nx
import random
import pickle
import json
import re
import pyrosetta
import tempfile
import py3Dmol
import os
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import webbrowser


class Protein:
    def __init__(self, name, sequence, structure=None, secondary_structure=None, id=None, description=None, annotations=None):
        """
        Initialize a new Protein object.

        :param name: Name of the protein
        :param sequence: Sequence of amino acids (as a string of single-letter codes)
        :param structure: Tertiary structure of the protein (optional)
        :param secondary_structure: Secondary structure of the protein (optional)
        """
        self.name = name
        self.sequence = sequence
        self.structure = structure
        self.secondary_structure = secondary_structure
        self.interactions = []
        self.id = id
        self.description = description
        self.annotations = annotations
        self.bindings = []
        self.mutation_probabilities = {
            'A': 0.1, 'C': 0.2, 'D': 0.3, 'E': 0.4, 'F': 0.5,
            'G': 0.6, 'H': 0.7, 'I': 0.8, 'K': 0.9, 'L': 0.1,
            'M': 0.2, 'N': 0.3, 'P': 0.4, 'Q': 0.5, 'R': 0.6,
            'S': 0.7, 'T': 0.8, 'V': 0.9, 'W': 0.1, 'Y': 0.2
        }
        self.protein_analysis = ProteinAnalysis(self.sequence)

    def add_interaction(self, other_protein, interaction_type, strength):
        """
        Define an interaction between this protein and another protein.

        :param other_protein: The protein this protein interacts with
        :param interaction_type: Type of interaction (e.g., "inhibition", "activation")
        :param strength: Strength of the interaction (e.g., "weak", "moderate", "strong")
        """
        self.interactions.append({
            'protein': other_protein,
            'type': interaction_type,
            'strength': strength
        })

    def remove_interaction(self, other_protein):
        """
        Remove an interaction between this protein and another protein.
        :param other_protein:
        :return:
        """
        self.interactions = [interaction for interaction in self.interactions if interaction['protein'] != other_protein]

    def add_binding(self, binding_site, affinity):
        """
        Define a binding site for the protein.

        :param binding_site: Location or description of the binding site
        :param affinity: Binding affinity (can be a number or description)
        """
        self.bindings.append({
            'site': binding_site,
            'affinity': affinity
        })

    def absolute_mutate(self, position, new_amino_acid, probability):
        """
        Mutate the sequence of the protein at a specific position with an absolute probability.
        :param position:
        :param new_amino_acid:
        :param probability:
        :return:
        """
        if random.random() < probability:
            self.sequence = (self.sequence[:position - 1] + new_amino_acid +
                             self.sequence[position:])
            return True

    def mutate_sequence(self, position, new_amino_acid):
        """
        Mutate the sequence of the protein at a specific position with a probability based on the current amino acid.

        :param position: Position in the sequence to mutate (1-based index)
        :param new_amino_acid: The new amino acid to replace the old one (single-letter code)
        """
        if 1 <= position <= len(self.sequence):
            current_amino_acid = self.sequence[position - 1]
            probability = self.mutation_probabilities.get(current_amino_acid, 0.5)  # Default to 0.5 if not found
            print("Probability:", probability)
            if random.random() < probability:
                self.sequence = (self.sequence[:position - 1] + new_amino_acid +
                                 self.sequence[position:])
                return True
            else:
                return False
        else:
            raise ValueError("Position out of range")

    def random_absolute_mutate(self, probability):
        """
        Randomly mutate the sequence of the protein with an absolute probability.
        """
        amino_acids = "ACDEFGHIKLMNPQRSTVWY"  # All possible amino acids
        for i in range(len(self.sequence)):
            if random.random() < probability:
                new_amino_acid = random.choice(amino_acids)
                self.mutate_sequence(i + 1, new_amino_acid)

    def random_mutate(self):
        """
        Randomly mutate the sequence of the protein with probabilities based on the current amino acids.
        """
        amino_acids = "ACDEFGHIKLMNPQRSTVWY"  # All possible amino acids
        for i in range(len(self.sequence)):
            current_amino_acid = self.sequence[i]
            probability = self.mutation_probabilities.get(current_amino_acid, 0.5)  # Default to 0.5 if not found
            print("Probability:", probability)
            if random.random() < probability:
                new_amino_acid = random.choice(amino_acids)
                self.mutate_sequence(i + 1, new_amino_acid)

    def calculate_properties(self):
        """
        Calculate and return basic properties of the protein, such as length and molecular weight.

        :return: A dictionary with properties like length and molecular weight.
        """
        length = len(self.sequence)
        molecular_weight = self.protein_analysis.molecular_weight()
        isoelectric_point = self.protein_analysis.isoelectric_point()
        aromaticity = self.protein_analysis.aromaticity()
        instability_index = self.protein_analysis.instability_index()
        gravy = self.protein_analysis.gravy()

        return {
            'length': length,
            'molecular_weight': molecular_weight,
            'isoelectric_point': isoelectric_point,
            'aromaticity': aromaticity,
            'instability_index': instability_index,
            'gravy': gravy
        }

    def simulate_interactions(self):
        """
        Simulate and visualize interactions between this protein and others using a graph.

        This method uses the networkx and matplotlib libraries to create a visual representation
        of the interactions.
        """
        G = nx.DiGraph()

        G.add_node(self.name, color='blue')

        for interaction in self.interactions:
            other_protein = interaction['protein'].name
            interaction_type = interaction['type']
            strength = interaction['strength']

            G.add_node(other_protein, color='red')
            G.add_edge(self.name, other_protein, label=f"{interaction_type} ({strength})")

        pos = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'label')
        node_colors = [G.nodes[n]['color'] for n in G.nodes()]

        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=10, font_color='white')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='green')
        plt.show()

    def interact_with_cell(self, cell):
        """
        Simulate the interaction between this protein and a cell.

        :param cell: The cell with which the protein interacts
        :return: A string describing the interaction result
        """
        interaction_result = [f"{self.name} interacts with {cell.name}."]

        # Check for receptor binding
        bound_receptors = [receptor for receptor in cell.receptors if
                           any(binding['site'] == receptor.name for binding in self.bindings)]
        if bound_receptors:
            interaction_result.append(f"Binding occurs at receptors: {', '.join([r.name for r in bound_receptors])}.")
        else:
            interaction_result.append("No specific receptor binding detected.")

        # Check for surface protein interaction
        interacting_surface_proteins = [sp for sp in cell.surface_proteins if self.sequence in sp.sequence]
        if interacting_surface_proteins:
            interaction_result.append(
                f"Interaction occurs with surface proteins: {', '.join([sp.name for sp in interacting_surface_proteins])}.")
        else:
            interaction_result.append("No specific surface protein interaction detected.")

        return " ".join(interaction_result)

    def describe_interactions(self):
        """
        Print details of the protein's interactions.
        """
        for i, interaction in enumerate(self.interactions, 1):
            print(f"Interaction {i}:")
            print(f"  Protein: {interaction['protein'].name}")
            print(f"  Type: {interaction['type']}")
            print(f"  Strength: {interaction['strength']}\n")

    def describe_bindings(self):
        """
        Print details of the protein's binding sites.
        """
        for i, binding in enumerate(self.bindings, 1):
            print(f"Binding {i}:")
            print(f"  Site: {binding['site']}")
            print(f"  Affinity: {binding['affinity']}\n")

    def activeness(self):
        """
        Determine the activeness of the protein based on its interactions, bindings, and mutations.

        :return: A float representing the activeness score of the protein.
        """
        # Base activeness starts at 1.0 (neutral)
        activeness_score = 1.0

        # Evaluate bindings: Higher affinity increases activeness
        for binding in self.bindings:
            if isinstance(binding['affinity'], (int, float)):
                activeness_score += binding['affinity'] * 0.1
            elif isinstance(binding['affinity'], str):
                if binding['affinity'].lower() == "high":
                    activeness_score += 0.5
                elif binding['affinity'].lower() == "medium":
                    activeness_score += 0.3
                elif binding['affinity'].lower() == "low":
                    activeness_score += 0.1

        # Evaluate interactions: Activation increases, inhibition decreases activeness
        for interaction in self.interactions:
            if interaction['type'].lower() == "activation":
                if interaction['strength'].lower() == "strong":
                    activeness_score += 0.5
                elif interaction['strength'].lower() == "moderate":
                    activeness_score += 0.3
                elif interaction['strength'].lower() == "weak":
                    activeness_score += 0.1
            elif interaction['type'].lower() == "inhibition":
                if interaction['strength'].lower() == "strong":
                    activeness_score -= 0.5
                elif interaction['strength'].lower() == "moderate":
                    activeness_score -= 0.3
                elif interaction['strength'].lower() == "weak":
                    activeness_score -= 0.1

        # Ensure the activeness score remains within a reasonable range
        activeness_score = max(0.0, activeness_score)  # Minimum activeness is 0.0
        activeness_score = min(10.0, activeness_score)  # Cap the activeness at 10.0

        return activeness_score

    def update_binding(self, binding_site, affinity=None):
        """
        Update an existing binding with a new affinity.
        """
        for binding in self.bindings:
            if binding['site'] == binding_site:
                if affinity is not None:
                    binding['affinity'] = affinity
                return
        print("Binding site not found.")

    def remove_binding(self, binding_site):
        """
        Remove a binding site.
        """
        self.bindings = [binding for binding in self.bindings if binding['site'] != binding_site]

    def update_interaction(self, other_protein, interaction_type=None, strength=None):
        """
        Update an existing interaction with a new type or strength.
        """
        for interaction in self.interactions:
            if interaction['protein'] == other_protein:
                if interaction_type is not None:
                    interaction['type'] = interaction_type
                if strength is not None:
                    interaction['strength'] = strength
                return
        print("Interaction not found.")

    def save_protein(self, file_path):
        with open(file_path, 'wb') as f:
            print(f"Protein saved to {file_path}")
            pickle.dump(self, f)

    @staticmethod
    def load_protein(file_path) -> 'Protein':
        with open(file_path, 'rb') as f:
            print(f"Protein loaded from {file_path}")
            return pickle.load(f)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'active': self.activeness()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Protein':
        protein = cls(data['name'], data['sequence'])
        protein.active = data['active']
        return protein

    def pose_to_pdb_string(self, pose):
        """
        Convert a PyRosetta Pose object to a PDB string.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdb') as temp_pdb_file:
            temp_pdb_path = temp_pdb_file.name
            pose.dump_pdb(temp_pdb_path)
            with open(temp_pdb_path, 'r') as pdb_file:
                pdb_string = pdb_file.read()
            return pdb_string

    def to_json(self) -> str:
        """
        Convert the protein to a JSON string representation.

        :return: JSON string representing the protein
        """
        protein_dict = {
            'name': self.name,
            'sequence': self.sequence,
            'secondary_structure': self.secondary_structure,
            'interactions': [
                {
                    'protein': interaction['protein'].name,
                    'type': interaction['type'],
                    'strength': interaction['strength']
                } for interaction in self.interactions
            ],
            'bindings': self.bindings,
            'active': self.activeness()
        }

        # Convert the Pose object to a PDB string if it exists
        if self.structure is not None and isinstance(self.structure, pyrosetta.rosetta.core.pose.Pose):
            protein_dict['structure'] = self.pose_to_pdb_string(self.structure)
        else:
            protein_dict['structure'] = self.structure

        return json.dumps(protein_dict, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Protein':
        """
        Create a Protein instance from a JSON string.

        :param json_str: JSON string representing the protein
        :return: An instance of Protein
        """
        protein_dict = json.loads(json_str)
        protein = cls(
            name=protein_dict['name'],
            sequence=protein_dict['sequence'],
            structure=protein_dict['structure'],
            secondary_structure=protein_dict['secondary_structure']
        )
        protein.bindings = protein_dict['bindings']
        protein.active = protein_dict['active']

        protein._interaction_data = protein_dict['interactions']

        return protein

    def recreate_interactions(self, protein_dict):
        """
        Recreate protein interactions after loading from JSON.

        :param protein_dict: Dictionary of all proteins in the network, keyed by name
        """
        for interaction_data in self._interaction_data:
            other_protein = protein_dict.get(interaction_data['protein'])
            if other_protein:
                self.add_interaction(other_protein, interaction_data['type'], interaction_data['strength'])
        del self._interaction_data  # Remove the temporary interaction data

    def search_motif(self, motif):
        """
        Search for a specific motif in the protein sequence.

        :param motif: A string representing the motif to search for.
                      Can include regular expression patterns.
        :return: A list of tuples, each containing the start position
                 and the matched sequence of the motif found.
        """
        matches = []
        for match in re.finditer(motif, self.sequence):
            matches.append((match.start() + 1, match.group()))  # +1 for 1-based indexing
        return matches

    def predict_structure(self):
        """
        Predict the protein structure using PyRosetta.
        """
        pyrosetta.init()
        pose = pyrosetta.pose_from_sequence(self.sequence)
        self.structure = pose
        return pose

    def display_3d_structure(self):
        """
        Display the protein structure in a 3D figure using py3Dmol in a web browser.
        """
        if self.structure is None:
            print("No structure available to display.")
            return

        # Convert the structure to a PDB string
        pdb_string = self.pose_to_pdb_string(self.structure)

        # Create a py3Dmol viewer
        viewer = py3Dmol.view(width=800, height=600)
        viewer.addModel(pdb_string, 'pdb')
        viewer.setStyle({'cartoon': {'color': 'spectrum'}})

        # Highlight bindings if available
        for binding in self.bindings:
            viewer.addSurface(py3Dmol.VDW, {'opacity': 0.6, 'atoms': {'resi': binding['site']}})

        # Zoom to fit the structure
        viewer.zoomTo()

        # Generate the HTML content
        html_content = f"""
        <html>
        <head>
            <script src="https://3dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
        </head>
        <body>
            <div id="container" style="width: 800px; height: 600px; position: relative;"></div>
            <script>
                let viewer = $3Dmol.createViewer(document.getElementById("container"));
                viewer.addModel(`{pdb_string}`, "pdb");
                viewer.setStyle({{'cartoon': {{'color': 'spectrum'}}}});

                {' '.join([f"viewer.addSurface($3Dmol.VDW, {{opacity: 0.6, atoms: {{resi: '{binding['site']}'}}}});" for binding in self.bindings])}

                viewer.zoomTo();
                viewer.render();
            </script>
        </body>
        </html>
        """

        # Create a temporary HTML file to display the 3D viewer
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name

        # Open the temporary HTML file in the default web browser
        webbrowser.open('file://' + temp_path)

        print(f"3D structure opened in your default web browser. Close the browser tab when done.")
        input("Press Enter to close the temporary file and exit...")

        # Clean up the temporary file
        os.unlink(temp_path)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __eq__(self, other):
        if isinstance(other, Protein):
            return self.sequence == other.sequence
        return False

    def __getstate__(self):
        return {
            'name': self.name,
            'sequence': self.sequence,
            'structure': self.structure,
            'secondary_structure': self.secondary_structure,
            'interactions': self.interactions,
            'bindings': self.bindings,
            'id': self.id,
            'description': self.description,
            'active': self.activeness(),
            'annotation': self.annotation
        }

    def __setstate__(self, state):
        self.name = state['name']
        self.sequence = state['sequence']
        self.structure = state['structure']
        self.secondary_structure = state['secondary_structure']
        self.interactions = state['interactions']
        self.bindings = state['bindings']
        self.id = state['id']
        self.description = state['description']
        self.active = state['active']
        self.annotation = state['annotation']

    def __str__(self):
        """
        Return a string representation of the protein.
        """
        properties = self.calculate_properties()
        return (f"Protein: {self.name}\n"
                f"Sequence: {self.sequence}\n"
                f"Structure: {self.structure or 'Not defined'}\n"
                f"Secondary Structure: {self.secondary_structure or 'Not defined'}\n"
                f"Interactions: {len(self.interactions)}\n"
                f"Bindings: {len(self.bindings)}\n"
                f"Molecular Weight: {properties['molecular_weight']:.2f} Da\n"
                f"Isoelectric Point: {properties['isoelectric_point']:.2f}\n"
                f"Aromaticity: {properties['aromaticity']:.2f}\n"
                f"Instability Index: {properties['instability_index']:.2f}\n"
                f"GRAVY: {properties['gravy']:.2f}")

    def get_id(self):
        return self.id
