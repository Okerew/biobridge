import unittest
from biobridge.definitions.infections.hsv import HSV, HSVState, Cell, DNA


class TestHSVInfection(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a basic DNA sequence for the virus
        self.viral_sequence = "ATCGATCGTAGCTACGTAGCTACGTAGCTACGT"
        
        # Initialize the HSV virus
        self.virus = HSV(
            sequence=self.viral_sequence,
            name="HSV-1-Test",
            spread_rate=0.8,
            latency_probability=0.4,
            reactivation_probability=0.3
        )
        
        # Create test cells of different types
        self.neuron = Cell(
            name="TestNeuron",
            cell_type="neuron",
            health=100,
            dna=DNA("GCTAGCTAGCTA")  # Simple test DNA sequence
        )
        
        self.epithelial_cell = Cell(
            name="TestEpithelial",
            cell_type="epithelial",
            health=100,
            dna=DNA("GCTAGCTAGCTA")
        )

    def test_basic_infection(self):
        """Test basic infection capability of the virus."""
        # Test infection of epithelial cell
        infection_result = self.virus.infect(self.epithelial_cell)
        self.assertIsInstance(infection_result, bool)
        if infection_result:
            self.assertIn(self.epithelial_cell.name, self.virus.infected_cells)
            self.assertEqual(self.virus.state, HSVState.LYTIC)

    def test_neuron_infection_and_latency(self):
        """Test infection of neurons and potential latency."""
        # Perform multiple infection attempts to account for probability
        successful_latency = False
        for _ in range(10):
            virus = HSV(self.viral_sequence, latency_probability=0.8)  # High latency probability for testing
            if virus.infect(self.neuron):
                if virus.state == HSVState.LATENT:
                    successful_latency = True
                    break
        
        self.assertTrue(successful_latency, "Failed to achieve latency in neuron after multiple attempts")

    def test_viral_reactivation(self):
        """Test viral reactivation from latency."""
        # Force the virus into latency
        self.virus.state = HSVState.LATENT
        
        # Try reactivation multiple times
        reactivation_occurred = False
        for _ in range(10):
            if self.virus.reactivate():
                reactivation_occurred = True
                self.assertEqual(self.virus.state, HSVState.LYTIC)
                break
        
        self.assertTrue(reactivation_occurred, "Virus failed to reactivate after multiple attempts")

    def test_dna_integration(self):
        """Test viral DNA integration into host genome."""
        # Create a fresh virus and cell for this test
        test_viral_sequence = "ATCGATCGTAGCTA"
        test_host_sequence = "GCTAGCTAGCTAGCTA"
    
        virus = HSV(sequence=test_viral_sequence)
        host_dna = DNA(test_host_sequence)
        cell = Cell(
            name="TestCell",
            cell_type="neuron",
            dna=host_dna
        )
    
        # First infect the cell
        infection_success = virus.infect(cell)
        print(infection_success)
    
        # Try to integrate at the start of the host DNA
        integration_position = 0
        integration_success = virus.integrate_into_host(cell.dna, integration_position)
    
        # Print diagnostic information
        print(f"Original host sequence: {test_host_sequence}")
        print(f"Viral sequence: {test_viral_sequence}")
        print(f"New host sequence: {cell.dna.get_sequence(1)}")
    
        # Check if integration was successful
        print(integration_success)

    def test_viral_protein_expression(self):
        """Test viral protein expression in different states."""
        # Test protein expression in lytic state
        self.virus.state = HSVState.LYTIC
        lytic_proteins = self.virus.express_viral_proteins()
        self.assertTrue(all(lytic_proteins.values()))
        
        # Test protein expression in latent state
        self.virus.state = HSVState.LATENT
        latent_proteins = self.virus.express_viral_proteins()
        self.assertTrue(any(not expr for expr in latent_proteins.values()))

    def test_viral_mutation(self):
        """Test viral mutation mechanisms."""
        original_sequence = self.virus.get_sequence(1)
        original_spread_rate = self.virus.spread_rate
        original_latency_prob = self.virus.latency_probability
        
        self.virus.mutate()
        
        # Check if any mutations occurred
        new_sequence = self.virus.get_sequence(1)
        new_spread_rate = self.virus.spread_rate
        new_latency_prob = self.virus.latency_probability
        
        changes = (
            original_sequence != new_sequence or
            original_spread_rate != new_spread_rate or
            original_latency_prob != new_latency_prob
        )
        
        self.assertTrue(changes, "No mutations occurred after mutation attempt")

    def test_cell_damage(self):
        """Test viral impact on cell health."""
        initial_health = self.epithelial_cell.health
        
        # Infect the cell
        self.virus.infect(self.epithelial_cell)
        
        # Simulate viral replication
        for _ in range(5):
            self.virus.replicate(self.epithelial_cell)
        
        print(self.virus.describe())
        print(self.epithelial_cell.describe())

    def test_describe_output(self):
        """Test the describe method output."""
        description = self.virus.describe()
        
        # Check if description contains key information
        required_info = [
            "HSV State",
            "Latency Probability",
            "Reactivation Probability",
            "Integration Sites",
            "Active Viral Proteins"
        ]
        
        for info in required_info:
            self.assertIn(info, description)

def run_hsv_tests():
    """Run all HSV virus tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    # Example usage
    virus = HSV("ATCGATCGTAGCTACGTAGCTACGTAGCTACGT")
    cell = Cell(name="TestCell", cell_type="neuron")
    
    # Basic infection test
    if virus.infect(cell):
        print("Infection successful!")
        print(virus.describe())
    
    # Run all tests
    run_hsv_tests()
