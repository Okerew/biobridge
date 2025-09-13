import requests


class IpBasic:
    def __init__(self, guide_rna: str, ip_address: str, port: int = 80, timeout: int = 1):
        """
        Initialize the SerialCRISPR object.

        :param guide_rna: The guide RNA sequence.
        :param ip_address: The IP address of the device.
        :param port: The port number to connect to.
        :param timeout: Timeout for the HTTP connection.
        """
        super().__init__(guide_rna)
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{self.ip_address}:{self.port}"
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the device."""
        try:
            response = requests.get(f"{self.base_url}/connect", timeout=self.timeout)
            if response.status_code == 200:
                print(f"Connected to the machine at {self.ip_address}:{self.port}")
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

    def send_command(self, command: str, endpoint: str = "command") -> str:
        """
        Send a command to the device and receive a response.

        :param command: The command to send.
        :param endpoint: The endpoint to send the command to. Defaults to "command".
        :return: The response from the machine
        """
        if command is None:
            raise ValueError("Command cannot be None.")
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")
        if endpoint is None:
            raise ValueError("Endpoint cannot be None.")
        if not isinstance(endpoint, str):
            raise TypeError("Endpoint must be a string.")

        try:
            response = requests.post(f"{self.base_url}/{endpoint}", json={"command": command}, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
            print(f"Failed to send command '{command}' to endpoint '{endpoint}': {e}")
            return ""

    def execute_custom_command(self, command_name: str, endpoint: str = "command", *args) -> str:
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

        print(f"Executing custom command: {command, endpoint}")
        return self.send_command(command, endpoint)

    def register_custom_command(self, name: str, func):
        """
        Register a custom command.

        :param name: The name of the custom command.
        :param func: A function that takes parameters and returns a command string.
        """
        if not callable(func):
            raise TypeError("Function must be callable.")
        self.custom_commands[name] = func
