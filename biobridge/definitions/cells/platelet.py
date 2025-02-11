from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell
from biobridge.definitions.cells.red_blood_cell import RedBloodCell


class Platelet(EukaryoticCell):
    """
    Represents a platelet, a cell fragment that plays a crucial role in blood clotting.
    Inherits from the Cell class and adds specific functionality for clotting and interaction with red blood cells.
    """
    
    def __init__(self, cell_type='Platelet', health_status=100):
        super().__init__(name="Platelet", cell_type=cell_type, health=health_status)
        self.activated = False
        self.bound_red_blood_cells = []  # Keeps track of bound red blood cells
        self.lifespan = 10  # Average lifespan of a platelet cell in days
        self.health_status = health_status
    
    def activate(self):
        """
        Activates the platelet, enabling it to bind to other cells like red blood cells.
        """
        if not self.activated:
            self.activated = True
            print("Platelet activated and ready for clot formation.")
        else:
            print("Platelet is already activated.")

    HEALTH_STATUS = {
        'normal': 100,  # Healthy cell
        'senescent': 20,  # Aging cell
    }

    def update_health_status(self):
        """
        Update the health status of the red blood cell based on various factors.
        """
        if self.age > self.lifespan:
            self.health_status = self.HEALTH_STATUS['senescent']
        else:
            self.health_status = self.HEALTH_STATUS['normal']

    def bind_red_blood_cell(self, red_blood_cell):
        """
        Binds to a red blood cell during clot formation, simulating interaction.
        
        :param red_blood_cell: A RedBloodCell instance to bind to.
        """
        if not self.activated:
            print("Platelet needs to be activated before binding to red blood cells.")
            return
        
        if isinstance(red_blood_cell, RedBloodCell):
            self.bound_red_blood_cells.append(red_blood_cell)
            print(f"Platelet bound to {red_blood_cell.cell_type} successfully.")
        else:
            print("Can only bind to Red Blood Cells.")

    def form_clot(self):
        """
        Simulates the process of clot formation with bound red blood cells.
        """
        if self.activated and self.bound_red_blood_cells:
            print(f"Clot formed with {len(self.bound_red_blood_cells)} red blood cell(s).")
            # Reset the platelet after clot formation
            self.activated = False
            self.bound_red_blood_cells.clear()
        else:
            print("Clot formation requires an activated platelet and bound red blood cells.")
    
    def __str__(self):
        """
        Return a string representation of the Platelet.
        """
        activation_status = "Activated" if self.activated else "Inactive"
        bound_cells = len(self.bound_red_blood_cells)
        return (f"Platelet\nHealth Status: {self.health_status}\n"
                f"Activation Status: {activation_status}\n"
                f"Bound Red Blood Cells: {bound_cells}\n")
