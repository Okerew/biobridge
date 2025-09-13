import time
import json
from opcua import Client, ua
from typing import Tuple


class OpcUaAutomatedLiquidHandler:
    def __init__(self, url: str, timeout: int = 1):
        """
        Initialize the OpcUaAutomatedLiquidHandler object.

        :param url: The URL of the OPC UA server.
        :param timeout: Timeout for the OPC UA connection.
        """
        self.url = url
        self.timeout = timeout
        self.client = Client(url)
        self.custom_commands = {}

    def connect(self):
        """Establish a connection to the OPC UA server."""
        try:
            self.client.connect()
            print(f"Connected to OPC UA server at {self.url}")
        except Exception as e:
            print(f"Failed to connect to OPC UA server at {self.url}: {e}")

    def disconnect(self):
        """Close the OPC UA connection."""
        self.client.disconnect()
        print(f"Disconnected from OPC UA server at {self.url}")

    def send_command(self, command: str) -> str:
        """
        Send a command to the liquid handler and receive a response.

        :param command: The command to send.
        :return: The response from the liquid handler.
        """
        try:
            command_node = self.client.get_node(f"ns=2;s={command}")
            response_node = self.client.get_node(f"ns=2;s={command}_Response")
            response_node.set_value(ua.Variant(None, ua.VariantType.Null))
            command_node.call_method(ua.Variant(None, ua.VariantType.Null))
            time.sleep(1)  # Wait for the device to process the command
            response = response_node.get_value()
            return response
        except Exception as e:
            print(f"Failed to send command to OPC UA server at {self.url}: {e}")
            return ""

    def move_to_position(self, x: float, y: float, z: float) -> str:
        """
        Move the liquid handler to a specific position.

        :param x: X-coordinate
        :param y: Y-coordinate
        :param z: Z-coordinate
        :return: The response from the equipment
        """
        command = f"MOVE_TO {x} {y} {z}"
        return self.send_command(command)

    def aspirate(self, volume: float) -> str:
        """
        Aspirate a specified volume of liquid.

        :param volume: Volume to aspirate in microliters
        :return: The response from the equipment
        """
        command = f"ASPIRATE {volume}"
        return self.send_command(command)

    def dispense(self, volume: float) -> str:
        """
        Dispense a specified volume of liquid.

        :param volume: Volume to dispense in microliters
        :return: The response from the equipment
        """
        command = f"DISPENSE {volume}"
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
            self.connect()
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

        finally:
            self.disconnect()
