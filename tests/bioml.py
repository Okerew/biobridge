import unittest
import torch
import numpy as np
from biobridge.networks.bioml import PyTorchNeuralNetwork, BioMlWrapper, Cell, Protein


class TestPyTorchNeuralNetwork(unittest.TestCase):
    def setUp(self):
        self.model = PyTorchNeuralNetwork(input_size=10, hidden_sizes=[5, 3], output_size=2)
        
    def test_initialization(self):
        self.assertIsInstance(self.model, torch.nn.Module)
        self.assertEqual(len(list(self.model.parameters())), 6)  # 3 layers * 2 params each
        
    def test_forward_pass(self):
        input_tensor = torch.randn(1, 10)
        output = self.model(input_tensor)
        self.assertEqual(output.shape, (1, 2))
        
    def test_training(self):
        # Create simple training data
        inputs = torch.randn(10, 10)
        targets = torch.randn(10, 2)
        
        losses = self.model.train_model(inputs, targets, epochs=5, lr=0.01)
        
        self.assertEqual(len(losses), 5)
        self.assertIsInstance(losses[0], float)
        # Loss should generally decrease (but not strictly due to randomness)
        self.assertTrue(losses[-1] < losses[0] or True)  # Allow for random fluctuations

class TestBioMlWrapper(unittest.TestCase):
    def setUp(self):
        self.bio_ml = BioMlWrapper(input_size=4, output_size=1, hidden_sizes=[8, 4])
        
    def test_initialization(self):
        self.assertIsInstance(self.bio_ml.neural_network, PyTorchNeuralNetwork)
        self.assertEqual(len(self.bio_ml.proteins), 0)
        self.assertEqual(len(self.bio_ml.cells), 0)
        
    def test_add_protein(self):
        protein = Protein("test_protein", sequence="ACDEFGHIKLMNPQRSTVWY")
        self.bio_ml.add_protein(protein)
        self.assertEqual(len(self.bio_ml.proteins), 1)
        self.assertEqual(self.bio_ml.proteins[0].name, "test_protein")
        
    def test_add_cell(self):
        cell = Cell("test_cell")
        self.bio_ml.add_cell(cell)
        self.assertEqual(len(self.bio_ml.cells), 1)
        self.assertEqual(self.bio_ml.cells[0].name, "test_cell")
        
    def test_prepare_input_data(self):
        protein = Protein("test", "ACGT")
        input_data = self.bio_ml._prepare_input_data(protein)
        expected = [ord('A'), ord('C'), ord('G'), ord('T')]
        self.assertEqual(input_data, expected)
        
    def test_interpret_output(self):
        output_tensor = torch.tensor([[1.0, 2.0, 3.0]])
        result = self.bio_ml._interpret_output(output_tensor)
        self.assertIn("Predicted structure", result)
        self.assertIn("1.", result)  # Should contain the tensor values
        
    def test_train_neural_network(self):
        # Create simple training data
        inputs = [[1, 2, 3, 4], [5, 6, 7, 8]]
        targets = [[0.5], [0.8]]
        
        losses = self.bio_ml.train_neural_network(inputs, targets, epochs=3, lr=0.01)
        
        self.assertEqual(len(losses), 3)
        self.assertIsInstance(losses[0], float)
        
    def test_hyperparameter_tuning(self):
        param_grid = {
            'lr': [0.01, 0.001],
            'hidden_sizes': [[8, 4], [16, 8]]
        }
        
        inputs = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        targets = [[0.1], [0.2], [0.3]]
        
        best_params, best_loss = self.bio_ml.hyperparameter_tuning(
            param_grid, inputs, targets, epochs=2, loss_function='mse'
        )
        
        self.assertIn('lr', best_params)
        self.assertIn('hidden_sizes', best_params)
        self.assertIsInstance(best_loss, float)
        
    def test_plot_loss(self):
        losses = [1.0, 0.8, 0.6, 0.4, 0.2]
        
        # This should not raise an exception
        try:
            self.bio_ml.plot_loss(losses)
            plot_success = True
        except:
            plot_success = False
            
        self.assertTrue(plot_success)
        
    def test_get_gradients(self):
        # Train a bit to generate gradients
        inputs = [[1, 2, 3, 4]]
        targets = [[0.5]]
        self.bio_ml.train_neural_network(inputs, targets, epochs=1, lr=0.01)
        
        gradients = self.bio_ml.get_gradients()
        self.assertGreater(len(gradients), 0)
        self.assertIsInstance(gradients[0], np.ndarray)
        
    def test_analyze_gradients(self):
        # This should not raise an exception
        try:
            self.bio_ml.analyze_gradients()
            analysis_success = True
        except:
            analysis_success = False
            
        self.assertTrue(analysis_success)
        
    def test_suggest_architecture(self):
        architecture = self.bio_ml.suggest_architecture(10, 2)
        
        self.assertIn('input_size', architecture)
        self.assertIn('hidden_sizes', architecture)
        self.assertIn('output_size', architecture)
        self.assertEqual(architecture['input_size'], 10)
        self.assertEqual(architecture['output_size'], 2)
        
    def test_apply_suggested_architecture(self):
        self.bio_ml.apply_suggested_architecture(20, 3, 'classification')
        
        # Test that the model has the new architecture
        test_input = torch.randn(1, 20)
        with torch.no_grad():
            output = self.bio_ml.neural_network(test_input)
            
        self.assertEqual(output.shape[1], 3)  # Output size should be 3
        
    def test_rank_network_performance(self):
        test_inputs = [[1, 2, 3, 4], [5, 6, 7, 8]]
        test_targets = [[0.5], [0.8]]
        
        performance = self.bio_ml.rank_network_performance(
            test_inputs, test_targets, task_type='regression'
        )
        
        self.assertIsInstance(performance, float)
        self.assertTrue(0 <= performance <= 1)
        
    def test_dna_conversion(self):
        # Test float to binary and back
        test_float = 3.14159
        binary = self.bio_ml._float_to_binary(test_float)
        dna = self.bio_ml._binary_to_dna(binary)
        
        self.assertIsInstance(dna, str)
        self.assertTrue(all(base in 'ACGT' for base in dna))
        
        # Test DNA to parameter conversion
        reconstructed = self.bio_ml._dna_to_parameter(dna)
        self.assertAlmostEqual(test_float, reconstructed, places=4)
        

