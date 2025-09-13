from typing import List, Dict
from biobridge.blocks.cell import Cell


class FlowCytometer:
    def __init__(self):
        """
        Initialize a new FlowCytometer object.
        """
        self.cells = []

    def add_cell(self, cell: 'Cell') -> None:
        """
        Add a cell to the flow cytometer.

        :param cell: The cell to add
        """
        self.cells.append(cell)

    def analyze_cells(self) -> List[Dict[str, any]]:
        """
        Analyze the cells in the flow cytometer.

        :return: A list of dictionaries containing analysis data for each cell
        """
        analysis_data = []
        for cell in self.cells:
            analysis = {
                'name': cell.name,
                'cell_type': cell.cell_type,
                'health': cell.health,
                'age': cell.age,
                'metabolism_rate': cell.metabolism_rate,
                'receptors': cell.receptors,
                'surface_proteins': cell.surface_proteins,
                'organelles': cell.organelles,
                'ph': cell.ph,
                'osmolarity': cell.osmolarity,
                'ion_concentrations': cell.ion_concentrations
            }
            analysis_data.append(analysis)
        return analysis_data

    def profile_cells(self) -> Dict[str, List[Dict[str, any]]]:
        """
        Profile the cells in the flow cytometer based on cell type.

        :return: A dictionary with cell types as keys and lists of cell profiles as values
        """
        profiles = {}
        for cell in self.cells:
            if cell.cell_type not in profiles:
                profiles[cell.cell_type] = []
            profiles[cell.cell_type].append({
                'name': cell.name,
                'health': cell.health,
                'age': cell.age,
                'metabolism_rate': cell.metabolism_rate,
                'receptors': cell.receptors,
                'surface_proteins': cell.surface_proteins,
                'organelles': cell.organelles,
                'ph': cell.ph,
                'osmolarity': cell.osmolarity,
                'ion_concentrations': cell.ion_concentrations
            })
        return profiles

    def sort_cells(self, criteria: str, ascending: bool = True) -> List['Cell']:
        """
        Sort the cells in the flow cytometer based on a specific criterion.

        :param criteria: The criterion to sort by (e.g., 'health', 'age', 'metabolism_rate')
        :param ascending: Whether to sort in ascending order (default is True)
        :return: A list of cells sorted by the specified criterion
        """
        if criteria not in ['health', 'age', 'metabolism_rate']:
            raise ValueError("Invalid sorting criterion. Choose from 'health', 'age', 'metabolism_rate'.")

        sorted_cells = sorted(self.cells, key=lambda cell: getattr(cell, criteria), reverse=not ascending)
        return sorted_cells

    def describe(self) -> str:
        """
        Provide a detailed description of the flow cytometer and its cells.
        """
        description = ["Flow Cytometer Analysis:"]
        for cell in self.cells:
            description.append(cell.describe())
        return "\n".join(description)

    def __str__(self) -> str:
        """
        Return a string representation of the flow cytometer.
        """
        return self.describe()
