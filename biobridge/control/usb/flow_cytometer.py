import usb.core
import usb.util
from typing import List, Dict, Any
from biobridge.blocks.cell import Cell
from biobridge.tools.flow_cytometer import FlowCytometer


class UsbFlowCytometer(FlowCytometer):
    def __init__(self, usb_vendor_id: int, usb_product_id: int, timeout: int = 1000):
        """
        Initialize the UsbFlowCytometer object.

        :param usb_vendor_id: The USB vendor ID of the flow cytometer.
        :param usb_product_id: The USB product ID of the flow cytometer.
        :param timeout: Timeout for the USB communication.
        """
        super().__init__()
        self.vendor_id = usb_vendor_id
        self.product_id = usb_product_id
        self.timeout = timeout
        self.device = None
        self.endpoint_out = None
        self.endpoint_in = None
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the flow cytometer over USB."""
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)

        if self.device is None:
            raise ValueError("Flow cytometer not found")

        # Set the active configuration. With no arguments, the first configuration will be the active one
        self.device.set_configuration()

        # Get an endpoint instance
        cfg = self.device.get_active_configuration()
        intf = cfg[(0, 0)]
        self.endpoint_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

        self.endpoint_in = usb.util.find_descriptor(
            intf,
            custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

        print("Connected to the flow cytometer over USB")

    def disconnect(self):
        """Close the USB connection."""
        if self.device:
            usb.util.dispose_resources(self.device)
            self.device = None
            print("Disconnected from the flow cytometer")

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

        if not self.device:
            raise ConnectionError("Not connected to the flow cytometer")

        try:
            # Send command to the flow cytometer
            self.endpoint_out.write(command.encode('utf-8'), self.timeout)

            # Read response from the flow cytometer
            response = self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, self.timeout)

            # Convert response to a string
            return ''.join([chr(x) for x in response])

        except usb.core.USBError as e:
            print(f"Failed to send command '{command}': {e}")
            return ""

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
