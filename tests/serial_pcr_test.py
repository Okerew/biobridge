import unittest
from unittest.mock import MagicMock, patch
from biobridge.control.serial.pcr import SerialPCR


class TestSerialPCR(unittest.TestCase):
    @patch('serial.Serial')
    def test_connect_and_disconnect(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Create SerialPCR instance
        pcr_machine = SerialPCR(sequence="ATCGATCGATCGATCGATCG", forward_primer="ATCG", reverse_primer="GATC", port="COM3")

        # Connect to the mock PCR machine
        pcr_machine.connect()
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.is_open = True

        # Disconnect from the mock PCR machine
        pcr_machine.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_set_cycles(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Cycles set to 30\n'

        # Create SerialPCR instance
        pcr_machine = SerialPCR(sequence="ATCGATCGATCGATCGATCG", forward_primer="ATCG", reverse_primer="GATC", port="COM3")

        # Connect to the mock PCR machine
        pcr_machine.connect()

        # Set the number of PCR cycles
        pcr_machine.set_cycles(30)
        mock_conn.write.assert_called_with(b'SET_CYCLES:30')
        mock_conn.readline.assert_called_once()

        # Disconnect from the mock PCR machine
        pcr_machine.disconnect()

    @patch('serial.Serial')
    def test_set_temperature(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Temperature set to 60.0 C\n'

        # Create SerialPCR instance
        pcr_machine = SerialPCR(sequence="ATCGATCGATCGATCGATCG", forward_primer="ATCG", reverse_primer="GATC", port="COM3")

        # Connect to the mock PCR machine
        pcr_machine.connect()

        # Set the temperature for the PCR process
        pcr_machine.set_temperature(60.0)
        mock_conn.write.assert_called_with(b'SET_TEMPERATURE:60.0')
        mock_conn.readline.assert_called_once()

        # Disconnect from the mock PCR machine
        pcr_machine.disconnect()

    @patch('serial.Serial')
    def test_start_and_stop_pcr(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'PCR started\n'

        # Create SerialPCR instance
        pcr_machine = SerialPCR(sequence="ATCGATCGATCGATCGATCG", forward_primer="ATCG", reverse_primer="GATC", port="COM3")

        # Connect to the mock PCR machine
        pcr_machine.connect()

        # Start the PCR process
        pcr_machine.start_pcr()
        mock_conn.write.assert_called_with(b'START_PCR')
        mock_conn.readline.assert_called_once()

        # Stop the PCR process
        mock_conn.readline.return_value = b'PCR stopped\n'
        pcr_machine.stop_pcr()
        mock_conn.write.assert_called_with(b'STOP_PCR')
        mock_conn.readline.assert_called()

        # Disconnect from the mock PCR machine
        pcr_machine.disconnect()

    @patch('serial.Serial')
    def test_get_status(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'IDLE\n'

        # Create SerialPCR instance
        pcr_machine = SerialPCR(sequence="ATCGATCGATCGATCGATCG", forward_primer="ATCG", reverse_primer="GATC", port="COM3")

        # Connect to the mock PCR machine
        pcr_machine.connect()

        # Get the status of the PCR machine
        status = pcr_machine.get_status()
        mock_conn.write.assert_called_with(b'GET_STATUS')
        mock_conn.readline.assert_called_once()
        self.assertEqual(status, 'IDLE')

        # Disconnect from the mock PCR machine
        pcr_machine.disconnect()


if __name__ == '__main__':
    unittest.main()
