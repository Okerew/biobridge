import unittest
from unittest.mock import patch, MagicMock
from biobridge.blocks.cell import Cell
from biobridge.control.serial.flow_cytometer import SerialFlowCytometer


class TestSerialFlowCytometer(unittest.TestCase):
    @patch('serial.Serial')
    def test_analyze_cells(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'OK\n'

        # Create cells and SerialFlowCytometer instance
        cell1 = Cell(name="Cell1", cell_type="Type1", health=90, age=5, receptors=["R1"], surface_proteins=["P1"], ph=7.4, osmolarity=300, ion_concentrations={"Na": 140})
        cell2 = Cell(name="Cell2", cell_type="Type2", health=80, age=3, receptors=["R2"], surface_proteins=["P2"], ph=7.2, osmolarity=280, ion_concentrations={"K": 5})
        flow_cytometer = SerialFlowCytometer(port="COM3")
        flow_cytometer.add_cell(cell1)
        flow_cytometer.add_cell(cell2)

        # Connect to the mock flow cytometer
        flow_cytometer.connect()

        # Analyze cells
        analysis_data = flow_cytometer.analyze_cells()

        print(analysis_data)

        # Test disconnection
        flow_cytometer.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_profile_cells(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'OK\n'

        # Create cells and SerialFlowCytometer instance
        cell1 = Cell(name="Cell1", cell_type="Type1", health=90, age=5, receptors=["R1"], surface_proteins=["P1"],  ph=7.4, osmolarity=300, ion_concentrations={"Na": 140})
        cell2 = Cell(name="Cell2", cell_type="Type2", health=80, age=3, receptors=["R2"], surface_proteins=["P2"], ph=7.2, osmolarity=280, ion_concentrations={"K": 5})
        flow_cytometer = SerialFlowCytometer(port="COM3")
        flow_cytometer.add_cell(cell1)
        flow_cytometer.add_cell(cell2)

        # Connect to the mock flow cytometer
        flow_cytometer.connect()

        # Profile cells
        profiles = flow_cytometer.profile_cells()

        print(profiles)

        # Test disconnection
        flow_cytometer.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_sort_cells(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'OK\n'

        # Create cells and SerialFlowCytometer instance
        cell1 = Cell(name="Cell1", cell_type="Type1", health=90, age=5, receptors=["R1"], surface_proteins=["P1"], ph=7.4, osmolarity=300, ion_concentrations={"Na": 140})
        cell2 = Cell(name="Cell2", cell_type="Type2", health=80, age=3, receptors=["R2"], surface_proteins=["P2"], ph=7.2, osmolarity=280, ion_concentrations={"K": 5})
        flow_cytometer = SerialFlowCytometer(port="COM3")
        flow_cytometer.add_cell(cell1)
        flow_cytometer.add_cell(cell2)

        # Connect to the mock flow cytometer
        flow_cytometer.connect()

        # Sort cells
        sorted_cells = flow_cytometer.sort_cells(criteria='health', ascending=True)

        print(sorted_cells)

        # Verify the serial command was sent correctly
        expected_command = b'SORT:health:True'
        mock_conn.write.assert_called_with(expected_command)

        # Test disconnection
        flow_cytometer.disconnect()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
