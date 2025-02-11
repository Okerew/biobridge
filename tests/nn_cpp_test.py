import biobridge.neural_network as neural_network
import numpy as np
from biobridge.networks.system import System, Tissue

# Create a neural network
net = neural_network.NeuralNetwork(0.01, True)

# Add neurons
net.addNeuron("input1", "input", "sigmoid")
net.addNeuron("input2", "input", "sigmoid")
net.addNeuron("hidden1", "hidden", "relu")
net.addNeuron("hidden2", "hidden", "tanh")
net.addNeuron("output1", "output", "sigmoid")
net.addNeuron("output2", "output", "sigmoid")

# Add synapses
net.addSynapse("input1", "hidden1", 0.5)
net.addSynapse("input2", "hidden1", 0.3)
net.addSynapse("hidden1", "hidden2", 0.7)
net.addSynapse("hidden2", "output1", 0.4)
net.addSynapse("hidden1", "output2", 0.6)

simple_system = System("simple_system")
skin = Tissue("Skin", "epithelial")
muscle = Tissue("Muscle", "muscle")
simple_system.add_tissue(skin)
simple_system.add_tissue(muscle)

# Create a dictionary representation of the system
system_dict = {}
for tissue in simple_system.tissues:
    # Assuming the average cell health is a float value
    average_cell_health = tissue.get_average_cell_health()
    system_dict[tissue.name] = average_cell_health

net.manageSystem("simple_system", system_dict)
net.feedback_from_system(simple_system)
# Test the network
input_data = np.array([0.5, 0.7])
net.propagate(10)  # Run the network for 10 time steps
output = net.getOutput()
# Create some input data
input_data2 = {
    "feature1": 0.5,
    "feature2": 0.2,
    "feature3": 0.8
}

# Create some output data
output_data = {
    "target1": 0.7,
    "target2": 0.3
}

# Define some integer and float arguments
num_iterations = 100
learning_rate = 0.1

losses, rewards = net.train(input_data2, output_data, num_iterations, learning_rate, 0.1)
print("Training losses:", losses)
print("Training rewards:", rewards)

net.saveNetwork("simple_system.pt")

test_net = neural_network.NeuralNetwork(0.01, True)
test_net.loadNetwork("simple_system.pt")
test_net.getOutput()
net.displayNetwork()
target_output = np.array([0.8, 0.6])
for _ in range(100):
    test_net.propagate(1)
    output = test_net.getOutput()
    for name, value in output.items():
        neurons = test_net.getNeurons()
        if name in neurons:
            neurons[name].adjustThreshold(target_output[int(name[-1]) - 1])
