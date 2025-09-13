from typing import List, Tuple

from biobridge.genes.dna import DNA


class GelElectrophoresis:
    def __init__(self, gel_length: int = 100, voltage: float = 100.0):
        self.gel_length = gel_length
        self.voltage = voltage
        self.samples = []

    def load_sample(self, dna: DNA):
        """Load a DNA sample into the gel."""
        self.samples.append(dna)

    def run_electrophoresis(self, duration: float) -> List[Tuple[DNA, int]]:
        """
        Simulate the electrophoresis process.

        :param duration: The duration of the electrophoresis in minutes
        :return: List of tuples containing the DNA samples and their positions on the gel
        """
        results = []
        for dna in self.samples:
            # Calculate migration distance based on DNA length, voltage, and duration
            migration_distance = min(
                self.gel_length, int((self.voltage * duration) / (dna.length**0.5))
            )
            results.append((dna, migration_distance))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def visualize_results(self, results: List[Tuple[DNA, int]]):
        """
        Create a simple ASCII visualization of the gel electrophoresis results.

        :param results: List of tuples containing the DNA samples and their positions
        """
        gel = [" " * self.gel_length for _ in range(len(results))]

        for i, (dna, position) in enumerate(results):
            marker = f"{dna.__len__()}bp"
            start_pos = max(0, position - len(marker) // 2)
            gel[i] = gel[i][:start_pos] + marker + gel[i][start_pos + len(marker) :]

        print("Gel Electrophoresis Results:")
        print("+" + "-" * self.gel_length + "+")
        for lane in gel:
            print(f"|{lane}|")
        print("+" + "-" * self.gel_length + "+")
        print(
            "  "
            + "".join([str(i) for i in range(0, self.gel_length, 10)]).ljust(
                self.gel_length
            )
        )
