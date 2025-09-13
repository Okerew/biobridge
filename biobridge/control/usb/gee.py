import time
import json
import usb.core
import usb.util


class UsbGelElectrophoresisController:
    def __init__(self, vendor_id: int, product_id: int, timeout: int = 1):
        """
        Initialize the UsbGelElectrophoresisController object.

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
        Send a command to the gel electrophoresis equipment and receive a response.

        :param command: The command to send.
        :return: The response from the gel electrophoresis equipment.
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

    def set_voltage(self, voltage: int) -> str:
        """
        Set the voltage for the gel electrophoresis run.

        :param voltage: The voltage to set (in volts).
        :return: The response from the equipment.
        """
        command = f"SET_VOLTAGE {voltage}"
        return self.send_command(command)

    def set_run_time(self, minutes: int) -> str:
        """
        Set the run time for the gel electrophoresis.

        :param minutes: The run time in minutes.
        :return: The response from the equipment.
        """
        command = f"SET_RUN_TIME {minutes}"
        return self.send_command(command)

    def start_run(self) -> str:
        """
        Start the gel electrophoresis run.

        :return: The response from the equipment.
        """
        command = "START_RUN"
        return self.send_command(command)

    def stop_run(self) -> str:
        """
        Stop the gel electrophoresis run.

        :return: The response from the equipment.
        """
        command = "STOP_RUN"
        return self.send_command(command)

    def get_status(self) -> dict:
        """
        Get the current status of the gel electrophoresis run.

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
        Execute a custom command registered with the gel electrophoresis equipment.

        :param command_name: The name of the custom command to execute.
        :param args: Arguments to pass to the custom command function.
        :return: The response from the gel electrophoresis equipment.
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

    def run_gel_electrophoresis(self, voltage: int, run_time: int):
        """
        Run a complete gel electrophoresis experiment.

        :param voltage: The voltage to set for the run (in volts).
        :param run_time: The run time (in minutes).
        """
        try:
            self.connect()
            print("Connected to gel electrophoresis equipment.")

            print(f"Setting voltage to {voltage}V...")
            self.set_voltage(voltage)

            print(f"Setting run time to {run_time} minutes...")
            self.set_run_time(run_time)

            print("Starting the run...")
            self.start_run()

            total_seconds = run_time * 60
            for i in range(total_seconds):
                status = self.get_status()
                print(f"Status: {status}")
                time.sleep(1)

                if i % 60 == 0:  # Print every minute
                    minutes_left = (total_seconds - i) // 60
                    print(f"{minutes_left} minutes remaining...")

            print("Run completed. Stopping...")
            self.stop_run()

            final_status = self.get_status()
            print(f"Final status: {final_status}")

        finally:
            self.disconnect()
