import json
import requests
from typing import Tuple


class IpAutomatedLiquidHandler:
    def __init__(self, ip: str, port: int = 80, timeout: int = 1):
        """
        Initialize the IpAutomatedLiquidHandler object.

        :param ip: The IP address of the liquid handler.
        :param port: The port number for the HTTP connection.
        :param timeout: Timeout for the HTTP connection.
        """
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{ip}:{port}"
        self.custom_commands = {}

    def send_command(self, command: str) -> str:
        """
        Send a command to the liquid handler and receive a response.

        :param command: The command to send.
        :return: The response from the liquid handler.
        """
        url = f"{self.base_url}/{command}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Failed to send command to {self.ip}: {e}")
            return ""

    def move_to_position(self, x: float, y: float, z: float) -> str:
        """
        Move the liquid handler to a specific position.

        :param x: X-coordinate
        :param y: Y-coordinate
        :param z: Z-coordinate
        :return: The response from the equipment
        """
        command = f"MOVE_TO/{x}/{y}/{z}"
        return self.send_command(command)

    def aspirate(self, volume: float) -> str:
        """
        Aspirate a specified volume of liquid.

        :param volume: Volume to aspirate in microliters
        :return: The response from the equipment
        """
        command = f"ASPIRATE/{volume}"
        return self.send_command(command)

    def dispense(self, volume: float) -> str:
        """
        Dispense a specified volume of liquid.

        :param volume: Volume to dispense in microliters
        :return: The response from the equipment
        """
        command = f"DISPENSE/{volume}"
        return self.send_command(command)

    def change_tip(self) -> str:
        """
        Change the current pipette tip.

        :return: The response from the equipment
        """
        command = "CHANGE_TIP"
        return self.send_command(command)

    def wash_tip(self) -> str:
        """
        Wash the current pipette tip.

        :return: The response from the equipment
        """
        command = "WASH_TIP"
        return self.send_command(command)

    def get_status(self) -> dict:
        """
        Get the current status of the liquid handler.

        :return: A dictionary containing the current status information.
        """
        command = "GET_STATUS"
        response = self.send_command(command)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

    def execute_custom_command(self, command_name: str, *args) -> str:
        """
        Execute a custom command registered with the liquid handler.

        :param command_name: The name of the custom command to execute.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the liquid handler.
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

    def run_liquid_transfer(self, source: Tuple[float, float, float], destination: Tuple[float, float, float], volume: float):
        """
        Run a complete liquid transfer operation.

        :param source: Tuple containing (x, y, z) coordinates of the source
        :param destination: Tuple containing (x, y, z) coordinates of the destination
        :param volume: Volume to transfer in microliters
        """
        try:
            print("Connected to liquid handler.")

            print("Changing tip...")
            self.change_tip()

            print(f"Moving to source position {source}...")
            self.move_to_position(*source)

            print(f"Aspirating {volume}µL...")
            self.aspirate(volume)

            print(f"Moving to destination position {destination}...")
            self.move_to_position(*destination)

            print(f"Dispensing {volume}µL...")
            self.dispense(volume)

            print("Washing tip...")
            self.wash_tip()

            print("Liquid transfer completed.")

        except Exception as e:
            print(f"An error occurred: {e}")
