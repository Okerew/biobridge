import logging
import struct
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell
import csv
import pickle
import matplotlib.pyplot as plt
from typing import List

class PyTorchNeuralNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_sizes: List[int] = None, output_size: int = 1):
        super(PyTorchNeuralNetwork, self).__init__()
        if hidden_sizes is None:
            hidden_sizes = [64, 32]
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        self.model = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)
    
    def train_model(self, inputs: torch.Tensor, targets: torch.Tensor, 
                   epochs: int = 100, lr: float = 0.01, 
                   loss_function: str = 'mse') -> List[float]:
        """
        Train the neural network
        """
        if loss_function == 'mse':
            criterion = nn.MSELoss()
        elif loss_function == 'cross_entropy':
            criterion = nn.CrossEntropyLoss()
        else:
            raise ValueError(f"Unsupported loss function: {loss_function}")
        
        optimizer = optim.Adam(self.parameters(), lr=lr)
        losses = []
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
            
            if epoch % 100 == 0:
                print(f'Epoch {epoch}, Loss: {loss.item()}')
        
        return losses

class BioMlWrapper:
    def __init__(self, input_size: int, output_size: int = 1, hidden_sizes: List[int] = None):
        self.neural_network = PyTorchNeuralNetwork(input_size, hidden_sizes, output_size)
        self.proteins = []
        self.cells = []
        self.logger = logging.getLogger(__name__)
        self.dna_encoding = {
            'A': '00', 'C': '01', 'G': '10', 'T': '11'
        }
        self.dna_decoding = {v: k for k, v in self.dna_encoding.items()}
        logging.basicConfig(level=logging.INFO)
        
    def add_protein(self, protein: Protein):
        self.proteins.append(protein)
        self.logger.info(f"Added protein: {protein}")
        
    def add_cell(self, cell: Cell):
        self.cells.append(cell)
        self.logger.info(f"Added cell: {cell}")
        
    def simulate_protein_interactions(self):
        for protein in self.proteins:
            protein.simulate_interactions()
            self.logger.info(f"Simulated interactions for protein: {protein}")
            
    def simulate_cell_behavior(self):
        for cell in self.cells:
            for protein in self.proteins:
                cell.interact_with_protein(protein)
            cell.metabolize()
            self.logger.info(f"Simulated behavior for cell: {cell}")
            
    def predict_protein_structure(self, protein: Protein):
        input_data = self._prepare_input_data(protein)
        input_tensor = torch.tensor(input_data, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            output_tensor = self.neural_network(input_tensor)
        predicted_structure = self._interpret_output(output_tensor)
        protein.structure = predicted_structure
        self.logger.info(f"Predicted structure for protein: {protein}")
        return predicted_structure
        
    def predict_protein_structures_batch(self, proteins: list):
        results = []
        for protein in proteins:
            result = self.predict_protein_structure(protein)
            results.append(result)
        self.logger.info(f"Predicted structures for batch of {len(proteins)} proteins")
        return results
        
    def _prepare_input_data(self, protein: Protein):
        input_data = [ord(aa) for aa in protein.sequence]
        return input_data
        
    def _interpret_output(self, output_tensor: torch.Tensor):
        predicted_structure = "Predicted structure based on output: " + str(output_tensor.numpy())
        return predicted_structure
        
    def visualize_protein_interactions(self, protein: Protein):
        protein.simulate_interactions()
        self.logger.info(f"Visualized interactions for protein: {protein}")
        
    def visualize_cell_behavior(self, cell: Cell):
        for protein in self.proteins:
            cell.interact_with_protein(protein)
        cell.metabolize()
        self.logger.info(f"Visualized behavior for cell: {cell}")
        
    def describe_simulation(self):
        for protein in self.proteins:
            print(protein)
        for cell in self.cells:
            print(cell)
        self.logger.info("Described simulation")
        
    def train_neural_network(self, inputs, targets, epochs=100, lr=0.01, loss_function='mse'):
        input_tensor = torch.tensor(inputs, dtype=torch.float32)
        target_tensor = torch.tensor(targets, dtype=torch.float32)
        
        losses = self.neural_network.train_model(input_tensor, target_tensor, epochs, lr, loss_function)
        self.logger.info(f"Trained neural network for {epochs} epochs")
        return losses
        
    def hyperparameter_tuning(self, param_grid, inputs, targets, epochs, loss_function):
        best_params = None
        best_loss = float('inf')
        
        input_tensor = torch.tensor(inputs, dtype=torch.float32)
        target_tensor = torch.tensor(targets, dtype=torch.float32)
        
        for lr in param_grid.get('lr', [0.01, 0.001]):
            for hidden_size in param_grid.get('hidden_sizes', [[64, 32], [128, 64]]):
                model = PyTorchNeuralNetwork(input_tensor.shape[1], hidden_size, target_tensor.shape[1])
                losses = model.train_model(input_tensor, target_tensor, epochs, lr, loss_function)
                final_loss = losses[-1]
                
                if final_loss < best_loss:
                    best_loss = final_loss
                    best_params = {'lr': lr, 'hidden_sizes': hidden_size}
                    self.neural_network = model
        
        self.logger.info(f"Best hyperparameters: {best_params}, Best loss: {best_loss}")
        return best_params, best_loss
        
    def export_simulation_data(self, file_path: str):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Protein', 'Cell', 'Sequence'])
            for protein in self.proteins:
                writer.writerow([protein.name, '', protein.sequence])
            for cell in self.cells:
                writer.writerow(['', cell, ''])
        self.logger.info(f"Exported simulation data to {file_path}")
        
    def import_simulation_data(self, file_path: str):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            self.proteins = []
            self.cells = []
            for row in reader:
                if row[0] and row[2]:
                    self.proteins.append(Protein(row[0], sequence=row[2]))
                if row[1]:
                    self.cells.append(Cell(row[1]))
        self.logger.info(f"Imported simulation data from {file_path}")
        
    def save_neural_network(self, file_path: str):
        torch.save(self.neural_network.state_dict(), file_path)
        self.logger.info(f"Saved neural network to {file_path}")
        
    def load_neural_network(self, file_path: str):
        self.neural_network.load_state_dict(torch.load(file_path))
        self.logger.info(f"Loaded neural network from {file_path}")
        
    def plot_loss(self, losses, title="Training Loss", xlabel="Epoch", ylabel="Loss"):
        plt.figure(figsize=(10, 6))
        plt.plot(losses)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()
        self.logger.info("Plotted training loss")
        
    def get_layer_outputs(self):
        # This would need to be implemented with hooks for PyTorch
        self.logger.warning("get_layer_outputs not implemented for PyTorch version")
        return []
        
    def get_gradients(self):
        gradients = []
        for param in self.neural_network.parameters():
            if param.grad is not None:
                gradients.append(param.grad.numpy())
        return gradients
        
    def get_parameter_history(self):
        self.logger.warning("get_parameter_history not implemented for PyTorch version")
        return []
        
    def analyze_gradients(self):
        gradients = self.get_gradients()
        if gradients:
            grad_norms = [np.linalg.norm(grad) for grad in gradients]
            self.logger.info(f"Gradient norms: {grad_norms}")
            self.logger.info(f"Average gradient norm: {np.mean(grad_norms)}")
        else:
            self.logger.warning("No gradients available for analysis")
            
    def plot_parameter_changes(self):
        self.logger.warning("plot_parameter_changes not implemented for PyTorch version")
        
    def suggest_architecture(self, input_size, output_size, task_type='classification'):
        # Simple architecture suggestion
        if task_type == 'classification':
            hidden_sizes = [64, 32]
        else:  # regression
            hidden_sizes = [128, 64]
            
        architecture = {
            'input_size': input_size,
            'hidden_sizes': hidden_sizes,
            'output_size': output_size,
            'activation': 'ReLU'
        }
        self.logger.info(f"Suggested architecture: {architecture}")
        return architecture
        
    def apply_suggested_architecture(self, input_size, output_size, task_type='classification'):
        architecture = self.suggest_architecture(input_size, output_size, task_type)
        self.neural_network = PyTorchNeuralNetwork(
            input_size, architecture['hidden_sizes'], output_size
        )
        self.logger.info("Applied suggested architecture")
        
    def train_with_suggested_architecture(self, inputs, targets, input_size, output_size, 
                                         task_type='classification', epochs=100, lr=0.01):
        self.apply_suggested_architecture(input_size, output_size, task_type)
        return self.train_neural_network(inputs, targets, epochs, lr, 
                                       'cross_entropy' if task_type == 'classification' else 'mse')
        
    def rank_network_performance(self, test_inputs, test_targets, task_type='classification'):
        input_tensor = torch.tensor(test_inputs, dtype=torch.float32)
        target_tensor = torch.tensor(test_targets, dtype=torch.float32)
        
        with torch.no_grad():
            predictions = self.neural_network(input_tensor)
            
        if task_type == 'classification':
            accuracy = (predictions.argmax(dim=1) == target_tensor.argmax(dim=1)).float().mean().item()
            performance_rank = accuracy
        else:
            mse = nn.MSELoss()(predictions, target_tensor).item()
            performance_rank = 1.0 / (1.0 + mse)  # Convert to a score between 0-1
            
        self.logger.info(f"Ranked network performance: {performance_rank}")
        return performance_rank
        
    def convert_model_to_dna(self, file_path: str, output_file: str):
        """
        Convert a trained model file into DNA sequences, considering only parameters
        that are not weights or biases.
        """
        try:
            # Load model state
            state_dict = torch.load(file_path)
            
            dna_sequences = []
            # Convert each parameter to DNA
            for param_name, param_value in state_dict.items():
                if param_value.numel() == 1:  # Single value parameters
                    param_value = param_value.item()
                    binary = self._float_to_binary(param_value)
                    dna_seq = self._binary_to_dna(binary)
                    dna_sequences.append(f"{param_name}: {dna_seq}")
            
            # Write DNA sequences to file
            with open(output_file, 'w') as f:
                f.write('\n'.join(dna_sequences))
                
            self.logger.info(f"Converted model to DNA sequences and saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error converting model to DNA: {e}")
            raise
            
    def _float_to_binary(self, f):
        """Convert a float to its binary representation."""
        return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', f))
        
    def _binary_to_dna(self, binary):
        """Convert a binary string to a DNA sequence."""
        dna = ''
        for i in range(0, len(binary), 2):
            dna += self.dna_decoding[binary[i:i + 2]]
        return dna
        
    def convert_dna_to_model(self, dna_file: str):
        """
        Convert DNA sequences back to model parameters.
        """
        try:
            with open(dna_file, 'r') as f:
                dna_sequences = f.readlines()
                
            state_dict = self.neural_network.state_dict()
            
            for dna_seq in dna_sequences:
                dna_seq = dna_seq.strip()
                if not dna_seq:
                    continue
                    
                try:
                    param_name, sequence = dna_seq.split(': ')
                    if param_name in state_dict:
                        # Convert DNA to parameter value
                        value = self._dna_to_parameter(sequence)
                        state_dict[param_name] = torch.tensor(value)
                        
                except ValueError:
                    self.logger.error(f"Invalid format in DNA sequence: {dna_seq}")
                    
            self.neural_network.load_state_dict(state_dict)
            self.logger.info(f"Converted DNA sequences to model parameters")
            
        except Exception as e:
            self.logger.error(f"Error converting DNA to model: {e}")
            raise
            
    def _dna_to_parameter(self, sequence):
        """
        Convert a DNA sequence to a parameter value.
        """
        binary = ''
        for nucleotide in sequence:
            binary += self.dna_encoding[nucleotide]
            
        while len(binary) % 8 != 0:
            binary = '0' + binary
            
        byte_data = int(binary, 2).to_bytes(len(binary) // 8, byteorder='big')
        
        try:
            if len(byte_data) == 4:
                return struct.unpack('>f', byte_data)[0]
            elif len(byte_data) == 8:
                return struct.unpack('>d', byte_data)[0]
            else:
                return int.from_bytes(byte_data, byteorder='big')
        except struct.error:
            return int.from_bytes(byte_data, byteorder='big')
            
    def save_simulation_state(self, file_path: str):
        """
        Save the current state of the simulation to a file.
        """
        state = {
            'proteins': self.proteins,
            'cells': self.cells
        }
        with open(file_path, 'wb') as f:
            pickle.dump(state, f)
        self.logger.info(f"Saved simulation state to {file_path}")
        
    def load_simulation_state(self, file_path: str):
        """
        Load the simulation state from a file.
        """
        with open(file_path, 'rb') as f:
            state = pickle.load(f)
            self.proteins = state['proteins']
            self.cells = state['cells']
        self.logger.info(f"Loaded simulation state from {file_path}")
