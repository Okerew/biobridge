import usb.core
import usb.util
from biobridge.genes.dna import DNA
from biobridge.tools.crispr import CRISPR


class UsbCRISPR(CRISPR):
    def __init__(self, guide_rna: str, usb_vendor_id: int, usb_product_id: int, timeout: int = 1000):
        """
        Initialize the UsbCRISPR object.

        :param guide_rna: The guide RNA sequence.
        :param usb_vendor_id: The USB vendor ID of the CRISPR kit.
        :param usb_product_id: The USB product ID of the CRISPR kit.
        :param timeout: Timeout for the USB communication.
        """
        super().__init__(guide_rna)
        self.vendor_id = usb_vendor_id
        self.product_id = usb_product_id
        self.timeout = timeout
        self.device = None
        self.endpoint_out = None
        self.endpoint_in = None
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the CRISPR kit over USB."""
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)

        if self.device is None:
            raise ValueError("Device not found")

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

        print("Connected to CRISPR kit over USB")

    def disconnect(self):
        """Close the USB connection."""
        if self.device:
            usb.util.dispose_resources(self.device)
            self.device = None
            print("Disconnected from CRISPR kit")

    def send_command(self, command: str) -> str:
        """
        Send a command to the CRISPR kit and receive a response.

        :param command: The command to send.
        :return: The response from the CRISPR kit.
        """
        if not self.device:
            raise ConnectionError("Not connected to the CRISPR kit")

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

    def execute_custom_command(self, command_name: str, *args) -> str:
        """
        Execute a custom command registered with the CRISPR kit.

        :param command_name: The name of the custom command to execute.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the CRISPR kit.
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

    def execute_edit(self, dna: 'DNA', edit_type: str, *args, occurrence: int = 1) -> 'DNA':
        """
        Perform a CRISPR edit on the DNA.

        :param dna: The DNA object to edit
        :param edit_type: The type of edit to perform ('insert', 'delete', or 'replace')
        :param args: Additional arguments specific to the edit type
        :param occurrence: The occurrence number of the guide RNA where the edit should take place (1-based index)
        :return: A new DNA object with the edit applied
        """
        target_sites = self.find_target_sequence(dna)
        if len(target_sites) < occurrence:
            print(f"Not enough target sites found for the guide RNA. Only {len(target_sites)} found.")
            return dna

        # Choose the specified target site for the edit
        edit_site = target_sites[occurrence - 1]  # 1-based index, so subtract 1

        if edit_type == 'insert':
            insert_seq = args[0]
            return self.insert_sequence(dna, insert_seq, edit_site + len(self.guide_rna))
        elif edit_type == 'delete':
            delete_length = args[0]
            return self.delete_sequence(dna, edit_site, edit_site + delete_length)
        elif edit_type == 'replace':
            replacement = args[0]
            return self.replace_sequence(dna, replacement, edit_site, edit_site + len(self.guide_rna))
        else:
            raise ValueError("Invalid edit type. Choose 'insert', 'delete', or 'replace'.")

    def simulate_off_target_effects(self, dna: 'DNA', mutation_rate: float = 0.1) -> 'DNA':
        """
        Simulate off-target effects of CRISPR editing and send the command to the CRISPR kit.

        :param dna: The DNA object to potentially modify.
        :param mutation_rate: The probability of an off-target mutation occurring.
        :return: A potentially modified DNA object.
        """
        mutated_dna = super().simulate_off_target_effects(dna, mutation_rate)

        # Notify the CRISPR kit of the off-target effects
        command = f"MUTATION:{mutation_rate}"
        response = self.send_command(command)

        print(f"CRISPR kit response: {response}")

        return mutated_dna
