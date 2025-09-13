import numpy as np
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell
from okrolearn.okrolearn import NeuralNetwork, CrossEntropyLoss, LearningRateScheduler, TanhActivationLayer
from biobridge.networks.bioml import BioMlWrapper
from okrolearn.optimizers import AdamOptimizer

if __name__ == "__main__":
    # Initialize neural network
    neural_network = NeuralNetwork()
    neural_network.debug_mode = True
    # Initialize wrapper
    wrapper = BioMlWrapper(neural_network)

    # Generate dummy data for training
    input_size = 20
    output_size = 10
    num_samples = 100
    inputs = np.random.rand(num_samples, input_size)
    targets = np.random.randint(0, output_size, size=(num_samples,))

    # Training parameters
    epochs = 10
    lr = 0.01
    optimizer = AdamOptimizer(lr=lr)
    batch_size = 32
    loss_function = CrossEntropyLoss()
    neural_network.add(TanhActivationLayer())

    # Train the neural network
    losses = wrapper.train_neural_network(inputs, targets, epochs, LearningRateScheduler(lr), optimizer, batch_size, loss_function)
    neural_network.save("neural_network.pkl")
    wrapper.plot_loss(losses)

    # Load the trained neural network
    wrapper.load_neural_network("neural_network.pkl")

    # Add proteins and cells
    protein1 = Protein(name="Protein1", sequence="ACDEFGHIKLMNPQRSTVWW")
    cell1 = Cell(name="Cell1", cell_type="neuron")
    wrapper.add_protein(protein1)
    wrapper.add_cell(cell1)

    # Predict protein structure
    predicted_structure = wrapper.predict_protein_structure(protein1)
    print(f"Predicted structure: {predicted_structure}")

    # Simulate protein interactions and cell behavior
    wrapper.simulate_protein_interactions()
    wrapper.simulate_cell_behavior()

    # Describe the simulation
    wrapper.describe_simulation()

    # Describe the loaded simulation
    wrapper.describe_simulation()

    wrapper.save_simulation_state("simulation_state.pkl")

    # Convert the current model to DNA
    wrapper.convert_model_to_dna("neural_network.pkl", "model_dna.txt")

    # Convert DNA back to model weights and biases
    wrapper.convert_dna_to_model('model_dna.txt')
