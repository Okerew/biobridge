import random
from biobridge.blocks.protein import Protein

class Hormone:
    def __init__(self, name, structure=None, target_receptor=None):
        """
        Initialize a hormone with specific characteristics.

        :param name: Name of the hormone
        :param structure: Molecular structure of the hormone
        :param target_receptor: The primary receptor the hormone binds to
        """
        self.name = name
        self.structure = structure
        self.target_receptor = target_receptor
        self.concentration = 0.0
        self.half_life = 60  # minutes
        self.signal_cascade = []

    def bind_to_receptor(self, receptor_protein):
        """
        Simulate the hormone binding to a specific receptor protein.

        :param receptor_protein: The Protein object representing the receptor
        :return: Binding result and potential cellular response
        """
        # Add a binding site to the receptor
        receptor_protein.add_binding(self.name, "high")
        
        # Check receptor activation
        receptor_activeness = receptor_protein.activeness()
        
        # Simulate signal transduction
        cellular_response = {
            "receptor_activation": receptor_activeness > 5.0,
            "signal_strength": min(receptor_activeness, 10.0)
        }
        
        return cellular_response

    def trigger_gene_expression(self, dna_object, gene_name):
        """
        Simulate hormone-induced gene expression.

        :param dna_object: The DNA object to potentially activate
        :param gene_name: Name of the gene to potentially activate
        :return: Whether gene expression was triggered
        """
        # Find the target gene
        target_genes = [gene for gene in dna_object.genes if gene.name == gene_name]
        
        if not target_genes:
            print(f"Gene {gene_name} not found in DNA.")
            return False
        
        # Simulate transcription probability based on hormone concentration
        transcription_probability = min(self.concentration / 10.0, 1.0)
        
        if random.random() < transcription_probability:
            # Simulating enhanced transcription
            print(f"Hormone {self.name} triggered expression of {gene_name}")
            return True
        
        return False

    def create_signal_cascade(self, initial_protein):
        """
        Create a signal cascade of protein interactions triggered by the hormone.

        :param initial_protein: The initial protein in the signal cascade
        :return: List of proteins involved in the cascade
        """
        self.signal_cascade = [initial_protein]
        current_protein = initial_protein
        
        # Simulate a cascade of 3-5 protein interactions
        for _ in range(random.randint(3, 5)):
            # Create a new protein to simulate the next interaction
            next_protein = Protein(f"Cascade_Protein_{len(self.signal_cascade)}", "MKVLWAALLVTFLAGCQAKVEQAVETEPEPELRQQTEWQSGQRWELALGRFWDYLRWVQTLSEQVQEELLSSQVTQELRALMDETMKELKAYKSELEEQLTPVAEETRARLSKELQAAQARLGADVLASHGRLVQYRGEVQAMLGQSTEELRVRLASHLRKLRKRLLRDADDLQKRLAVYQAGAREGAERGLSAIRERLGPLVEQGRVRAATVGSLAGQPLQERAQAWGERLRARMEEMGSRTRDRLDEVKEQVAEVRAKLEEQAQQIRLVLASHQARLKSWFEPLVEDMQRQWAGLVEKVQAAVGTSAAPVPSDNH")
            
            # Add an interaction between the current and next protein
            interaction_types = ["activation", "signal_transfer"]
            interaction_strengths = ["weak", "moderate", "strong"]
            
            current_protein.add_interaction(
                next_protein, 
                random.choice(interaction_types), 
                random.choice(interaction_strengths)
            )
            
            self.signal_cascade.append(next_protein)
            current_protein = next_protein
        
        return self.signal_cascade

    def simulate_hormone_action(self, receptor_protein, dna_object, target_gene):
        """
        Simulate the complete hormone action from receptor binding to gene expression.

        :param receptor_protein: The receptor protein
        :param dna_object: The DNA object
        :param target_gene: Name of the target gene
        :return: Dictionary of simulation results
        """
        # Increase concentration
        self.concentration = random.uniform(5.0, 15.0)
        
        # Bind to receptor
        receptor_response = self.bind_to_receptor(receptor_protein)
        
        # Create signal cascade
        signal_cascade = self.create_signal_cascade(receptor_protein)
        
        # Trigger gene expression
        gene_expressed = self.trigger_gene_expression(dna_object, target_gene)
        
        return {
            "hormone_name": self.name,
            "concentration": self.concentration,
            "receptor_activated": receptor_response["receptor_activation"],
            "signal_strength": receptor_response["signal_strength"],
            "signal_cascade_length": len(signal_cascade),
            "gene_expressed": gene_expressed
        }

    def __str__(self):
        """
        String representation of the hormone.
        """
        return (f"Hormone: {self.name}\n"
                f"Target Receptor: {self.target_receptor or 'Not specified'}\n"
                f"Concentration: {self.concentration:.2f}\n"
                f"Half-life: {self.half_life} minutes")