import logging
import struct
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell
from okrolearn.okrolearn import NeuralNetwork, Tensor, np
import csv
import pickle


class BioMlWrapper:
    def __init__(self, neural_network: NeuralNetwork):
        self.neural_network = neural_network
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
        input_tensor = Tensor(input_data)
        output_tensor = self.neural_network.forward(input_tensor)
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

    def _interpret_output(self, output_tensor: Tensor):
        predicted_structure = "Predicted structure based on output: " + str(output_tensor.data)
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

    def train_neural_network(self, inputs, targets, epochs, lr_scheduler, optimizer, batch_size, loss_function):
        input_tensor = Tensor(inputs)
        target_tensor = Tensor(targets)
        losses = self.neural_network.train(input_tensor, target_tensor, epochs, lr_scheduler, optimizer, batch_size, loss_function)
        self.logger.info(f"Trained neural network for {epochs} epochs")
        return losses

    def hyperparameter_tuning(self, param_grid, inputs, targets, epochs, loss_function):
        best_params, best_loss = self.neural_network.hyperparameter_tuning(param_grid, inputs, targets, epochs, loss_function)
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
        self.neural_network.save(file_path)
        self.logger.info(f"Saved neural network to {file_path}")

    def load_neural_network(self, file_path: str):
        self.neural_network.load(file_path)
        self.logger.info(f"Loaded neural network from {file_path}")

    def plot_loss(self, losses, title="Training Loss", xlabel="Epoch", ylabel="Loss"):
        self.neural_network.plot_loss(losses, title, xlabel, ylabel)
        self.logger.info("Plotted training loss")

    def get_layer_outputs(self):
        return self.neural_network.get_layer_outputs()

    def get_gradients(self):
        return self.neural_network.get_gradients()

    def get_parameter_history(self):
        return self.neural_network.get_parameter_history()

    def analyze_gradients(self):
        self.neural_network.analyze_gradients()
        self.logger.info("Analyzed gradients")

    def plot_parameter_changes(self):
        self.neural_network.plot_parameter_changes()
        self.logger.info("Plotted parameter changes")

    def set_loss_function(self, loss_function):
        self.neural_network.set_loss_function(loss_function)
        self.logger.info(f"Set loss function to {loss_function}")

    def deploy_neural_network(self, host='0.0.0.0', port=5000):
        self.neural_network.deploy(host, port)
        self.logger.info(f"Deployed neural network on {host}:{port}")

    def suggest_architecture(self, input_size, output_size, task_type='classification', data_type='tabular', depth=3, temperature=1.0):
        architecture = self.neural_network.suggest_architecture(input_size, output_size, task_type, data_type, depth, temperature)
        self.logger.info(f"Suggested architecture: {architecture}")
        return architecture

    def apply_suggested_architecture(self, input_size, output_size, task_type='classification', data_type='tabular', depth=3):
        self.neural_network.apply_suggested_architecture(input_size, output_size, task_type, data_type, depth)
        self.logger.info("Applied suggested architecture")

    def train_with_suggested_architecture(self, inputs, targets, input_size, output_size, optimizer=None, task_type='classification', data_type='tabular', depth=3, epochs=100, lr=0.01, batch_size=32):
        input_tensor = Tensor(inputs)
        target_tensor = Tensor(targets)
        losses = self.neural_network.train_with_suggested_architecture(input_tensor, target_tensor, input_size, output_size, optimizer, task_type, data_type, depth, epochs, lr, batch_size)
        self.logger.info(f"Trained with suggested architecture for {epochs} epochs")
        return losses

    def rank_network_performance(self, test_inputs, test_targets, temperature, task_type='classification', creativity_threshold=0.5):
        test_input_tensor = Tensor(test_inputs)
        test_target_tensor = Tensor(test_targets)
        performance_rank = self.neural_network.rank_network_performance(test_input_tensor, test_target_tensor, temperature, task_type, creativity_threshold)
        self.logger.info(f"Ranked network performance: {performance_rank}")
        return performance_rank

    def convert_model_to_dna(self, file_path: str, output_file: str):
        """
        Convert a trained model file into DNA sequences, considering only parameters
        that are not weights or biases.

        :param file_path: Path to the trained model file
        :param output_file: Path to save the DNA sequence output
        """
        # Load the model parameters from file
        try:
            params = np.load(file_path, allow_pickle=True)

            # Handle tuple case
            if isinstance(params, tuple):
                filtered_params = []
                for item in params:
                    if not isinstance(item, (np.ndarray, list)) or \
                            (isinstance(item, np.ndarray) and item.size == 1) or \
                            (isinstance(item, list) and len(item) == 1):
                        filtered_params.append(item)
            elif isinstance(params, np.ndarray) and params.dtype == object:
                # If it's a numpy array of objects, it might be storing the tuple
                params = params.item()
                if isinstance(params, tuple):
                    filtered_params = [
                        item for item in params
                        if not isinstance(item, (np.ndarray, list)) or
                           (isinstance(item, np.ndarray) and item.size == 1) or
                           (isinstance(item, list) and len(item) == 1)
                    ]
                else:
                    raise ValueError("Unexpected structure: numpy array does not contain a tuple")
            else:
                raise ValueError("Unexpected input structure: not a tuple or numpy array")

            # If no parameters are left after filtering, raise an exception
            if not filtered_params:
                raise ValueError("No parameters found that are not weights or biases")

        except Exception as e:
            self.logger.error(f"Error loading or processing model file: {e}")
            raise
        dna_sequences = []

        layer_params = {i: value for i, value in enumerate(filtered_params) if value is not None}

        # Iterate over the dictionary directly
        for param_value in layer_params:
            print(param_value)

            # Convert parameter to binary
            binary = self._float_to_binary(param_value)

            # Convert binary to DNA sequence
            dna_seq = self._binary_to_dna(binary)

            # Use the index as the identifier for the parameter
            dna_sequences.append(f"param_{len(dna_sequences)}: {dna_seq}")

        # Write DNA sequences to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(dna_sequences))

        self.logger.info(f"Converted model to DNA sequences and saved to {output_file}")

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
        Convert DNA sequences back to model parameters, including those that are not weights or biases.

        :param dna_file: Path to the file containing DNA sequences
        """
        with open(dna_file, 'r') as f:
            dna_sequences = f.readlines()

        parameters = {}

        for dna_seq in dna_sequences:
            dna_seq = dna_seq.strip()
            if not dna_seq:
                continue  # Skip empty lines

            try:
                name, sequence = dna_seq.split(': ')
            except ValueError:
                self.logger.error(f"Invalid format in DNA sequence: {dna_seq}")
                continue

            parts = name.split('_')

            if len(parts) >= 3 and parts[0] == 'layer':
                # Handle weights and biases
                try:
                    layer_index = int(parts[1])
                    param_type = parts[2]

                    # Validate layer index
                    if layer_index < 0 or layer_index >= len(self.neural_network.layers):
                        self.logger.error(
                            f"Layer index {layer_index} is out of range. Total layers: {len(self.neural_network.layers)}")
                        continue

                    # Convert DNA to numpy array
                    arr = self._dna_to_ndarray(sequence, self.neural_network.layers[layer_index])

                    # Set the weights or biases
                    if param_type == 'weights':
                        self.neural_network.layers[layer_index].weights = arr
                    elif param_type == 'biases':
                        self.neural_network.layers[layer_index].biases = arr
                    else:
                        self.logger.warning(f"Unknown parameter type '{param_type}' for layer {layer_index}")
                except ValueError:
                    self.logger.error(f"Invalid layer index in parameter name: {name}")
                except Exception as e:
                    self.logger.error(f"Error processing parameter {name}: {str(e)}")
            else:
                # Handle other parameters
                param_name = '_'.join(parts)

                try:
                    # Convert DNA to appropriate data type
                    value = self._dna_to_parameter(sequence)

                    # Store the parameter
                    parameters[param_name] = value
                except Exception as e:
                    self.logger.error(f"Error processing parameter {param_name}: {str(e)}")

        # Set the non-weight, non-bias parameters
        for param_name, value in parameters.items():
            try:
                setattr(self.neural_network, param_name, value)
            except Exception as e:
                self.logger.error(f"Error setting parameter {param_name}: {str(e)}")

        self.logger.info(f"Converted DNA sequences to model parameters, weights, and biases")
        self.logger.info(f"Total layers in neural network: {len(self.neural_network.layers)}")
        self.logger.info(f"Processed parameters: {list(parameters.keys())}")

    def _dna_to_parameter(self, sequence):
        """
        Convert a DNA sequence to a parameter value.
        """
        # Convert DNA to binary
        binary = ''
        for nucleotide in sequence:
            binary += self.dna_encoding[nucleotide]

        # Ensure the binary string has a length multiple of 8 (for byte conversion)
        while len(binary) % 8 != 0:
            binary = '0' + binary

        # Convert binary to bytes
        byte_data = int(binary, 2).to_bytes(len(binary) // 8, byteorder='big')

        # Try to interpret the bytes as different data types
        try:
            # Try to interpret as float (assuming 4 bytes for float32)
            if len(byte_data) == 4:
                return struct.unpack('>f', byte_data)[0]
            # Try to interpret as double (assuming 8 bytes for float64)
            elif len(byte_data) == 8:
                return struct.unpack('>d', byte_data)[0]
            # If not float, interpret as int
            else:
                return int.from_bytes(byte_data, byteorder='big')
        except struct.error:
            # If all else fails, return as int
            return int.from_bytes(byte_data, byteorder='big')

    def _dna_to_ndarray(self, dna, layer):
        """Convert a DNA sequence to a numpy array."""
        binary = self._dna_to_binary(dna)
        floats = [self._binary_to_float(binary[i:i + 32]) for i in range(0, len(binary), 32)]
        if hasattr(layer, 'weights'):
            return np.array(floats).reshape(layer.weights.shape)
        elif hasattr(layer, 'biases'):
            return np.array(floats).reshape(layer.biases.shape)

    def _dna_to_binary(self, dna):
        """Convert a DNA sequence to its binary representation."""
        return ''.join(self.dna_encoding[base] for base in dna)

    def _binary_to_float(self, binary):
        """Convert a binary string to a float."""
        return struct.unpack('!f', struct.pack('!I', int(binary, 2)))[0]

    def save_simulation_state(self, file_path: str):
        """
        Save the current state of the simulation to a file.

        :param file_path: Path to save the simulation state
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

        :param file_path: Path to load the simulation state
        """
        with open(file_path, 'rb') as f:
            state = pickle.load(f)
            self.proteins = state['proteins']
            self.cells = state['cells']
        self.logger.info(f"Loaded simulation state from {file_path}")
