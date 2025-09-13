from opcua import Client
from biobridge.genes.dna import DNA
from biobridge.tools.crispr import CRISPR


class OpcuaCRISPR(CRISPR):
    def __init__(self, guide_rna: str, ip_address: str, port: int = 4840):
        """
        Initialize the OpcuaCRISPR object.

        :param guide_rna: The guide RNA sequence.
        :param ip_address: The opcua address of the CRISPR kit.
        :param port: The port number to connect to. Defaults to 4840 (OPC UA default port).
        """
        super().__init__(guide_rna)
        self.ip_address = ip_address
        self.port = port
        self.url = f"opc.tcp://{self.ip_address}:{self.port}"
        self.client = Client(self.url)
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the CRISPR kit."""
        try:
            self.client.connect()
            print(f"Connected to CRISPR kit at {self.url}")
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
        Send a command to the CRISPR kit and receive a response.

        :param command: The command to send.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: The response from the CRISPR kit.
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
        Execute a custom command registered with the CRISPR kit.

        :param command_name: The name of the custom command to execute.
        :param node_id: The node ID of the OPC UA object to write the command to.
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

    def simulate_off_target_effects(self, dna: 'DNA', mutation_rate: float = 0.1, node_id: str = "ns=2;i=2") -> 'DNA':
        """
        Simulate off-target effects of CRISPR editing and send the command to the CRISPR kit.

        :param dna: The DNA object to potentially modify.
        :param mutation_rate: The probability of an off-target mutation occurring.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: A potentially modified DNA object.
        """
        mutated_dna = super().simulate_off_target_effects(dna, mutation_rate)

        # Notify the CRISPR kit of the off-target effects
        command = f"MUTATION:{mutation_rate}"
        response = self.send_command(command, node_id)

        print(f"CRISPR kit response: {response}")

        return mutated_dna
