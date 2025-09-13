import unittest
from unittest.mock import MagicMock, patch
from biobridge.genes.dna import DNA
from biobridge.control.serial.crispr import SerialCRISPR


def custom_command_func(param1, param2):
    return f"CUSTOM:{param1},{param2}"


class TestSerialCRISPR(unittest.TestCase):
    @patch('serial.Serial')
    def test_execute_edit(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Simulate the CRISPR kit response to a command
        mock_conn.readline.return_value = b'OK\n'

        # Create DNA and SerialCRISPR instance
        dna = DNA("ATGCTAGCTAGCTAGCTAGCTAGCTA")
        crispr = SerialCRISPR(guide_rna="TAGC", port="COM3")

        # Connect to the mock CRISPR kit
        crispr.connect()

        # Perform an insert edit
        edited_dna = crispr.execute_edit(dna, 'insert', 'GTC', occurrence=3)

        print(edited_dna)

        # Test disconnection
        crispr.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_execute_custom_command(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'OK\n'
        crispr = SerialCRISPR(guide_rna="TAGC", port="COM3")
        crispr.connect()

        crispr.register_custom_command("my_custom_command", custom_command_func)

        # Execute the custom command
        response = crispr.execute_custom_command("my_custom_command", "value1", "value2")
        print(response)
        crispr.disconnect()

    @patch('serial.Serial')
    def test_simulate_off_target_effects(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Simulate the CRISPR kit response to a command
        mock_conn.readline.return_value = b'OK\n'

        # Create DNA and SerialCRISPR instance
        dna = DNA("ATGCTAGCTAGCTAGCTAGCTAGCTA")
        crispr = SerialCRISPR(guide_rna="TAGC", port="COM3")

        # Connect to the mock CRISPR kit
        crispr.connect()

        # Perform off-target simulation
        mutated_dna = crispr.simulate_off_target_effects(dna, mutation_rate=0.5)

        print(mutated_dna)

        # Verify the serial command was sent correctly
        expected_command = b'MUTATION:0.5'
        mock_conn.write.assert_called_with(expected_command)

        # Since mutation is random, ensure the mock was called but don't assert sequence
        mock_conn.readline.assert_called_once()

        # Test disconnection
        crispr.disconnect()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
