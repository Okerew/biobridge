import requests
from typing import List, Dict, Any
from biobridge.blocks.cell import Cell
from biobridge.tools.flow_cytometer import FlowCytometer


class IPFlowCytometer(FlowCytometer):
    def __init__(self, ip: str, port: int = 80, timeout: int = 1):
        """
        Initialize a new IPFlowCytometer object.

        :param ip: The IP address of the flow cytometer.
        :param port: The port number to connect to.
        :param timeout: Timeout for the HTTP request.
        """
        super().__init__()
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{ip}:{port}"
        self.custom_commands = {}  # Dictionary to store custom commands

    def send_command(self, command: str) -> str:
        """
        Send a command to the flow cytometer and receive a response.

        :param command: The command to send.
        :return: The response from the flow cytometer.
        """
        if command is None:
            raise ValueError("Command cannot be None.")
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")

        url = f"{self.base_url}/command"
        data = {"command": command}
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            print(f"Failed to send command to flow cytometer: {e}")
            return

    def execute_custom_command(self, command_name: str, *args) -> str:
        """
        Execute a custom command registered with the flow cytometer.

        :param command_name: The name of the custom command to execute.
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

    def analyze_cells(self) -> List[Dict[str, Any]]:
        """
        Analyze the cells in the flow cytometer.

        :return: A list of dictionaries containing analysis data for each cell
        """
        analysis_data = super().analyze_cells()
        # Send the analysis data to the flow cytometer
        command = f"ANALYZE:{analysis_data}"
        response = self.send_command(command)
        print(f"Flow cytometer response: {response}")
        return analysis_data

    def profile_cells(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Profile the cells in the flow cytometer based on cell type.

        :return: A dictionary with cell types as keys and lists of cell profiles as values
        """
        profiles = super().profile_cells()
        # Send the profile data to the flow cytometer
        command = f"PROFILE:{profiles}"
        response = self.send_command(command)
        print(f"Flow cytometer response: {response}")
        return profiles

    def sort_cells(self, criteria: str, ascending: bool = True) -> List['Cell']:
        """
        Sort the cells in the flow cytometer based on a specific criterion.

        :param criteria: The criterion to sort by (e.g., 'health', 'age', 'metabolism_rate')
        :param ascending: Whether to sort in ascending order (default is True)
        :return: A list of cells sorted by the specified criterion
        """
        sorted_cells = super().sort_cells(criteria, ascending)
        # Send the sorted cells data to the flow cytometer
        command = f"SORT:{criteria}:{ascending}"
        response = self.send_command(command)
        print(f"Flow cytometer response: {response}")
        return sorted_cells

    def describe(self) -> str:
        """
        Provide a detailed description of the flow cytometer and its cells.
        """
        description = super().describe()
        # Send the description to the flow cytometer
        command = f"DESCRIBE:{description}"
        response = self.send_command(command)
        print(f"Flow cytometer response: {response}")
        return description
