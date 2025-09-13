from biobridge.blocks.protein import Protein


class Hemoglobin(Protein):
    """
    Represents the Hemoglobin protein, which carries oxygen in red blood cells.
    Inherits from the Protein class and adds specific functionality for oxygen binding.
    """
    def __init__(self, sequence='VHLTPEEK', structure=None, secondary_structure=None, id=None, description=None, annotations=None):
        super().__init__('Hemoglobin', sequence, structure, secondary_structure, id, description, annotations)
        self.oxygen_binding_sites = []  # Store information about oxygen binding
        self.oxygen_capacity = 4  # Hemoglobin can bind up to 4 oxygen molecules
    
    def bind_oxygen(self, oxygen_molecules):
        """
        Binds oxygen molecules to the hemoglobin protein.
        
        :param oxygen_molecules: Number of oxygen molecules to bind.
        """
        if len(self.oxygen_binding_sites) + oxygen_molecules > self.oxygen_capacity:
            raise ValueError("Exceeds oxygen binding capacity of hemoglobin.")
        
        self.oxygen_binding_sites.extend(['O2'] * oxygen_molecules)
        return f"Bound {oxygen_molecules} oxygen molecules."

    def release_oxygen(self):
        """
        Releases all bound oxygen molecules.
        """
        released_oxygen = len(self.oxygen_binding_sites)
        self.oxygen_binding_sites.clear()
        return f"Released {released_oxygen} oxygen molecules."
    
    def oxygen_saturation(self):
        """
        Calculates the oxygen saturation level of the hemoglobin.
        
        :return: Percentage of oxygen saturation (0 to 100%)
        """
        return (len(self.oxygen_binding_sites) / self.oxygen_capacity) * 100
    
    def __str__(self):
        """
        Return a string representation of the Hemoglobin.
        """
        return (super().__str__() +
                f"\nOxygen Binding Sites: {len(self.oxygen_binding_sites)} / {self.oxygen_capacity} bound")
                