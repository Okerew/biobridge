import unittest
from unittest.mock import MagicMock, patch
from biobridge.control.serial.sequencer import SerialDNASequencer
from biobridge.genes.dna import DNA


class TestDNASequencer(unittest.TestCase):
    @patch('serial.Serial')
    def test_connect_and_disconnect(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Create DNASequencer instance
        sequencer = SerialDNASequencer(port="COM3")

        # Connect to the mock DNA sequencer
        sequencer.connect()
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.is_open = True

        # Disconnect from the mock DNA sequencer
        sequencer.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_send_command(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Command received\n'

        # Create DNASequencer instance
        sequencer = SerialDNASequencer(port="COM3")

        # Connect to the mock DNA sequencer
        sequencer.connect()

        # Send a command
        response = sequencer.send_command("TEST_COMMAND")
        mock_conn.write.assert_called_with(b'TEST_COMMAND')
        mock_conn.readline.assert_called_once()
        self.assertEqual(response, 'Command received')

        # Disconnect from the mock DNA sequencer
        sequencer.disconnect()

    @patch('serial.Serial')
    def test_get_sequence_json_response(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'{"sequence": "ATCG"}\n'

        # Create DNASequencer instance
        sequencer = SerialDNASequencer(port="COM3")

        # Connect to the mock DNA sequencer
        sequencer.connect()

        # Get the sequence
        dna = sequencer.get_sequence()
        mock_conn.write.assert_called_with(b'GET_SEQUENCE')
        mock_conn.readline.assert_called_once()
        self.assertIsInstance(dna, DNA)
        self.assertEqual(dna.sequence, "ATCG")

        # Disconnect from the mock DNA sequencer
        sequencer.disconnect()

    @patch('serial.Serial')
    def test_get_sequence_string_response(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'ATCG\n'

        # Create DNASequencer instance
        sequencer = SerialDNASequencer(port="COM3")

        # Connect to the mock DNA sequencer
        sequencer.connect()

        # Get the sequence
        dna = sequencer.get_sequence()
        mock_conn.write.assert_called_with(b'GET_SEQUENCE')
        mock_conn.readline.assert_called_once()
        self.assertIsInstance(dna, DNA)
        self.assertEqual(dna.sequence, "ATCG")

        # Disconnect from the mock DNA sequencer
        sequencer.disconnect()

    @patch('serial.Serial')
    @patch('biobridge.serial.sequencer.DNASequencer.analyze_sequence')
    def test_run_sequencing_experiment(self, mock_analyze, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'ATCG\n'

        # Create DNASequencer instance
        sequencer = SerialDNASequencer(port="COM3")

        # Run the sequencing experiment
        sequencer.run_sequencing_experiment()

        # Check that the correct methods were called
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.write.assert_called_with(b'GET_SEQUENCE')
        mock_conn.readline.assert_called_once()
        mock_analyze.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
