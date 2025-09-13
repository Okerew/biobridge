import unittest
from unittest.mock import MagicMock, patch
from biobridge.control.serial.gee import SerialGelElectrophoresisController
from biobridge.control.serial.alh import SerialAutomatedLiquidHandler


class TestGelElectrophoresisController(unittest.TestCase):
    @patch('serial.Serial')
    def test_connect_and_disconnect(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Create GelElectrophoresisController instance
        controller = SerialGelElectrophoresisController(port="COM3")

        # Connect to the mock gel electrophoresis equipment
        controller.connect()
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.is_open = True

        # Disconnect from the mock gel electrophoresis equipment
        controller.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_send_command(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Command received\n'

        # Create GelElectrophoresisController instance
        controller = SerialGelElectrophoresisController(port="COM3")

        # Connect to the mock gel electrophoresis equipment
        controller.connect()

        # Send a command
        response = controller.send_command("TEST_COMMAND")
        mock_conn.write.assert_called_with(b'TEST_COMMAND')
        mock_conn.readline.assert_called_once()
        self.assertEqual(response, 'Command received')

        # Disconnect from the mock gel electrophoresis equipment
        controller.disconnect()

    @patch('serial.Serial')
    def test_set_voltage(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Voltage set\n'

        # Create GelElectrophoresisController instance
        controller = SerialGelElectrophoresisController(port="COM3")

        # Connect to the mock gel electrophoresis equipment
        controller.connect()

        # Set voltage
        response = controller.set_voltage(100)
        mock_conn.write.assert_called_with(b'SET_VOLTAGE 100')
        mock_conn.readline.assert_called_once()
        self.assertEqual(response, 'Voltage set')

        # Disconnect from the mock gel electrophoresis equipment
        controller.disconnect()

    @patch('serial.Serial')
    def test_run_gel_electrophoresis(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'{"status": "running"}\n'

        # Create GelElectrophoresisController instance
        controller = SerialGelElectrophoresisController(port="COM3")

        # Run the gel electrophoresis experiment
        with patch('time.sleep'):  # Mock sleep to speed up test
            controller.run_gel_electrophoresis(voltage=100, run_time=1)

        # Check that the correct methods were called
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.write.assert_any_call(b'SET_VOLTAGE 100')
        mock_conn.write.assert_any_call(b'SET_RUN_TIME 1')
        mock_conn.write.assert_any_call(b'START_RUN')
        mock_conn.write.assert_any_call(b'GET_STATUS')
        mock_conn.write.assert_any_call(b'STOP_RUN')
        mock_conn.close.assert_called_once()


class TestAutomatedLiquidHandler(unittest.TestCase):
    @patch('serial.Serial')
    def test_connect_and_disconnect(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Create AutomatedLiquidHandler instance
        handler = SerialAutomatedLiquidHandler(port="COM3")

        # Connect to the mock liquid handler
        handler.connect()
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.is_open = True

        # Disconnect from the mock liquid handler
        handler.disconnect()
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_send_command(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Command received\n'

        # Create AutomatedLiquidHandler instance
        handler = SerialAutomatedLiquidHandler(port="COM3")

        # Connect to the mock liquid handler
        handler.connect()

        # Send a command
        response = handler.send_command("TEST_COMMAND")
        mock_conn.write.assert_called_with(b'TEST_COMMAND')
        mock_conn.readline.assert_called_once()
        self.assertEqual(response, 'Command received')

        # Disconnect from the mock liquid handler
        handler.disconnect()

    @patch('serial.Serial')
    def test_move_to_position(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Moved to position\n'

        # Create AutomatedLiquidHandler instance
        handler = SerialAutomatedLiquidHandler(port="COM3")

        # Connect to the mock liquid handler
        handler.connect()

        # Move to position
        response = handler.move_to_position(10.0, 20.0, 5.0)
        mock_conn.write.assert_called_with(b'MOVE_TO 10.0 20.0 5.0')
        mock_conn.readline.assert_called_once()
        self.assertEqual(response, 'Moved to position')

        # Disconnect from the mock liquid handler
        handler.disconnect()

    @patch('serial.Serial')
    def test_run_liquid_transfer(self, mock_serial):
        # Setup mock serial connection
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.readline.return_value = b'Operation completed\n'

        # Create AutomatedLiquidHandler instance
        handler = SerialAutomatedLiquidHandler(port="COM3")

        # Run the liquid transfer operation
        source_pos = (10.0, 20.0, 5.0)
        dest_pos = (50.0, 60.0, 5.0)
        handler.run_liquid_transfer(source_pos, dest_pos, 100.0)

        # Check that the correct methods were called
        mock_serial.assert_called_once_with("COM3", 9600, timeout=1)
        mock_conn.write.assert_any_call(b'CHANGE_TIP')
        mock_conn.write.assert_any_call(b'MOVE_TO 10.0 20.0 5.0')
        mock_conn.write.assert_any_call(b'ASPIRATE 100.0')
        mock_conn.write.assert_any_call(b'MOVE_TO 50.0 60.0 5.0')
        mock_conn.write.assert_any_call(b'DISPENSE 100.0')
        mock_conn.write.assert_any_call(b'WASH_TIP')
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
