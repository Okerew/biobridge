from biobridge.blocks.cell import Cell, Vacuole, Optional, DNA, plt, patches, Organelle
import numpy as np

class PlantCell(Cell):
    def __init__(self, name: str, cell_type: str = "plant", 
                 dna: Optional[DNA] = None, **kwargs):
        super().__init__(name, cell_type, dna=dna, **kwargs)
        
        self.chloroplasts = [Organelle("Organelle") for _ in range(3)]
        self.central_vacuole = Vacuole()
        
        self.photosynthetic_rate = 0.1
        self.cellulose_synthesis_rate = 0.05
        self.starch_storage = 0.0
        
        if not hasattr(self, 'cellular_structures'):
            self.cellular_structures = {}
        
        for i, chloroplast in enumerate(self.chloroplasts):
            self.cellular_structures[f"chloroplast_{i}"] = chloroplast

    def photosynthesize(self, light_intensity: float, co2_level: float) -> float:
        efficiency = self.photosynthetic_rate
        glucose_produced = light_intensity * co2_level * efficiency * 0.01
        return glucose_produced

    def synthesize_cellulose(self) -> float:
        if self.health > 20:
            cellulose_amount = self.cellulose_synthesis_rate * self.health * 0.01
            self.health -= 5
            return cellulose_amount
        return 0

    def respond_to_light_stress(self, uv_intensity: float) -> None:
        if uv_intensity > 5.0:
            self.health -= uv_intensity * 2

    def water_uptake(self, water_availability: float) -> None:
        self.central_vacuole.adjust_turgor_pressure(water_availability)
        
        if self.central_vacuole.turgor_pressure < 0.2:
            self.health -= 10
        elif self.central_vacuole.turgor_pressure > 0.8:
            self.health = min(100, self.health + 5)

    def cell_division_with_wall_formation(self) -> 'PlantCell':
        if self.health < 30:
            return None
        
        new_cell = PlantCell(f"{self.name}_daughter", 
                           dna=self.dna.replicate() if self.dna else None)
        
        self.synthesize_cellulose()
        new_cell.synthesize_cellulose()
        
        self.health -= 20
        return new_cell

    def describe(self) -> str:
        description = super().describe()
        plant_info = f"""
Plant Cell Specific Features:
    Chloroplasts: {len(self.chloroplasts)}
    Central Vacuole Volume: {self.central_vacuole.volume}%
    Turgor Pressure: {self.central_vacuole.turgor_pressure:.2f}
    Starch Storage: {self.starch_storage:.2f} units
    Photosynthetic Rate: {self.photosynthetic_rate}
        """
        return description + plant_info

    def to_dict(self) -> dict:
        cell_dict = super().to_dict()
        cell_dict.update({
            'chloroplasts': [c.name for c in self.chloroplasts],
            'photosynthetic_rate': self.photosynthetic_rate,
            'cellulose_synthesis_rate': self.cellulose_synthesis_rate,
            'starch_storage': self.starch_storage
        })
        return cell_dict

    @classmethod
    def from_dict(cls, cell_dict: dict) -> 'PlantCell':
        base_dict = {k: v for k, v in cell_dict.items() 
                    if k in Cell.__init__.__code__.co_varnames}
        
        plant_cell = cls(cell_dict['name'], **base_dict)
        
        plant_cell.chloroplasts = [c.name
                                  for c in cell_dict['chloroplasts']]
        plant_cell.photosynthetic_rate = cell_dict['photosynthetic_rate']
        plant_cell.cellulose_synthesis_rate = cell_dict[
                                             'cellulose_synthesis_rate']
        plant_cell.starch_storage = cell_dict['starch_storage']
        
        return plant_cell

    def visualize_plant_cell(self):
        fig, ax = plt.subplots(figsize=(12, 10))
        
        cell_wall = patches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                    linewidth=4, edgecolor='brown', 
                                    facecolor='none', label='Cell Wall')
        ax.add_patch(cell_wall)
        
        cell_membrane = patches.Rectangle((0.1, 0.1), 0.8, 0.8, 
                                        linewidth=2, edgecolor='black', 
                                        facecolor='lightgreen', alpha=0.3,
                                        label='Cell Membrane')
        ax.add_patch(cell_membrane)
        
        vacuole_size = self.central_vacuole.volume / 100 * 0.4
        central_vacuole = patches.Circle((0.5, 0.5), vacuole_size, 
                                       facecolor='lightblue', alpha=0.7,
                                       edgecolor='blue', 
                                       label='Central Vacuole')
        ax.add_patch(central_vacuole)
        
        for i, chloroplast in enumerate(self.chloroplasts):
            angle = i * 2 * np.pi / len(self.chloroplasts)
            x = 0.5 + 0.25 * np.cos(angle)
            y = 0.5 + 0.25 * np.sin(angle)
            
            chloroplast_patch = patches.Ellipse((x, y), 0.08, 0.05, 
                                              facecolor='darkgreen',
                                              edgecolor='green',
                                              label='Organelle' if i == 0 
                                              else "")
            ax.add_patch(chloroplast_patch)
        
        nucleus = patches.Circle((0.3, 0.7), 0.06, facecolor='purple',
                               alpha=0.8, edgecolor='darkpurple',
                               label='Nucleus')
        ax.add_patch(nucleus)
        
        info_text = f"""
Turgor Pressure: {self.central_vacuole.turgor_pressure:.2f}
Starch Storage: {self.starch_storage:.2f}
Health: {self.health}%
        """
        ax.text(0.02, 0.02, info_text.strip(), fontsize=9, va='bottom', 
                ha='left', bbox=dict(boxstyle="round,pad=0.3", 
                facecolor="white", alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(f"Plant Cell: {self.name}", fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.axis('off')
        
        plt.tight_layout()
        plt.show()

