import usb.core
import usb.util
from biobridge.genes.dna import DNA
import json


class UsbDNASequencer:
    def __init__(self, usb_vendor_id: int, usb_product_id: int, timeout: int = 1000):
        """
        Initialize the UsbDNASequencer object.

        :param usb_vendor_id: The USB vendor ID of the DNA sequencer.
        :param usb_product_id: The USB product ID of the DNA sequencer.
        :param timeout: Timeout for the USB communication (in milliseconds).
        """
        self.vendor_id = usb_vendor_id
        self.product_id = usb_product_id
        self.timeout = timeout
        self.device = None
        self.endpoint_out = None
        self.endpoint_in = None
        self.custom_commands = {}

    def connect(self):
        """Establish a connection to the DNA sequencer over USB."""
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)

        if self.device is None:
            raise ValueError("DNA sequencer not found")

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

        print("Connected to the DNA sequencer over USB")

    def disconnect(self):
        """Close the USB connection."""
        if self.device:
            usb.util.dispose_resources(self.device)
            self.device = None
            print("Disconnected from the DNA sequencer")

    def send_command(self, command: str) -> str:
        """
        Send a command to the DNA sequencer and receive a response.

        :param command: The command to send.
        :return: The response from the DNA sequencer.
        """
        if command is None:
            raise ValueError("Command cannot be None.")
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")

        if not self.device:
            raise ConnectionError("Not connected to the DNA sequencer")

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

    def get_sequence(self) -> DNA:
        """
        Retrieve the DNA sequence from the sequencer and return a DNA object.

        :return: A DNA object containing the sequenced DNA.
        """
        command = "GET_SEQUENCE"
        response = self.send_command(command)

        try:
            # Try to parse the response as JSON
            data = json.loads(response)

            # Check if the JSON contains a 'sequence' field
            if 'sequence' in data:
                dna_sequence = data['sequence']
            else:
                # If 'sequence' is not in the JSON, use the entire JSON string
                dna_sequence = response
        except json.JSONDecodeError:
            # If JSON parsing fails, use the response as a raw string
            dna_sequence = response

        # Create and return a DNA object
        return DNA(dna_sequence)

    def analyze_sequence(self, dna: DNA):
        """
        Perform various analyses on the DNA sequence.

        :param dna: The DNA object to analyze.
        """
        print("DNA Sequence Analysis:")
        print(f"Sequence length: {len(dna)}")
        print(f"GC content: {dna.gc_content():.2f}%")
        print(f"Nucleotide frequency: {dna.calculate_nucleotide_frequency()}")

        print("\nRepeats:")
        repeats = dna.find_repeats(min_length=3)
        for repeat, count in repeats.items():
            if count > 2:  # Only show repeats that occur more than twice
                print(f"  {repeat}: {count} occurrences")

        print("\nPalindromes:")
        palindromes = dna.find_palindromes(min_length=6)
        for palindrome in palindromes[:5]:  # Show the first 5 palindromes
            print(f"  {palindrome}")

        print("\nOpen Reading Frames:")
        orfs = dna.find_orfs(min_length=50)  # Find ORFs with at least 50 nucleotides
        for start, end, aa_sequence in orfs[:3]:  # Show the first 3 ORFs
            print(f"  Position {start}-{end}: {aa_sequence}")

    def run_sequencing_experiment(self):
        """
        Run a complete sequencing experiment, from connection to analysis.
        """
        try:
            self.connect()
            dna = self.get_sequence()
            print("Sequencing complete. Analyzing DNA...")
            self.analyze_sequence(dna)
        finally:
            self.disconnect()

    def execute_custom_command(self, command_name: str, *args) -> str:
        """
        Execute a custom command registered with the DNA sequencer.

        :param command_name: The name of the custom command to execute.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the DNA sequencer.
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
