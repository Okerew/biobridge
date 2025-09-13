from biobridge.blocks.tissue import Tissue, List


class Bioreactor:
    def __init__(self, name: str, capacity: int, temperature: float = 37.0, pH: float = 7.0, oxygen_level: float = 0.2):
        self.name = name
        self.capacity = capacity
        self.temperature = temperature
        self.pH = pH
        self.oxygen_level = oxygen_level
        self.tissues: List[Tissue] = []
        self.nutrient_level = 1.0
        self.waste_level = 0.0

    def add_tissue(self, tissue: Tissue) -> None:
        """Add a tissue to the bioreactor."""
        if len(self.tissues) < self.capacity:
            self.tissues.append(tissue)
        else:
            print(f"Cannot add tissue. Bioreactor {self.name} is at full capacity.")

    def remove_tissue(self, tissue: Tissue) -> None:
        """Remove a tissue from the bioreactor."""
        if tissue in self.tissues:
            self.tissues.remove(tissue)

    def adjust_temperature(self, new_temperature: float) -> None:
        """Adjust the temperature of the bioreactor."""
        self.temperature = new_temperature

    def adjust_pH(self, new_pH: float) -> None:
        """Adjust the pH of the bioreactor."""
        self.pH = new_pH

    def adjust_oxygen_level(self, new_oxygen_level: float) -> None:
        """Adjust the oxygen level of the bioreactor."""
        self.oxygen_level = new_oxygen_level

    def add_nutrients(self, amount: float) -> None:
        """Add nutrients to the bioreactor."""
        self.nutrient_level = min(1.0, self.nutrient_level + amount)

    def remove_waste(self, amount: float) -> None:
        """Remove waste from the bioreactor."""
        self.waste_level = max(0.0, self.waste_level - amount)

    def simulate_time_step(self) -> None:
        """Simulate one time step in the bioreactor's operation."""
        for tissue in self.tissues:
            # Apply bioreactor conditions to the tissue
            external_factors = [
                ("nutrient", self.nutrient_level),
                ("toxin", self.waste_level)
            ]

            # Temperature effect
            if abs(self.temperature - 37.0) > 2:
                external_factors.append(("radiation", abs(self.temperature - 37.0) / 10))

            # pH effect
            if abs(self.pH - 7.0) > 0.5:
                external_factors.append(("toxin", abs(self.pH - 7.0) / 10))

            # Oxygen level effect
            if abs(self.oxygen_level - 0.2) > 0.05:
                external_factors.append(("radiation", abs(self.oxygen_level - 0.2) * 2))

            tissue.simulate_time_step(external_factors)

        # Update bioreactor conditions
        self.nutrient_level = max(0.0, self.nutrient_level - 0.1 * len(self.tissues))
        self.waste_level = min(1.0, self.waste_level + 0.05 * len(self.tissues))

    def get_status(self) -> str:
        """Get the current status of the bioreactor."""
        status = [
            f"Bioreactor: {self.name}",
            f"Temperature: {self.temperature:.1f}°C",
            f"pH: {self.pH:.2f}",
            f"Oxygen Level: {self.oxygen_level:.2f}",
            f"Nutrient Level: {self.nutrient_level:.2f}",
            f"Waste Level: {self.waste_level:.2f}",
            f"Tissues: {len(self.tissues)}/{self.capacity}"
        ]
        return "\n".join(status)

    def __str__(self) -> str:
        """Return a string representation of the bioreactor."""
        return self.get_status()
    