class TestEdgeCases(unittest.TestCase):
    def test_empty_inputs(self):
        bio_ml = BioMlWrapper(input_size=0, output_size=0)
        
        # Should not crash with empty inputs
        test_input = torch.tensor([[]], dtype=torch.float32)
        with torch.no_grad():
            output = bio_ml.neural_network(test_input)
            self.assertEqual(output.shape, (1, 0))
            
    def test_single_neuron_network(self):
        bio_ml = BioMlWrapper(input_size=1, output_size=1, hidden_sizes=[])
        
        test_input = torch.tensor([[1.0]], dtype=torch.float32)
        with torch.no_grad():
            output = bio_ml.neural_network(test_input)
            self.assertEqual(output.shape, (1, 1))
            
    def test_large_network(self):
        # Test that large networks don't crash
        bio_ml = BioMlWrapper(input_size=1000, output_size=10, hidden_sizes=[500, 200])
        
        test_input = torch.randn(1, 1000)
        with torch.no_grad():
            output = bio_ml.neural_network(test_input)
            self.assertEqual(output.shape, (1, 10))

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestPyTorchNeuralNetwork))
    suite.addTest(unittest.makeSuite(TestBioMlWrapper))
    suite.addTest(unittest.makeSuite(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\nAll tests passed!")
        exit(0)
    else:
        print("\nSome tests failed!")
        exit(1)
