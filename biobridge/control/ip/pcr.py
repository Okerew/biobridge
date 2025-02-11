import requests
from biobridge.tools.pcr import PCR


class IpPCR(PCR):
    def __init__(self, sequence, forward_primer, reverse_primer, ip_address, port=80, timeout=1, cycles=30, mutation_rate=0.001):
        """
        Initialize the SerialPCR object.

        :param sequence: The nucleotide sequence of the DNA or RNA strand
        :param forward_primer: The forward primer sequence
        :param reverse_primer: The reverse primer sequence
        :param ip_address: The IP address of the PCR machine.
        :param port: The port number to connect to.
        :param timeout: Timeout for the HTTP connection.
        :param cycles: Number of PCR cycles (default is 30)
        :param mutation_rate: The probability of a mutation occurring at each nucleotide (default is 0.001)
        """
        super().__init__(sequence, forward_primer, reverse_primer, cycles, mutation_rate)
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{self.ip_address}:{self.port}"
        self.custom_commands = {}  # Dictionary to store custom commands

    def connect(self):
        """Establish a connection to the PCR machine."""
        try:
            response = requests.get(f"{self.base_url}/connect", timeout=self.timeout)
            if response.status_code == 200:
                print(f"Connected to PCR machine at {self.ip_address}:{self.port}")
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
        Send a command to the PCR machine and receive a response.

        :param command: The command to send.
        :return: The response from the PCR machine.
        """
        try:
            response = requests.post(f"{self.base_url}/command", json={"command": command}, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
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
