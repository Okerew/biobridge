from opcua import Client
import random
from typing import List, Dict, Optional
from biobridge.blocks.tissue import Tissue


class BioreactorOpcuaManager:
    def __init__(self, ip_address: str, port: int = 4840):
        """
        Initialize the BioreactorOpcuaManager.

        :param ip_address: The IP address of the OPC UA server.
        :param port: The port number of the OPC UA server. Defaults to 4840 (OPC UA default port).
        """
        self.ip_address = ip_address
        self.port = port
        self.url = f"opc.tcp://{self.ip_address}:{self.port}"
        self.client = Client(self.url)
        self.tissues: Dict[str, Tissue] = {}
        self.nutrient_level = 100.0
        self.temperature = 37.0  # in Celsius
        self.pH = 7.4

    def connect(self):
        """Establish an OPC UA connection to the bioreactor."""
        try:
            self.client.connect()
            print(f"Connected to bioreactor at {self.url}")
        except Exception as e:
            print(f"Failed to connect to {self.url}: {e}")

    def disconnect(self):
        """Close the OPC UA connection."""
        self.client.disconnect()
        print(f"Disconnected from {self.url}")

    def send_command(self, command: str, node_id: str) -> str:
        """
        Send a command to the bioreactor and receive a response.

        :param command: The command to send.
        :param node_id: The node ID of the OPC UA object to write the command to.
        :return: The response from the bioreactor.
        """
        try:
            node = self.client.get_node(node_id)
            node.set_value(command)
            response = node.get_value()
            return response
        except Exception as e:
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

    def set_temperature(self, temperature: float, node_id: str = "ns=2;i=2"):
        """
        Set the temperature of the bioreactor.

        :param temperature: The desired temperature in Celsius.
        :param node_id: The node ID of the OPC UA object to write the command to.
        """
        command = f"SET_TEMP:{temperature:.1f}"
        response = self.send_command(command, node_id)
        if "OK" in response:
            self.temperature = temperature
            print(f"Set bioreactor temperature to {temperature:.1f}°C")
        else:
            print(f"Failed to set temperature: {response}")

    def set_pH(self, pH: float, node_id: str = "ns=2;i=3"):
        """
        Set the pH of the bioreactor.

        :param pH: The desired pH value.
        :param node_id: The node ID of the OPC UA object to write the command to.
        """
        command = f"SET_PH:{pH:.2f}"
        response = self.send_command(command, node_id)
        if "OK" in response:
            self.pH = pH
            print(f"Set bioreactor pH to {pH:.2f}")
        else:
            print(f"Failed to set pH: {response}")

    def add_nutrients(self, amount: float, node_id: str = "ns=2;i=4"):
        """
        Add nutrients to the bioreactor.

        :param amount: The amount of nutrients to add (0-100).
        :param node_id: The node ID of the OPC UA object to write the command to.
        """
        command = f"ADD_NUTRIENTS:{amount:.1f}"
        response = self.send_command(command, node_id)
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
