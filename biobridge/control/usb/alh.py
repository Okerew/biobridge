import time
import json
import usb.core
import usb.util
from typing import List, Tuple


class UsbAutomatedLiquidHandler:
    def __init__(self, vendor_id: int, product_id: int, timeout: int = 1):
        """
        Initialize the UsbAutomatedLiquidHandler object.

        :param vendor_id: The vendor ID of the USB device.
        :param product_id: The product ID of the USB device.
        :param timeout: Timeout for the USB communication.
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.timeout = timeout
        self.device = None
        self.custom_commands = {}

    def connect(self):
        """Establish a connection to the USB device."""
        try:
            self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            if self.device is None:
                raise ValueError("Device not found")
            self.device.set_configuration()
            print(f"Connected to USB device with vendor ID {self.vendor_id} and product ID {self.product_id}")
        except Exception as e:
            print(f"Failed to connect to USB device with vendor ID {self.vendor_id} and product ID {self.product_id}: {e}")

    def disconnect(self):
        """Close the USB connection."""
        if self.device:
            usb.util.dispose_resources(self.device)
            self.device = None
            print(f"Disconnected from USB device with vendor ID {self.vendor_id} and product ID {self.product_id}")

    def send_command(self, command: str) -> str:
        """
        Send a command to the liquid handler and receive a response.

        :param command: The command to send.
        :return: The response from the liquid handler.
        """
        if not self.device:
            raise ConnectionError("Not connected to any USB device. Please connect first.")

        try:
            self.device.write(0x01, command.encode('utf-8'), timeout=self.timeout)
            time.sleep(1)  # Wait for the device to process the command
            response = self.device.read(0x81, 64, timeout=self.timeout).tobytes().decode('utf-8').strip()
            return response
        except Exception as e:
            print(f"Failed to send command to USB device with vendor ID {self.vendor_id} and product ID {self.product_id}: {e}")
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