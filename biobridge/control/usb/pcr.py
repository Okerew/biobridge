import usb.core
import usb.util
from biobridge.tools.pcr import PCR


class UsbPCR(PCR):
    def __init__(self, sequence, forward_primer, reverse_primer, usb_vendor_id, usb_product_id, timeout=1000, cycles=30,
                 mutation_rate=0.001):
        """
        Initialize the UsbPCR object.

        :param sequence: The nucleotide sequence of the DNA or RNA strand
        :param forward_primer: The forward primer sequence
        :param reverse_primer: The reverse primer sequence
        :param usb_vendor_id: The USB vendor ID of the PCR machine.
        :param usb_product_id: The USB product ID of the PCR machine.
        :param timeout: Timeout for the USB communication (in milliseconds).
        :param cycles: Number of PCR cycles (default is 30)
        :param mutation_rate: The probability of a mutation occurring at each nucleotide (default is 0.001)
        """
        super().__init__(sequence, forward_primer, reverse_primer, cycles, mutation_rate)
        self.vendor_id = usb_vendor_id
        self.product_id = usb_product_id
        self.timeout = timeout
        self.device = None
        self.endpoint_out = None
        self.endpoint_in = None
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the PCR machine over USB."""
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)

        if self.device is None:
            raise ValueError("PCR machine not found")

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

        print("Connected to the PCR machine over USB")

    def disconnect(self):
        """Close the USB connection."""
        if self.device:
            usb.util.dispose_resources(self.device)
            self.device = None
            print("Disconnected from the PCR machine")

    def send_command(self, command: str) -> str:
        """
        Send a command to the PCR machine and receive a response.

        :param command: The command to send.
        :return: The response from the PCR machine.
        """
        if command is None:
            raise ValueError("Command cannot be None.")
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")

        if not self.device:
            raise ConnectionError("Not connected to the PCR machine")

        try:
            # Send command to the device
            self.endpoint_out.write(command.encode('utf-8'), self.timeout)

            # Read response from the device
            response = self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, self.timeout)

            # Convert response to a string
            return ''.join([chr(x) for x in response])

        except usb.core.USBError as e:
            print(f"Failed to send command '{command}': {e}")
            return ""

    def start_pcr(self):
        """Send a command to start the PCR process."""
        command = "START_PCR"
        response = self.send_command(command)
        print(f"PCR machine response: {response}")

    def stop_pcr(self):
        """Send a command to stop the PCR process."""
        command = "STOP_PCR"
        response = self.send_command(command)
        print(f"PCR machine response: {response}")

    def set_cycles(self, cycles: int):
        """
        Set the number of PCR cycles.

        :param cycles: Number of PCR cycles.
        """
        command = f"SET_CYCLES:{cycles}"
        response = self.send_command(command)
        print(f"PCR machine response: {response}")

    def set_temperature(self, temperature: float):
        """
        Set the temperature for the PCR process.

        :param temperature: Temperature in Celsius.
        """
        command = f"SET_TEMPERATURE:{temperature}"
        response = self.send_command(command)
        print(f"PCR machine response: {response}")

    def get_status(self):
        """Get the current status of the PCR machine."""
        command = "GET_STATUS"
        response = self.send_command(command)
        print(f"PCR machine status: {response}")
        return response

    def execute_custom_command(self, command_name: str, *args) -> str:
        """
        Execute a custom command registered with the PCR machine.

        :param command_name: The name of the custom command to execute.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the PCR machine.
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
