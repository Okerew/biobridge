from opcua import Client
from biobridge.genes.dna import DNA
import json


class DNASequencerOpcua:
    def __init__(self, ip_address: str, port: int = 4840):
        """
        Initialize the DNASequencerOpcua object.

        :param ip_address: The IP address of the OPC UA server.
        :param port: The port number of the OPC UA server. Defaults to 4840 (OPC UA default port).
        """
        self.ip_address = ip_address
        self.port = port
        self.url = f"opc.tcp://{self.ip_address}:{self.port}"
        self.client = Client(self.url)
        self.custom_commands = {}

    def connect(self):
        """Establish an OPC UA connection to the DNA sequencer."""
        try:
            self.client.connect()
            print(f"Connected to DNA sequencer at {self.url}")
        except Exception as e:
            print(f"Failed to connect to {self.url}: {e}")

    def disconnect(self):
        """Close the OPC UA connection."""
        self.client.disconnect()
        print(f"Disconnected from {self.url}")

    def send_command(self, command: str, node_id: str) -> str:
        """
        Send a command to the DNA sequencer and receive a response.

        :param command: The command to send.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: The response from the DNA sequencer.
        """
        try:
            node = self.client.get_node(node_id)
            node.set_value(command)
            response = node.get_value()
            return response
        except Exception as e:
            print(f"Failed to send command '{command}': {e}")
            return ""

    def get_sequence(self, node_id: str = "ns=2;i=2") -> DNA:
        """
        Retrieve the DNA sequence from the sequencer and return a DNA object.

        :param node_id: The node ID of the OPC UA object to read the sequence from.
        :return: A DNA object containing the sequenced DNA.
        """
        command = "GET_SEQUENCE"
        response = self.send_command(command, node_id)

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
