import unittest
from biobridge.tools.dna_analyzer import DNAAnalyzer, MutationType


class TestDNAAnalyzer(unittest.TestCase):
    def setUp(self):
        # Mock DNA class for testing
        class MockDNA:
            def get_sequence(self, _):
                return "ATGGCCCAGCAGTGGAGCCTCCGAGGAGTGTCCATATGGTCTGAATGGAGTTGAGTGC"

        self.dna = MockDNA()
        self.analyzer = DNAAnalyzer(self.dna)

    def test_custom_marker_detection(self):
        # Add a custom marker
        self.analyzer.add_custom_marker(
            "Custom_Marker1",
            "CCGAGGAGTGT",
            MutationType.MISSENSE,
            0.6,
            "Custom Trait"
        )

        # Detect traits
        trait_probabilities, traits = self.analyzer.detect_traits()

        # Check if the custom trait is detected
        self.assertIn("Custom Trait", trait_probabilities)
        self.assertIn("Custom Trait", traits)

        # Check if the custom marker is in the detected traits
        custom_markers = [marker for marker in traits["Custom Trait"] if marker.name == "Custom_Marker1"]
        self.assertEqual(len(custom_markers), 1)

        # Check the probability of the custom trait
        self.assertGreater(trait_probabilities["Custom Trait"], 0)

    def test_multiple_custom_markers(self):
        # Add multiple custom markers
        self.analyzer.add_custom_marker(
            "Custom_Marker1",
            "CCGAGGAGTGT",
            MutationType.MISSENSE,
            0.6,
            "Custom Trait 1"
        )
        self.analyzer.add_custom_marker(
            "Custom_Marker2",
            "TGAATGGAGTT",
            MutationType.NONSENSE,
            0.8,
            "Custom Trait 2"
        )

        # Detect traits
        trait_probabilities, traits = self.analyzer.detect_traits()

        # Check if both custom traits are detected
        self.assertIn("Custom Trait 1", trait_probabilities)
        self.assertIn("Custom Trait 2", trait_probabilities)

        # Check if both custom markers are in the detected traits
        self.assertEqual(len(traits["Custom Trait 1"]), 1)
        self.assertEqual(len(traits["Custom Trait 2"]), 1)

        # Check the probabilities of the custom traits
        self.assertGreater(trait_probabilities["Custom Trait 1"], 0)
        self.assertGreater(trait_probabilities["Custom Trait 2"], 0)


if __name__ == "__main__":
    unittest.main()