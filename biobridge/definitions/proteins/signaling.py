from biobridge.blocks.protein import Protein
import random


class SignalingProtein(Protein):
    def __init__(self, name, sequence, signal_type):
        super().__init__(name, sequence)
        self.signal_type = signal_type
        self.signal_strength = random.uniform(0.1, 1.0)

    def send_signal(self, cell):
        cell.receive_signal(self.signal_type, self.signal_strength)
        return f"{self.name} sent a {self.signal_type} signal with strength {self.signal_strength:.2f}"

    def interact_with_cell(self, cell):
        result = super().interact_with_cell(cell)
        signal_result = self.send_signal(cell)
        return f"{result} {signal_result}"
