import requests
from biobridge.genes.dna import DNA
import json


class IpDNASequencer:
    def __init__(self, ip_address: str, port: int = 80, timeout: int = 1):
        """
        Initialize the DNASequencer object.

        :param ip_address: The IP address of the DNA sequencer.
        :param port: The port number to connect to.
        :param timeout: Timeout for the HTTP connection.
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{self.ip_address}:{self.port}"
        self.custom_commands = {}

    def connect(self):
        """Establish a connection to the DNA sequencer."""
        try:
            response = requests.get(f"{self.base_url}/connect", timeout=self.timeout)
            if response.status_code == 200:
                print(f"Connected to DNA sequencer at {self.ip_address}:{self.port}")
            else:
                print(f"Failed to connect to {self.ip_address}:{self.port}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to connect to {self.ip_address}:{self.port}: {e}")

    def disconnect(self):
        """Close the connection."""
        try:
            response = requests.get(f"{self.base_url}/disconnect", timeout=self.timeout)
            if response.status_code == 200:
                print(f"Disconnected from {self.ip_address}:{self.port}")
            else:
                print(f"Failed to disconnect from {self.ip_address}:{self.port}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to disconnect from {self.ip_address}:{self.port}: {e}")

    def send_command(self, command: str) -> str:
        """
        Send a command to the DNA sequencer and receive a response.

        :param command: The command to send.
        :return: The response from the DNA sequencer.
        """
        try:
            response = requests.post(f"{self.base_url}/command", json={"command": command}, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
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
