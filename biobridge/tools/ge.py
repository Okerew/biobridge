from typing import List, Tuple, Optional, Dict
from biobridge.genes.dna import DNA
import math


class GelElectrophoresis:
    def __init__(
        self,
        gel_length: int = 100,
        voltage: float = 100.0,
        gel_concentration: float = 1.0,
        buffer_type: str = "TAE"
    ):
        self.gel_length = gel_length
        self.voltage = voltage
        self.gel_concentration = gel_concentration
        self.buffer_type = buffer_type
        self.samples: List[Dict] = []
        self.ladder: Optional[List[int]] = None
        self.run_complete = False
        self.results: List[Tuple[DNA, int]] = []
        
    def set_ladder(self, sizes: List[int]):
        self.ladder = sorted(sizes, reverse=True)
        
    def load_sample(
        self, 
        dna: DNA, 
        label: str = "", 
        concentration: float = 1.0
    ):
        self.samples.append({
            'dna': dna,
            'label': label or f"Sample_{len(self.samples)+1}",
            'concentration': concentration
        })
        self.run_complete = False
        
    def clear_samples(self):
        self.samples = []
        self.run_complete = False
        self.results = []
        
    def _calculate_migration(
        self, 
        dna: DNA, 
        duration: float
    ) -> int:
        dna_length = len(dna.sequence)
        gel_factor = 1.0 / (self.gel_concentration ** 0.8)
        voltage_factor = self.voltage / 100.0
        time_factor = duration / 60.0
        
        base_migration = (
            voltage_factor * 
            time_factor * 
            gel_factor * 
            100.0
        )
        
        size_resistance = math.log10(dna_length + 1) / 4.0
        migration_distance = base_migration / (1 + size_resistance)
        
        return min(self.gel_length, int(migration_distance))
        
    def run_electrophoresis(
        self, 
        duration: float
    ) -> List[Tuple[DNA, int, str]]:
        if not self.samples:
            raise ValueError("No samples loaded")
            
        self.results = []
        for sample in self.samples:
            dna = sample['dna']
            migration = self._calculate_migration(dna, duration)
            self.results.append((dna, migration, sample['label']))
            
        self.results = sorted(
            self.results, 
            key=lambda x: x[1], 
            reverse=True
        )
        self.run_complete = True
        return self.results
        
    def _calculate_ladder_positions(
        self, 
        duration: float
    ) -> List[Tuple[int, int]]:
        if not self.ladder:
            return []
            
        positions = []
        for size in self.ladder:
            gel_factor = 1.0 / (self.gel_concentration ** 0.8)
            voltage_factor = self.voltage / 100.0
            time_factor = duration / 60.0
            
            base_migration = (
                voltage_factor * 
                time_factor * 
                gel_factor * 
                100.0
            )
            
            size_resistance = math.log10(size + 1) / 4.0
            migration_distance = base_migration / (1 + size_resistance)
            migration = min(self.gel_length, int(migration_distance))
            
            positions.append((size, migration))
        return positions
        
    def visualize_results(
        self, 
        results: Optional[List[Tuple[DNA, int, str]]] = None,
        show_ladder: bool = True,
        duration: float = 60.0
    ):
        if results is None:
            if not self.run_complete:
                raise ValueError("Run electrophoresis first")
            results = self.results
            
        gel_display = []
        labels = []
        
        if show_ladder and self.ladder:
            ladder_positions = self._calculate_ladder_positions(duration)
            gel_display.append(self._create_lane(ladder_positions, True))
            labels.append("Ladder")
            
        for dna, position, label in results:
            lane = self._create_lane(
                [(len(dna.sequence), position)], 
                False
            )
            gel_display.append(lane)
            labels.append(label)
            
        self._print_gel(gel_display, labels)
        
    def _create_lane(
        self, 
        bands: List[Tuple[int, int]], 
        is_ladder: bool
    ) -> str:
        lane = [' '] * self.gel_length
        
        for size, position in bands:
            if position >= self.gel_length:
                continue
                
            marker = '═' if is_ladder else '█'
                
            if position < self.gel_length:
                lane[position] = marker
                
        return ''.join(lane)
        
    def _print_gel(self, gel_display: List[str], labels: List[str]):
        max_label_len = max(len(label) for label in labels)
        
        print("\nGel Electrophoresis Results")
        print(f"Voltage: {self.voltage}V | "
              f"Gel: {self.gel_concentration}% | "
              f"Buffer: {self.buffer_type}")
        print()
        
        print(" " * (max_label_len + 3) + "+" + "-" * self.gel_length 
              + "+")
        
        for label, lane in zip(labels, gel_display):
            padded_label = label.rjust(max_label_len)
            print(f"{padded_label} | |{lane}|")
            
        print(" " * (max_label_len + 3) + "+" + "-" * self.gel_length 
              + "+")
        
        ruler = " " * (max_label_len + 5)
        for i in range(0, self.gel_length, 10):
            ruler += str(i % 100).ljust(10)
        print(ruler[:max_label_len + 5 + self.gel_length])
        
    def estimate_size(
        self, 
        migration_distance: int, 
        duration: float = 60.0
    ) -> Optional[int]:
        if not self.ladder:
            return None
            
        ladder_positions = self._calculate_ladder_positions(duration)
        
        if migration_distance >= ladder_positions[0][1]:
            return ladder_positions[0][0]
        if migration_distance <= ladder_positions[-1][1]:
            return ladder_positions[-1][0]
            
        for i in range(len(ladder_positions) - 1):
            size1, pos1 = ladder_positions[i]
            size2, pos2 = ladder_positions[i + 1]
            
            if pos2 <= migration_distance <= pos1:
                ratio = (migration_distance - pos2) / (pos1 - pos2)
                log_size = (
                    math.log10(size2) + 
                    ratio * (math.log10(size1) - math.log10(size2))
                )
                return int(10 ** log_size)
                
        return None
        
    def generate_report(self) -> str:
        if not self.run_complete:
            return "No electrophoresis run completed"
            
        report = []
        report.append("=" * 60)
        report.append("ELECTROPHORESIS ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"\nExperimental Conditions:")
        report.append(f"  Voltage: {self.voltage}V")
        report.append(f"  Gel Concentration: {self.gel_concentration}%")
        report.append(f"  Buffer: {self.buffer_type}")
        report.append(f"  Gel Length: {self.gel_length}mm")
        report.append(f"\nSample Analysis:")
        
        for i, (dna, migration, label) in enumerate(self.results, 1):
            report.append(f"\n  {i}. {label}")
            report.append(f"     DNA Length: {len(dna.sequence)} bp")
            report.append(f"     Migration Distance: {migration} mm")
            report.append(f"     Relative Mobility: "
                         f"{migration/self.gel_length:.3f}")
            
        report.append("\n" + "=" * 60)
        return "\n".join(report)
