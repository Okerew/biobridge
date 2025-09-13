from opcua import Client
from biobridge.tools.pcr import PCR


class OpcuaPCR(PCR):
    def __init__(self, sequence, forward_primer, reverse_primer, ip_address, port=4840, cycles=30, mutation_rate=0.001):
        """
        Initialize the OpcuaPCR object.

        :param sequence: The nucleotide sequence of the DNA or RNA strand
        :param forward_primer: The forward primer sequence
        :param reverse_primer: The reverse primer sequence
        :param ip_address: The IP address of the OPC UA server.
        :param port: The port number of the OPC UA server. Defaults to 4840 (OPC UA default port).
        :param cycles: Number of PCR cycles (default is 30)
        :param mutation_rate: The probability of a mutation occurring at each nucleotide (default is 0.001)
        """
        super().__init__(sequence, forward_primer, reverse_primer, cycles, mutation_rate)
        self.ip_address = ip_address
        self.port = port
        self.url = f"opc.tcp://{self.ip_address}:{self.port}"
        self.client = Client(self.url)
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish an OPC UA connection to the PCR machine."""
        try:
            self.client.connect()
            print(f"Connected to PCR machine at {self.url}")
        except Exception as e:
            print(f"Failed to connect to {self.url}: {e}")

    def disconnect(self):
        """Close the OPC UA connection."""
        self.client.disconnect()
        print(f"Disconnected from {self.url}")

    def send_command(self, command: str, node_id: str) -> str:
        """
        Send a command to the PCR machine and receive a response.

        :param command: The command to send.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: The response from the PCR machine.
        """

        try:
            node = self.client.get_node(node_id)
            node.set_value(command)
            response = node.get_value()
            return response
        except Exception as e:
            print(f"Failed to send command '{command}': {e}")
            return ""

    def start_pcr(self, node_id: str = "ns=2;i=2"):
        """Send a command to start the PCR process."""
        command = "START_PCR"
        response = self.send_command(command, node_id)
        print(f"PCR machine response: {response}")

    def stop_pcr(self, node_id: str = "ns=2;i=3"):
        """Send a command to stop the PCR process."""
        command = "STOP_PCR"
        response = self.send_command(command, node_id)
        print(f"PCR machine response: {response}")

    def set_cycles(self, cycles: int, node_id: str = "ns=2;i=4"):
        """
        Set the number of PCR cycles.

        :param cycles: Number of PCR cycles.
        """
        command = f"SET_CYCLES:{cycles}"
        response = self.send_command(command, node_id)
        print(f"PCR machine response: {response}")

    def set_temperature(self, temperature: float, node_id: str = "ns=2;i=5"):
        """
        Set the temperature for the PCR process.

        :param temperature: Temperature in Celsius.
        """
        command = f"SET_TEMPERATURE:{temperature}"
        response = self.send_command(command, node_id)
        print(f"PCR machine response: {response}")

    def get_status(self, node_id: str = "ns=2;i=6"):
        """Get the current status of the PCR machine."""
        command = "GET_STATUS"
        response = self.send_command(command, node_id)
        print(f"PCR machine status: {response}")
        return response

    def execute_custom_command(self, command_name: str, node_id: str, *args) -> str:
        """
        Execute a custom command registered with the basic kit.

        :param command_name: The name of the custom command to execute.
        :param node_id: The node ID of the OPC UA object to write the command to.
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
        return self.send_command(command, node_id)

    def register_custom_command(self, name: str, func):
        """
        Register a custom command.

        :param name: The name of the custom command.
        :param func: A function that takes parameters and returns a command string.
        """
        if not callable(func):
            raise TypeError("Function must be callable.")
        self.custom_commands[name] = func
