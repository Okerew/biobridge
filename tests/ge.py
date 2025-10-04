import unittest
from biobridge.genes.dna import DNA
from biobridge.tools.ge import GelElectrophoresis


class TestGelElectrophoresis(unittest.TestCase):
    
    def setUp(self):
        self.gel = GelElectrophoresis(gel_length=100, voltage=100.0)
        self.dna1 = DNA("ATCGATCGATCG" * 50)
        self.dna2 = DNA("ATCG" * 100)
        self.dna3 = DNA("ATCGATCG" * 200)
        
    def test_initialization(self):
        self.assertEqual(self.gel.gel_length, 100)
        self.assertEqual(self.gel.voltage, 100.0)
        self.assertEqual(len(self.gel.samples), 0)
        self.assertFalse(self.gel.run_complete)
        
    def test_load_sample(self):
        self.gel.load_sample(self.dna1, label="Sample1")
        self.assertEqual(len(self.gel.samples), 1)
        self.assertEqual(self.gel.samples[0]['label'], "Sample1")
        
    def test_load_multiple_samples(self):
        self.gel.load_sample(self.dna1)
        self.gel.load_sample(self.dna2)
        self.gel.load_sample(self.dna3)
        self.assertEqual(len(self.gel.samples), 3)
        
    def test_clear_samples(self):
        self.gel.load_sample(self.dna1)
        self.gel.clear_samples()
        self.assertEqual(len(self.gel.samples), 0)
        self.assertFalse(self.gel.run_complete)
        
    def test_run_electrophoresis(self):
        self.gel.load_sample(self.dna1)
        self.gel.load_sample(self.dna2)
        results = self.gel.run_electrophoresis(duration=60.0)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(self.gel.run_complete)
        
    def test_migration_order(self):
        self.gel.load_sample(self.dna3, label="Long")
        self.gel.load_sample(self.dna2, label="Medium")
        self.gel.load_sample(self.dna1, label="Short")
        
        results = self.gel.run_electrophoresis(duration=60.0)
        
        short_migration = results[0][1]
        medium_migration = results[1][1]
        long_migration = results[2][1]
        
        self.assertGreater(short_migration, medium_migration)
        self.assertGreater(medium_migration, long_migration)
        
    def test_migration_within_bounds(self):
        self.gel.load_sample(self.dna1)
        results = self.gel.run_electrophoresis(duration=60.0)
        
        migration = results[0][1]
        self.assertGreaterEqual(migration, 0)
        self.assertLessEqual(migration, self.gel.gel_length)
        
    def test_set_ladder(self):
        ladder_sizes = [10000, 5000, 2500, 1000, 500]
        self.gel.set_ladder(ladder_sizes)
        self.assertEqual(len(self.gel.ladder), 5)
        self.assertEqual(self.gel.ladder[0], 10000)
        
    def test_run_without_samples(self):
        with self.assertRaises(ValueError):
            self.gel.run_electrophoresis(duration=60.0)
            
    def test_voltage_effect(self):
        gel_low = GelElectrophoresis(gel_length=100, voltage=50.0)
        gel_high = GelElectrophoresis(gel_length=100, voltage=150.0)
        
        dna = DNA("ATCG" * 100)
        gel_low.load_sample(dna)
        gel_high.load_sample(dna)
        
        results_low = gel_low.run_electrophoresis(duration=60.0)
        results_high = gel_high.run_electrophoresis(duration=60.0)
        
        self.assertLess(results_low[0][1], results_high[0][1])
        
    def test_gel_concentration_effect(self):
        gel_thin = GelElectrophoresis(
            gel_length=100, 
            gel_concentration=0.8
        )
        gel_thick = GelElectrophoresis(
            gel_length=100, 
            gel_concentration=2.0
        )
        
        dna = DNA("ATCG" * 100)
        gel_thin.load_sample(dna)
        gel_thick.load_sample(dna)
        
        results_thin = gel_thin.run_electrophoresis(duration=60.0)
        results_thick = gel_thick.run_electrophoresis(duration=60.0)
        
        self.assertGreater(results_thin[0][1], results_thick[0][1])
        
    def test_generate_report(self):
        self.gel.load_sample(self.dna1, label="Test")
        self.gel.run_electrophoresis(duration=60.0)
        report = self.gel.generate_report()
        
        self.assertIn("ELECTROPHORESIS ANALYSIS REPORT", report)
        self.assertIn("Test", report)
        self.assertIn(str(len(self.dna1.sequence)), report)
        
    def test_estimate_size_without_ladder(self):
        result = self.gel.estimate_size(50, duration=60.0)
        self.assertIsNone(result)
        
    def test_estimate_size_with_ladder(self):
        self.gel.set_ladder([10000, 5000, 2500, 1000, 500])
        estimated = self.gel.estimate_size(50, duration=60.0)
        self.assertIsNotNone(estimated)
        self.assertIsInstance(estimated, int)


if __name__ == '__main__':
    unittest.main()
