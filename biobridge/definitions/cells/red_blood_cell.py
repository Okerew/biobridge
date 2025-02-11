from biobridge.definitions.proteins.hemoglobin import Hemoglobin
from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell


class RedBloodCell(EukaryoticCell):
    """
    Represents a red blood cell which contains hemoglobin for oxygen transport.
    Inherits from the Cell class and adds specific functionality for oxygen transport.
    """

    def __init__(self, hemoglobin=None, cell_type='Red Blood Cell', health_status=100):
        # Initialize as a Cell and set additional attributes for red blood cells
        super().__init__(name="Red Blood Cell", cell_type=cell_type, health=health_status)
        self.hemoglobin = hemoglobin or Hemoglobin()  # Default to a Hemoglobin instance
        self.receptors = ['O2']  # Red blood cells carry oxygen receptors
        self.lifespan = 120  # Average lifespan of a red blood cell in days
        self.age = 0  # Age of the cell in days
        self.health_status = health_status

    def oxygen_transport(self, oxygen_molecules):
        """
        Facilitates oxygen binding to hemoglobin in the red blood cell.

        :param oxygen_molecules: Number of oxygen molecules available for transport.
        :return: The amount of oxygen molecules successfully bound.
        """
        try:
            bound_oxygen = self.hemoglobin.bind_oxygen(oxygen_molecules)
            self.update_health_status()
            return bound_oxygen
        except ValueError as e:
            print(e)
            return 0

    def release_oxygen(self):
        """
        Simulates the release of oxygen from hemoglobin in the red blood cell.
        """
        released_oxygen = self.hemoglobin.release_oxygen()
        self.update_health_status()
        return released_oxygen

    def check_oxygen_saturation(self):
        """
        Check the oxygen saturation of hemoglobin in the red blood cell.

        :return: Oxygen saturation level as a percentage.
        """
        return self.hemoglobin.oxygen_saturation()

    def mutate_hemoglobin(self, position, new_amino_acid):
        """
        Mutate the hemoglobin protein inside the red blood cell.

        :param position: Position to mutate in the sequence.
        :param new_amino_acid: New amino acid to introduce at the position.
        """
        mutation_result = self.hemoglobin.mutate_sequence(position, new_amino_acid)
        self.update_health_status()
        return mutation_result

    def display_structure(self):
        """
        Display the 3D structure of hemoglobin within the red blood cell.
        """
        return self.hemoglobin.display_3d_structure()

    HEALTH_STATUS = {
        'normal': 100,  # Healthy cell
        'senescent': 20,  # Aging cell
        'hypoxic': 50,  # Low oxygen
        'hyperoxic': 150,
    }

    def update_health_status(self):
        """
        Update the health status of the red blood cell based on various factors.
        """
        oxygen_saturation = self.check_oxygen_saturation()

        if self.age > self.lifespan:
            self.health_status = self.HEALTH_STATUS['senescent']
        elif oxygen_saturation < 70:
            self.health_status = self.HEALTH_STATUS['hypoxic']
        elif oxygen_saturation > 98:
            self.health_status = self.HEALTH_STATUS['hyperoxic']
        else:
            self.health_status = self.HEALTH_STATUS['normal']

    def age_cell(self, days):
        """
        Age the cell by a specified number of days.

        :param days: Number of days to age the cell.
        """
        self.age += days
        self.update_health_status()

    def is_healthy(self):
        """
        Check if the red blood cell is healthy.

        :return: Boolean indicating whether the cell is healthy.
        """
        return self.health_status == 'normal'

    def __str__(self):
        """
        Return a string representation of the Red Blood Cell.
        """
        return (f"Red Blood Cell\nHealth Status: {self.health_status}\n"
                f"Age: {self.age} days\n"
                f"Oxygen Saturation: {self.check_oxygen_saturation()}%\n"
                f"{str(self.hemoglobin)}\n")
