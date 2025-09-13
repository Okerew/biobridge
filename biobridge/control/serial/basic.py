import serial
import time


class SerialBasic:
    def __init__(self, guide_rna: str, port: str, baudrate: int = 9600, timeout: int = 1):
        """
        Initialize the SerialCRISPR object.

        :param guide_rna: The guide RNA sequence.
        :param port: The serial port to connect to (e.g., 'COM3' or '/dev/ttyUSB0').
        :param baudrate: The baud rate for the serial connection.
        :param timeout: Timeout for the serial connection.
        """
        super().__init__(guide_rna)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a serial connection to the CRISPR kit."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Wait for the connection to establish
            print(f"Connected to the machine on {self.port}")
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print(f"Disconnected from {self.port}")

    def send_command(self, command: str) -> str:
        """
        Send a command to the CRISPR kit and receive a response.

        :param command: The command to send.
        :return: The response from the machine
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            raise ConnectionError("Not connected to any machine. Please connect first.")

        if command is None:
            raise ValueError("Command cannot be None.")
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")

        command_encoded = command.encode('utf-8')
        self.serial_conn.write(command_encoded)
        time.sleep(1)  # Wait for the device to process the command
        response = self.serial_conn.readline().decode('utf-8').strip()
        return response

    def execute_custom_command(self, command_name: str, *args) -> str:
        """
        Execute a custom command registered with the basic kit.

        :param command_name: The name of the custom command to execute.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the basic kit.
        """
        if command_name not in self.custom_commands:
            raise ValueError(f"Custom command '{command_name}' not found.")

        command_func = self.custom_commands[command_name]
        command = command_func(*args)

        if command is None:
            raise ValueError(f"Custom command function for '{command_name}' returned None.")
        if not isinstance(command, str):
            raise TypeError(f"Custom command function for '{command_name}' must return a string.")

        print(f"Executing custom command: {command}")
        return self.send_command(command)

    def register_custom_command(self, name: str, func):
        """
        Register a custom command.

        :param name: The name of the custom command.
        :param func: A function that takes parameters and returns a command string.
        """
        if not callable(func):
            raise TypeError("Function must be callable.")
        self.custom_commands[name] = func
