import usb.core
import usb.util
import random
from typing import List, Dict, Optional
from biobridge.blocks.tissue import Tissue


class BioreactorUsbManager:
    def __init__(self, vendor_id: int, product_id: int):
        """
        Initialize the BioreactorUsbManager.

        :param vendor_id: The USB vendor ID of the bioreactor.
        :param product_id: The USB product ID of the bioreactor.
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.tissues: Dict[str, Tissue] = {}
        self.nutrient_level = 100.0
        self.temperature = 37.0  # in Celsius
        self.pH = 7.4

    def connect(self):
        """Establish a connection to the bioreactor via USB."""
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        if self.device is None:
            raise ValueError(f"Bioreactor with Vendor ID {self.vendor_id} and Product ID {self.product_id} not found.")

        try:
            self.device.set_configuration()
            print(f"Connected to bioreactor with Vendor ID {self.vendor_id} and Product ID {self.product_id}.")
        except usb.core.USBError as e:
            print(f"Failed to set USB configuration: {e}")
            self.device = None

    def disconnect(self):
        """Close the USB connection."""
        if self.device:
            usb.util.dispose_resources(self.device)
            print(f"Disconnected from bioreactor with Vendor ID {self.vendor_id} and Product ID {self.product_id}.")
            self.device = None
        else:
            print("No device connected.")

    def send_command(self, command: str) -> str:
        """
        Send a command to the bioreactor via USB and receive a response.

        :param command: The command to send.
        :return: The response from the bioreactor.
        """
        if not self.device:
            print("Device not connected.")
            return ""

        try:
            # Send command to the bioreactor (example assumes bioreactor expects ASCII commands)
            self.device.write(1, command.encode('utf-8'))
            response = self.device.read(0x81, 64)  # Example endpoint and size
            return ''.join(chr(i) for i in response)
        except usb.core.USBError as e:
            print(f"Failed to send command '{command}': {e}")
            return ""

    def add_tissue(self, tissue: Tissue):
        """
        Add a tissue to the bioreactor.

        :param tissue: The Tissue object to add.
        """
        self.tissues[tissue.name] = tissue
        print(f"Added {tissue.name} to the bioreactor.")

    def remove_tissue(self, tissue_name: str):
        """
        Remove a tissue from the bioreactor.

        :param tissue_name: The name of the tissue to remove.
        """
        if tissue_name in self.tissues:
            del self.tissues[tissue_name]
            print(f"Removed {tissue_name} from the bioreactor.")
        else:
            print(f"Tissue {tissue_name} not found in the bioreactor.")

    def set_temperature(self, temperature: float):
        """
        Set the temperature of the bioreactor.

        :param temperature: The desired temperature in Celsius.
        """
        command = f"SET_TEMP:{temperature:.1f}"
        response = self.send_command(command)
        if "OK" in response:
            self.temperature = temperature
            print(f"Set bioreactor temperature to {temperature:.1f}°C")
        else:
            print(f"Failed to set temperature: {response}")

    def set_pH(self, pH: float):
        """
        Set the pH of the bioreactor.

        :param pH: The desired pH value.
        """
        command = f"SET_PH:{pH:.2f}"
        response = self.send_command(command)
        if "OK" in response:
            self.pH = pH
            print(f"Set bioreactor pH to {pH:.2f}")
        else:
            print(f"Failed to set pH: {response}")

    def add_nutrients(self, amount: float):
        """
        Add nutrients to the bioreactor.

        :param amount: The amount of nutrients to add (0-100).
        """
        command = f"ADD_NUTRIENTS:{amount:.1f}"
        response = self.send_command(command)
        if "OK" in response:
            self.nutrient_level = min(100.0, self.nutrient_level + amount)
            print(f"Added nutrients. Current level: {self.nutrient_level:.1f}")
        else:
            print(f"Failed to add nutrients: {response}")

    def simulate_time_step(self, external_factors: Optional[List[tuple]] = None):
        """
        Simulate one time step in the bioreactor, affecting all tissues.

        :param external_factors: List of tuples (factor, intensity) to apply to tissues.
        """
        for tissue_name, tissue in self.tissues.items():
            tissue.simulate_time_step(external_factors)

            # Apply bioreactor-specific factors
            tissue.apply_external_factor("nutrient", self.nutrient_level / 100)

            # Temperature effect
            temp_factor = abs(self.temperature - 37.0) / 10  # Optimal temperature is 37°C
            tissue.apply_external_factor("temperature", temp_factor)

            # pH effect
            ph_factor = abs(self.pH - 7.4) / 2  # Optimal pH is 7.4
            tissue.apply_external_factor("pH", ph_factor)

        # Decrease nutrient level
        self.nutrient_level = max(0, int(self.nutrient_level - random.uniform(1, 5)))

        print(
            f"Bioreactor status: Temperature: {self.temperature:.1f}°C, pH: {self.pH:.2f}, Nutrient level: {self.nutrient_level:.1f}")

    def get_tissue_status(self, tissue_name: str) -> str:
        """
        Get the status of a specific tissue in the bioreactor.

        :param tissue_name: The name of the tissue to check.
        :return: A string describing the tissue status.
        """
        if tissue_name in self.tissues:
            tissue = self.tissues[tissue_name]
            return f"Tissue: {tissue_name}\n{tissue.describe()}"
        else:
            return f"Tissue {tissue_name} not found in the bioreactor."

    def get_all_tissue_status(self) -> str:
        """
        Get the status of all tissues in the bioreactor.

        :return: A string describing the status of all tissues.
        """
        status = "Bioreactor Tissue Status:\n"
        for tissue_name, tissue in self.tissues.items():
            status += f"\n{self.get_tissue_status(tissue_name)}\n"
        return status

    def run_experiment(self, duration: int, interval: int = 1):
        """
        Run a bioreactor experiment for a specified duration.

        :param duration: The total duration of the experiment in time steps.
        :param interval: The interval between status updates in time steps.
        """
        print(f"Starting bioreactor experiment for {duration} time steps.")
        for step in range(duration):
            self.simulate_time_step()

            if step % interval == 0:
                print(f"\nTime step {step + 1}:")
                print(self.get_all_tissue_status())

            # Randomly apply external factors
            if random.random() < 0.1:  # 10% chance of external factor
                factor = random.choice(["radiation", "toxin"])
                intensity = random.uniform(0, 0.5)
                print(f"Applying external factor: {factor} (intensity: {intensity:.2f})")
                self.simulate_time_step([(factor, intensity)])

            # Maintain optimal conditions
            if self.nutrient_level < 50:
                self.add_nutrients(random.uniform(10, 20))
            if abs(self.temperature - 37.0) > 1:
                self.set_temperature(37.0 + random.uniform(-0.5, 0.5))
            if abs(self.pH - 7.4) > 0.2:
                self.set_pH(7.4 + random.uniform(-0.1, 0.1))

        print("\nExperiment completed.")
        print(self.get_all_tissue_status())
