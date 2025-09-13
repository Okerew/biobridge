import re
from collections import Counter
from enum import Enum
import random


class MutationType(Enum):
    MISSENSE = 1
    NONSENSE = 2
    FRAMESHIFT = 3
    SPLICE_SITE = 4
    INVERSION = 5
    DELETION = 6
    INSERTION = 7


class GeneticMarker:
    def __init__(self, name, sequence, mutation_type, impact):
        self.name = name
        self.sequence = sequence
        self.mutation_type = mutation_type
        self.impact = impact  # Impact on trait expression (0.0 to 1.0)


class DNAAnalyzer:
    def __init__(self, dna):
        self.dna = dna
        self.hemophilia_markers = self._initialize_hemophilia_markers()
        self.color_blindness_markers = self._initialize_color_blindness_markers()
        self.custom_markers = []

    def _initialize_hemophilia_markers(self):
        return [
            GeneticMarker("F8_intron22_inv", "AGATCTACATCTGGGCTAACAAAGATATGAGATCTAG", MutationType.INVERSION, 0.8),
            GeneticMarker("F8_intron1_inv", "CTCCAGGACTTTCTGATTGCAACAGTGCCCTGTGCTCAG", MutationType.INVERSION, 0.7),
            GeneticMarker("F8_nonsense1", "TGAAGTGA", MutationType.NONSENSE, 0.9),
            GeneticMarker("F8_missense1", "GACTCGTACCTGAAGTTC", MutationType.MISSENSE, 0.5),
            GeneticMarker("F8_frameshift1", "GATCAGTCAGTCA", MutationType.FRAMESHIFT, 0.85),
            GeneticMarker("F9_missense1", "CATGAAGCTTGGCAATCC", MutationType.MISSENSE, 0.6),
            GeneticMarker("F9_splice_site1", "AGGTAAGT", MutationType.SPLICE_SITE, 0.75)
        ]

    def _initialize_color_blindness_markers(self):
        return [
            GeneticMarker("OPN1LW_deletion", "ATGGCCCAGCAGTGGAGCCT", MutationType.DELETION, 0.9),
            GeneticMarker("OPN1MW_missense1", "CCGAGGAGTGTCCATATGGTC", MutationType.MISSENSE, 0.7),
            GeneticMarker("OPN1MW_missense2", "GGTCTTCTACCTGCAAGGC", MutationType.MISSENSE, 0.6),
            GeneticMarker("OPN1SW_nonsense1", "TGAATGGAGTTGAGTGC", MutationType.NONSENSE, 0.85),
            GeneticMarker("OPN1LW_OPN1MW_hybrid", "ATGGCCCAGCAGTGGAGCCGCCGAGAAATGTCCATATGGTC", MutationType.INSERTION, 0.75)
        ]

    def analyze_gc_content(self):
        """
        Analyze GC content of the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        gc_count = sequence.count('G') + sequence.count('C')
        gc_content = (gc_count / len(sequence)) * 100
        return gc_content

    def find_cpg_islands(self, window_size=200, gc_threshold=55, obs_exp_ratio=0.65):
        """
        Find CpG islands in the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        cpg_islands = []

        for i in range(len(sequence) - window_size + 1):
            window = sequence[i:i + window_size]
            gc_content = (window.count('G') + window.count('C')) / window_size * 100
            obs_cpg = window.count('CG')
            exp_cpg = window.count('C') * window.count('G') / window_size

            if gc_content > gc_threshold and obs_cpg / exp_cpg > obs_exp_ratio:
                cpg_islands.append((i, i + window_size))

        return cpg_islands

    def find_tandem_repeats(self, min_length=2, max_length=6):
        """
        Find tandem repeats in the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        tandem_repeats = []

        for length in range(min_length, max_length + 1):
            pattern = r'(.{' + str(length) + r'})(?=\1+)'
            matches = re.finditer(pattern, sequence)
            for match in matches:
                repeat = match.group(1)
                start = match.start()
                end = start + len(repeat) * sequence[start:].count(repeat)
                tandem_repeats.append((repeat, start, end))

        return tandem_repeats

    def find_promoter_regions(self, tata_box='TATAAA', upstream_range=(-35, -25)):
        """
        Find potential promoter regions based on TATA box presence.
        """
        sequence = self.dna.get_sequence(1)
        promoter_regions = []

        for match in re.finditer(tata_box, sequence):
            tata_start = match.start()
            upstream_start = max(0, tata_start + upstream_range[0])
            promoter_regions.append((upstream_start, tata_start + len(tata_box)))

        return promoter_regions

    def analyze_codon_bias(self):
        """
        Analyze codon usage bias in the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        codons = [sequence[i:i + 3] for i in range(0, len(sequence) - 2, 3)]
        codon_counts = Counter(codons)
        total_codons = sum(codon_counts.values())

        codon_frequencies = {codon: count / total_codons for codon, count in codon_counts.items()}
        return codon_frequencies

    def find_gene_clusters(self, max_distance=1000):
        """
        Find clusters of genes that are close to each other.
        """
        genes = sorted(self.dna.get_genes(), key=lambda g: g.start)
        clusters = []
        current_cluster = []

        for i, gene in enumerate(genes):
            if not current_cluster or gene.start - genes[i - 1].end <= max_distance:
                current_cluster.append(gene)
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [gene]

        if len(current_cluster) > 1:
            clusters.append(current_cluster)

        return clusters

    def analyze_nucleotide_distribution(self, window_size=100):
        """
        Analyze the distribution of nucleotides along the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        distribution = []

        for i in range(0, len(sequence), window_size):
            window = sequence[i:i + window_size]
            counts = Counter(window)
            distribution.append({
                'start': i,
                'end': i + window_size,
                'A': counts['A'] / len(window),
                'T': counts['T'] / len(window),
                'C': counts['C'] / len(window),
                'G': counts['G'] / len(window)
            })

        return distribution

    def find_palindromic_sequences(self, min_length=4, max_length=10):
        """
        Find palindromic sequences in the DNA.
        """
        sequence = self.dna.get_sequence(1)
        palindromes = []

        for length in range(min_length, max_length + 1):
            for i in range(len(sequence) - length + 1):
                substr = sequence[i:i + length]
                if substr == substr[::-1]:
                    palindromes.append((substr, i, i + length))

        return palindromes

    def analyze_gc_skew(self, window_size=1000):
        """
        Analyze GC skew along the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        gc_skew = []

        for i in range(0, len(sequence), window_size):
            window = sequence[i:i + window_size]
            g_count = window.count('G')
            c_count = window.count('C')
            if g_count + c_count > 0:
                skew = (g_count - c_count) / (g_count + c_count)
            else:
                skew = 0
            gc_skew.append((i, i + window_size, skew))

        return gc_skew

    def predict_open_reading_frames(self, min_length=100):
        """
        Predict open reading frames (ORFs) in the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        orfs = []
        start_codon = 'ATG'
        stop_codons = ['TAA', 'TAG', 'TGA']

        for frame in range(3):
            frame_orfs = []
            for i in range(frame, len(sequence), 3):
                if sequence[i:i + 3] == start_codon:
                    for j in range(i + 3, len(sequence), 3):
                        if sequence[j:j + 3] in stop_codons:
                            if j - i >= min_length:
                                frame_orfs.append((i, j + 3))
                            break
            orfs.extend(frame_orfs)

        return orfs

    def _detect_markers(self, sequence, markers):
        detected = []
        for marker in markers:
            if marker.sequence in sequence:
                detected.append(marker)
            elif marker.mutation_type in [MutationType.DELETION, MutationType.INSERTION]:
                # For deletions and insertions, check for partial matches
                if self._partial_match(sequence, marker.sequence, 0.8):
                    detected.append(marker)
        return detected

    def _partial_match(self, sequence, marker_sequence, threshold):
        marker_length = len(marker_sequence)
        for i in range(len(sequence) - marker_length + 1):
            substring = sequence[i:i + marker_length]
            similarity = sum(a == b for a, b in zip(substring, marker_sequence)) / marker_length
            if similarity >= threshold:
                return True
        return False

    def detect_hemophilia_markers(self):
        sequence = self.dna.get_sequence(1)
        return self._detect_markers(sequence, self.hemophilia_markers)

    def detect_color_blindness_markers(self):
        sequence = self.dna.get_sequence(1)
        return self._detect_markers(sequence, self.color_blindness_markers)

    def analyze_trait_probability(self, detected_markers):
        if not detected_markers:
            return 0.0

        # Consider the impact of each detected marker
        total_impact = sum(marker.impact for marker in detected_markers)

        # Apply a probabilistic model
        probability = 1 - (1 - total_impact) ** len(detected_markers)

        # Consider epistasis (gene interactions)
        if len(detected_markers) > 1:
            probability *= 1 + (0.1 * len(detected_markers))  # Increase probability for multiple mutations

        return min(probability, 1.0)  # Ensure probability doesn't exceed 1.0

    def add_custom_marker(self, name, sequence, mutation_type, impact, trait):
        """
        Add a custom genetic marker.
        """
        marker = GeneticMarker(name, sequence, mutation_type, impact)
        self.custom_markers.append((marker, trait))

    def detect_custom_markers(self):
        """
        Detect custom markers in the DNA sequence.
        """
        sequence = self.dna.get_sequence(1)
        detected = []
        for marker, trait in self.custom_markers:
            if marker.sequence in sequence:
                detected.append((marker, trait))
            elif marker.mutation_type in [MutationType.DELETION, MutationType.INSERTION]:
                if self._partial_match(sequence, marker.sequence, 0.8):
                    detected.append((marker, trait))
        return detected

    def detect_traits(self):
        traits = {
            'Hemophilia': self.detect_hemophilia_markers(),
            'Color Blindness': self.detect_color_blindness_markers()
        }

        # Add custom markers to their respective traits
        for marker, trait in self.detect_custom_markers():
            if trait not in traits:
                traits[trait] = []
            traits[trait].append(marker)

        trait_probabilities = {
            trait: self.analyze_trait_probability(mutations)
            for trait, mutations in traits.items()
        }

        return trait_probabilities, traits

    def simulate_environmental_factors(self):
        # Simulate random environmental factors that might influence trait expression
        return {
            'Hemophilia': random.uniform(0.9, 1.1),
            'Color Blindness': random.uniform(0.95, 1.05)
        }

    def generate_trait_report(self):
        trait_probabilities, detected_traits = self.detect_traits()
        environmental_factors = self.simulate_environmental_factors()

        report = "Advanced Genetic Trait Analysis Report\n"
        report += "=====================================\n\n"

        for trait, probability in trait_probabilities.items():
            adjusted_probability = min(probability * environmental_factors[trait], 1.0)
            report += f"{trait}:\n"
            report += f"  Base Genetic Probability: {probability:.2%}\n"
            report += f"  Environmental Factor: {environmental_factors[trait]:.2f}\n"
            report += f"  Adjusted Probability: {adjusted_probability:.2%}\n"
            if detected_traits[trait]:
                report += "  Detected Markers:\n"
                for marker in detected_traits[trait]:
                    report += f"    - {marker.name} (Type: {marker.mutation_type.name}, Impact: {marker.impact:.2f})\n"
            report += "\n"

        report += "Note: This analysis is based on a complex genetic model and simulated environmental factors.\n"
        report += "It should not be used for medical diagnosis. Consult with a healthcare professional for accurate genetic testing and counseling."

        return report

    def analyze_gene_interactions(self):
        """
        Analyze potential interactions between detected genetic markers.
        """
        all_markers = self.detect_hemophilia_markers() + self.detect_color_blindness_markers()
        interactions = []

        for i, marker1 in enumerate(all_markers):
            for marker2 in all_markers[i + 1:]:
                if marker1.mutation_type == marker2.mutation_type:
                    interactions.append(
                        f"Potential interaction between {marker1.name} and {marker2.name} (both {marker1.mutation_type.name})")
                elif marker1.mutation_type in [MutationType.MISSENSE, MutationType.NONSENSE] and \
                        marker2.mutation_type in [MutationType.MISSENSE, MutationType.NONSENSE]:
                    interactions.append(
                        f"Possible compound effect: {marker1.name} ({marker1.mutation_type.name}) and {marker2.name} ({marker2.mutation_type.name})")

        return interactions

    def predict_severity(self, probability):
        """
        Predict the potential severity of a trait based on genetic probability.
        """
        if probability < 0.3:
            return "Low"
        elif probability < 0.7:
            return "Moderate"
        else:
            return "High"

    def generate_comprehensive_report(self):
        trait_probabilities, detected_traits = self.detect_traits()
        environmental_factors = self.simulate_environmental_factors()
        gene_interactions = self.analyze_gene_interactions()

        report = "Comprehensive Genetic Analysis Report\n"
        report += "======================================\n\n"

        for trait, probability in trait_probabilities.items():
            adjusted_probability = min(probability * environmental_factors[trait], 1.0)
            severity = self.predict_severity(adjusted_probability)

            report += f"{trait}:\n"
            report += f"  Base Genetic Probability: {probability:.2%}\n"
            report += f"  Environmental Factor: {environmental_factors[trait]:.2f}\n"
            report += f"  Adjusted Probability: {adjusted_probability:.2%}\n"
            report += f"  Predicted Severity: {severity}\n"
            if detected_traits[trait]:
                report += "  Detected Genetic Markers:\n"
                for marker in detected_traits[trait]:
                    report += f"    - {marker.name}:\n"
                    report += f"      Type: {marker.mutation_type.name}\n"
                    report += f"      Impact: {marker.impact:.2f}\n"
                    report += f"      Sequence: {marker.sequence}\n"
            report += "\n"

        if gene_interactions:
            report += "Potential Gene Interactions:\n"
            for interaction in gene_interactions:
                report += f"  - {interaction}\n"
            report += "\n"

        report += "Recommendations:\n"
        for trait, probability in trait_probabilities.items():
            if probability > 0.5:
                report += f"  - Consider genetic counseling for {trait}\n"
            if probability > 0.7:
                report += f"  - Regular monitoring recommended for {trait}\n"

        report += "\nDisclaimer: This analysis is based on a complex genetic model and simulated environmental factors.\n"
        report += "It should not be used for medical diagnosis. Consult with a healthcare professional for accurate genetic testing and counseling."

        return report
