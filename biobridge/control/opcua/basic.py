from opcua import Client


class OpcuaBasic:
    def __init__(self, guide_rna: str, ip_address: str, port: int = 4840):
        """
        Initialize the OpcuaBasic object.

        :param guide_rna: The guide RNA sequence.
        :param ip_address: The opcua address of the device.
        :param port: The port number to connect to. Defaults to 4840 (OPC UA default port).
        """
        super().__init__(guide_rna)
        self.ip_address = ip_address
        self.port = port
        self.url = f"opc.tcp://{self.ip_address}:{self.port}"
        self.client = Client(self.url)
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the device."""
        try:
            self.client.connect()
            print(f"Connected to the machine at {self.url}")
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
        Send a command to the device and receive a response.

        :param command: The command to send.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: The response from the machine
        """
        if command is None:
            raise ValueError("Command cannot be None.")
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")
        if node_id is None:
            raise ValueError("Node ID cannot be None.")
        if not isinstance(node_id, str):
            raise TypeError("Node ID must be a string.")

        try:
            node = self.client.get_node(node_id)
            node.set_value(command)
            response = node.get_value()
            return response
        except Exception as e:
            print(f"Failed to send command '{command}' to node '{node_id}': {e}")
            return ""

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

        print(f"Executing custom command: {command, node_id}")
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
