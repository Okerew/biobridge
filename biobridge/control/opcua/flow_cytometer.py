from typing import List, Dict, Any
from opcua import Client
from biobridge.blocks.cell import Cell
from biobridge.tools.flow_cytometer import FlowCytometer


class OpcuaFlowCytometer(FlowCytometer):
    def __init__(self, ip_address: str, port: int = 4840, timeout: int = 1):
        """
        Initialize a new OpcuaFlowCytometer object.

        :param ip_address: The IP address of the OPC UA server.
        :param port: The port number to connect to. Defaults to 4840 (OPC UA default port).
        :param timeout: Timeout for the OPC UA client.
        """
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.url = f"opc.tcp://{self.ip_address}:{self.port}"
        self.client = Client(self.url)
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the OPC UA server."""
        try:
            self.client.connect()
            print(f"Connected to OPC UA server at {self.url}")
        except Exception as e:
            print(f"Failed to connect to {self.url}: {e}")

    def disconnect(self):
        """Close the connection."""
        try:
            self.client.disconnect()
            print(f"Disconnected from {self.url}")
        except Exception as e:
            print(f"Failed to disconnect from {self.url}: {e}")

    def send_command(self, command: str, node_id: str) -> str:
        """
        Send a command to the flow cytometer and receive a response.

        :param command: The command to send.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: The response from the flow cytometer.
        """
        try:
            node = self.client.get_node(node_id)
            node.set_value(command)
            response = node.get_value()
            return response
        except Exception as e:
            print(f"Failed to send command '{command}': {e}")
            return ""

    def execute_custom_command(self, command_name: str, node_id: str, *args) -> str:
        """
        Execute a custom command registered with the flow cytometer.

        :param command_name: The name of the custom command to execute.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the flow cytometer.
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

    def analyze_cells(self, node_id: str = "ns=2;i=2") -> List[Dict[str, Any]]:
        """
        Analyze the cells in the flow cytometer.

        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: A list of dictionaries containing analysis data for each cell
        """
        analysis_data = super().analyze_cells()
        # Send the analysis data to the flow cytometer
        command = f"ANALYZE:{analysis_data}"
        response = self.send_command(command, node_id)
        print(f"Flow cytometer response: {response}")
        return analysis_data

    def profile_cells(self, node_id: str = "ns=2;i=3") -> Dict[str, List[Dict[str, Any]]]:
        """
        Profile the cells in the flow cytometer based on cell type.

        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: A dictionary with cell types as keys and lists of cell profiles as values
        """
        profiles = super().profile_cells()
        # Send the profile data to the flow cytometer
        command = f"PROFILE:{profiles}"
        response = self.send_command(command, node_id)
        print(f"Flow cytometer response: {response}")
        return profiles

    def sort_cells(self, criteria: str, ascending: bool = True, node_id: str = "ns=2;i=4") -> List['Cell']:
        """
        Sort the cells in the flow cytometer based on a specific criterion.

        :param criteria: The criterion to sort by (e.g., 'health', 'age', 'metabolism_rate')
        :param ascending: Whether to sort in ascending order (default is True)
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: A list of cells sorted by the specified criterion
        """
        sorted_cells = super().sort_cells(criteria, ascending)
        # Send the sorted cells data to the flow cytometer
        command = f"SORT:{criteria}:{ascending}"
        response = self.send_command(command, node_id)
        print(f"Flow cytometer response: {response}")
        return sorted_cells

    def describe(self, node_id: str = "ns=2;i=5") -> str:
        """
        Provide a detailed description of the flow cytometer and its cells.

        :param node_id: The node ID of the OPC UA object to write the command to.
        """
        description = super().describe()
        # Send the description to the flow cytometer
        command = f"DESCRIBE:{description}"
        response = self.send_command(command, node_id)
        print(f"Flow cytometer response: {response}")
        return description
