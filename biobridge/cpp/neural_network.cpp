#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <nlohmann/json.hpp>
#include <random>
#include <set>
#include <sstream>
#include <vector>

namespace py = pybind11;
using json = nlohmann::json;

class Synapse;

class Neuron {
 public:
  Neuron(const std::string& name, const std::string& type,
         const std::string& activation_function)
      : name(name), type(type), activation_function(activation_function) {
    threshold = static_cast<float>(rand()) / RAND_MAX * (0.7 - 0.3) + 0.3;
    activation = 0.0f;
    output = 0.0f;
    fired = false;
    learning_rate = 0.01f;
    refractory_period = 0;
    last_spike_time = 0;
    useBias = true;
    bias = static_cast<float>(rand()) / RAND_MAX * 0.2f - 0.1f;
    delta = 0.0f;
  }

  bool activate(int currentTime) {
    if (refractory_period > 0) {
      refractory_period--;
      return false;
    }

    if (activation_function == "sigmoid") {
      output = 1.0f / (1.0f + std::exp(-activation));
    } else if (activation_function == "relu") {
      output = std::max(0.0f, activation);
    } else if (activation_function == "tanh") {
      output = std::tanh(activation);
    }

    if (output >= threshold) {
      fired = true;
      last_spike_time = currentTime;
      refractory_period = 5;
      activation = 0.0f;
      return true;
    }
    return false;
  }

  float activationDerivative() const {
    if (activation_function == "sigmoid") {
      return output * (1.0f - output);
    } else if (activation_function == "relu") {
      return activation > 0 ? 1.0f : 0.0f;
    } else if (activation_function == "tanh") {
      return 1.0f - output * output;
    }
    return 0.0f;
  }

  void reset() {
    activation = 0.0f;
    output = 0.0f;
    fired = false;
  }

  void adjustThreshold(float target) {
    threshold += learning_rate * (target - threshold);
  }

  void updateWeights(float reward);
  std::string name;
  std::string type;
  std::string activation_function;
  float threshold;
  float activation;
  float output;
  bool fired;
  float learning_rate;
  std::vector<Synapse*> dendrites;
  std::vector<Synapse*> axons;
  int refractory_period;
  int last_spike_time;
  bool useBias;
  float bias;
  float delta;
  float depth;
  std::map<std::string, float> weights;
  std::map<std::string, float> outgoingConnections;
  void calculateDelta(float target);
};

// Declaration for layers
std::map<std::string, std::vector<Neuron*>> layers;

// Helper function to get layer order
std::vector<std::string> getLayerOrder() {
  std::vector<std::string> order;
  order.reserve(layers.size());
  for (const auto& [layerName, neurons] : layers) {
    order.push_back(layerName);
  }
  std::sort(order.begin(), order.end(),
            [](const std::string& a, const std::string& b) {
              return layers[a][0]->depth < layers[b][0]->depth;
            });
  return order;
}

class Synapse {
 public:
  Synapse(Neuron* preNeuron, Neuron* postNeuron, float weight = 0.0f)
      : preNeuron(preNeuron),
        postNeuron(postNeuron),
        weight(weight != 0.0f
                   ? weight
                   : static_cast<float>(rand()) / RAND_MAX * 2.0f - 1.0f) {
    plasticity = 0.1f;
    eligibilityTrace = 0.0f;
  }

  void transmit() {
    if (preNeuron->fired) {
      postNeuron->activation += weight * preNeuron->output;
    }
  }

  void adjustWeight(float reward) {
    float delta = reward * eligibilityTrace;
    weight += delta * plasticity;
    weight = std::max(-1.0f, std::min(1.0f, weight));
    eligibilityTrace *= 0.9f;  // Decay eligibility trace
  }

  Neuron* preNeuron;
  Neuron* postNeuron;
  Neuron* presynaptic_neuron;
  Neuron* postsynaptic_neuron;
  float weight;
  float plasticity;
  float eligibilityTrace;
};

void Neuron::updateWeights(float reward) {
  for (auto& synapse : dendrites) {
    synapse->weight +=
        learning_rate * reward * synapse->presynaptic_neuron->output;
  }
  if (useBias) {
    bias += learning_rate * reward;
  }
}

void Neuron::calculateDelta(float target) {
  if (type == "output") {
    delta = (target - output) * activationDerivative();
  } else {
    delta = 0.0f;
    for (const auto& synapse : axons) {
      delta += synapse->weight * synapse->postNeuron->delta;
    }
    delta *= activationDerivative();
  }
}

py::object import_system_class() {
  py::module_ sys_module = py::module_::import("biobridge.networks.system");
  return sys_module.attr("System");
}

class NeuralNetwork {
 public:
  NeuralNetwork(float learningRate = 0.01f, bool debug = false)
      : lr(learningRate), debug(debug) {}

  ~NeuralNetwork() {
    // Ensure proper cleanup
    neurons.clear();
    synapses.clear();
  }

  float getLearningRate() const { return lr; }
  void setLearningRate(float newLr) { lr = newLr; }
  bool getDebug() const { return debug; }
  void setDebug(bool newDebug) { debug = newDebug; }
  std::map<std::string, Neuron*> getNeurons() const {
    std::map<std::string, Neuron*> result;
    for (const auto& kv : neurons) {
      result[kv.first] = kv.second.get();
    }
    return result;
  }

  void addNeuron(const std::string& name, const std::string& type = "hidden",
                 const std::string& activationFunction = "sigmoid") {
    neurons[name] =
        std::unique_ptr<Neuron>(new Neuron(name, type, activationFunction));
    if (type == "input") {
      inputNeurons.insert(name);
    } else if (type == "output") {
      if (debug) {
        std::cout << "Adding output neuron: " << name << std::endl;
      }
      outputNeurons.insert(name);
    }
  }
  void addSynapse(const std::string& preNeuronName,
                  const std::string& postNeuronName, float weight = 0.0f) {
    Neuron* preNeuron = neurons[preNeuronName].get();
    Neuron* postNeuron = neurons[postNeuronName].get();
    synapses.emplace_back(new Synapse(preNeuron, postNeuron, weight));
    preNeuron->axons.push_back(synapses.back().get());
    postNeuron->dendrites.push_back(synapses.back().get());
  }

  void propagate(int steps = 5) {
    for (int _ = 0; _ < steps; ++_) {
      timeStep++;
      for (const auto& neuron : neurons) {
        neuron.second->activate(timeStep);
        if (debug) {
          std::cout << "Neuron " << neuron.first << " activated with output "
                    << neuron.second->output << std::endl;
        }
      }

      for (const auto& synapse : synapses) {
        synapse->transmit();
        if (debug) {
          std::cout << "Synapse from " << synapse->preNeuron->name << " to "
                    << synapse->postNeuron->name << " transmitted with weight "
                    << synapse->weight << std::endl;
        }
      }

      applySTDP();
    }
  }

  std::map<std::string, float> getOutput() {
    std::map<std::string, float> output;
    for (const auto& neuronName : outputNeurons) {
      output[neuronName] = neurons[neuronName]->output;
    }
    if (debug) {
      std::stringstream ss;
      ss << "Network output: ";
      for (const auto& [name, value] : output) {
        ss << name << ": " << value << ", ";
      }
      std::cout << ss.str() << std::endl;
    }
    return output;
  }

  void resetNetwork() {
    for (auto& neuron : neurons) {
      neuron.second->reset();
    }
    timeStep = 0;
  }

  void backpropagate(const std::map<std::string, float>& outputErrors,
                     float learningRate) {
    // Start with output layer
    for (const auto& [outputName, error] : outputErrors) {
      auto& neuron = neurons[outputName];
      neuron->delta = error * neuron->activationDerivative();

      // Update weights for this neuron
      for (auto& synapse : neuron->dendrites) {
        float weightUpdate =
            learningRate * neuron->delta * synapse->preNeuron->output;
        synapse->weight += weightUpdate;
      }
    }

    // Propagate error back through hidden layers
    for (auto& [name, neuron] : neurons) {
      if (neuron->type != "output") {
        neuron->delta = 0.0f;
        for (const auto& synapse : neuron->axons) {
          neuron->delta += synapse->weight * synapse->postNeuron->delta;
        }
        neuron->delta *= neuron->activationDerivative();

        // Update weights for this neuron
        for (auto& synapse : neuron->dendrites) {
          float weightUpdate =
              learningRate * neuron->delta * synapse->preNeuron->output;
          synapse->weight += weightUpdate;
        }
      }
    }
  }

  std::string normalizeKey(const std::string& key) {
    std::string normalizedKey = key;
    normalizedKey.erase(
        std::remove_if(normalizedKey.begin(), normalizedKey.end(), ::isspace),
        normalizedKey.end());
    std::transform(normalizedKey.begin(), normalizedKey.end(),
                   normalizedKey.begin(), ::tolower);
    return normalizedKey;
  }

  py::tuple train(const std::map<std::string, float>& inputs,
                  const std::map<std::string, float>& targetOutputs, int epochs,
                  float learningRate = 0.01f, float gamma = 0.9f) {
    py::gil_scoped_release release;
    try {
      std::vector<float> epochLosses;
      std::vector<float> epochRewards;

      if (debug) {
        std::cout << "Starting training with " << epochs << " epochs."
                  << std::endl;
      }

      for (int epoch = 0; epoch < epochs; epoch++) {
        if (debug) {
          std::cout << "Entering epoch " << epoch + 1 << "/" << epochs
                    << std::endl;
        }

        float epochLoss = 0.0f;
        float epochReward = 0.0f;

        resetNetwork();

        // Set input activations
        for (const auto& [inputName, value] : inputs) {
          auto it = neurons.find(inputName);
          if (it != neurons.end() && it->second->type == "input") {
            it->second->activation = value;
          }
        }

        // Forward propagation
        propagate();

        std::map<std::string, float> currentOutputs = getOutput();

        if (debug) {
          std::cout << "Current outputs:" << std::endl;
          for (const auto& [outputName, value] : currentOutputs) {
            std::cout << outputName << ": " << value << std::endl;
          }
        }

        // Calculate loss and prepare for backpropagation
        std::map<std::string, float> outputErrors;
        for (const auto& [outputName, targetValue] : targetOutputs) {
          std::string normalizedOutputName = normalizeKey(outputName);
          auto it = std::find_if(
              currentOutputs.begin(), currentOutputs.end(),
              [this, &normalizedOutputName](
                  const std::pair<std::string, float>& element) {
                return normalizeKey(element.first) == normalizedOutputName;
              });

          if (it != currentOutputs.end()) {
            float error = targetValue - it->second;
            outputErrors[outputName] = error;
            if (debug) {
              std::cout << "Output: " << outputName
                        << ", Target: " << targetValue
                        << ", Current: " << it->second << ", Error: " << error
                        << std::endl;
            }
            epochLoss += std::pow(error, 2);
            epochReward -= std::abs(error);
          } else {
            if (debug) {
              std::cout << "Warning: Output '" << outputName
                        << "' not found in current outputs." << std::endl;
            }
          }
        }

        epochLoss /= targetOutputs.size();
        std::cout << "targetOutputs: " << targetOutputs.size() << std::endl;
        // Backpropagation
        backpropagate(outputErrors, learningRate);

        // Apply STDP and other adaptations
        applySTDP();
        adapt_to_feedback();

        epochLosses.push_back(epochLoss);
        epochRewards.push_back(epochReward);

        if (debug) {
          std::cout << "Epoch " << epoch + 1 << "/" << epochs
                    << ", Loss: " << epochLoss << ", Reward: " << epochReward
                    << std::endl;
        }
      }

      py::gil_scoped_acquire acquire;
      return py::make_tuple(epochLosses, epochRewards);
    } catch (const std::exception& e) {
      py::gil_scoped_acquire acquire;
      throw py::value_error(std::string("Error in train method: ") + e.what());
    }
  }

  void displayNetwork() const {
    py::gil_scoped_acquire acquire;
    try {
        py::module_ networkx = py::module_::import("networkx");
        py::module_ matplotlib = py::module_::import("matplotlib.pyplot");

        py::object G = networkx.attr("DiGraph")();

        for (const auto& neuron : neurons) {
            G.attr("add_node")(neuron.first);
        }

        for (const auto& synapse : synapses) {
            G.attr("add_edge")(synapse->preNeuron->name, synapse->postNeuron->name,
                               py::arg("weight") = synapse->weight);
        }

        py::object pos = networkx.attr("spring_layout")(G, py::arg("k") = 0.5, py::arg("iterations") = 50);
        py::object labels = networkx.attr("get_edge_attributes")(G, "weight");

        matplotlib.attr("figure")(py::arg("figsize") = py::make_tuple(12, 8));

        networkx.attr("draw")(
            G, pos, py::arg("with_labels") = true, py::arg("node_size") = 1500,
            py::arg("node_color") = "skyblue", py::arg("node_shape") = "o",
            py::arg("alpha") = 0.7, py::arg("linewidths") = 1.5);

        networkx.attr("draw_networkx_edge_labels")(G, pos,
                                                   py::arg("edge_labels") = labels,
                                                   py::arg("font_size") = 8);

        matplotlib.attr("show")();
    } catch (const std::exception& e) {
            std::cerr << "Error in displayNetwork: " << e.what() << std::endl;
        }
    }


  void manageSystem(const std::string& systemName,
                    const std::map<std::string, float>& networkOutput) {
    py::object System = import_system_class();
    py::object systemInstance = System(systemName);

    // Convert networkOutput to a Python dictionary
    py::dict networkOutputDict;
    for (const auto& [key, value] : networkOutput) {
      networkOutputDict[py::str(key)] = value;
    }

    // Call the update method on the System instance
    systemInstance.attr("update")(networkOutputDict);
  }

  void adapt_to_feedback() {
    for (const auto& kv : neurons) {
      Neuron* neuron = kv.second.get();
      if (neuron->fired) {
        neuron->adjustThreshold(0.9f * neuron->threshold);
      } else {
        neuron->adjustThreshold(1.1f * neuron->threshold);
      }
      if (debug) {
        std::cout << "Adjusting threshold of neuron " << neuron->name << " to "
                  << neuron->threshold << std::endl;
      }
    }
  }

  void feedback_from_system(py::object systemInstance) {
    // Get the status from the System instance
    float status = systemInstance.attr("get_status")().cast<float>();

    // Create input signals based on the status
    std::map<std::string, float> inputSignals;
    for (const auto& neuronName : inputNeurons) {
      inputSignals[neuronName] = status;
    }

    // Call the stimulate method with the input signals
    stimulate(inputSignals);

    std::cout << "Status: " << status << std::endl;
  }

  void stimulate(const std::map<std::string, float>& inputSignals) {
    for (const auto& [neuronName, signal] : inputSignals) {
      if (inputNeurons.find(neuronName) != inputNeurons.end()) {
        neurons[neuronName]->activation = signal;
      }
    }
  }

  void saveNetwork(const std::string& filename) const {
    std::ofstream file(filename, std::ios::binary);
    if (file.is_open()) {
      // Write learning rate and debug flag
      file.write(reinterpret_cast<const char*>(&lr), sizeof(lr));
      file.write(reinterpret_cast<const char*>(&debug), sizeof(debug));

      // Write neuron data
      size_t numNeurons = neurons.size();
      file.write(reinterpret_cast<const char*>(&numNeurons),
                 sizeof(numNeurons));
      for (const auto& kv : neurons) {
        const Neuron* neuron = kv.second.get();
        size_t nameLength = kv.first.length();
        file.write(reinterpret_cast<const char*>(&nameLength),
                   sizeof(nameLength));
        file.write(kv.first.c_str(), nameLength);
        file.write(reinterpret_cast<const char*>(&neuron->type),
                   sizeof(neuron->type));
        file.write(reinterpret_cast<const char*>(&neuron->activation_function),
                   sizeof(neuron->activation_function));
        file.write(reinterpret_cast<const char*>(&neuron->threshold),
                   sizeof(neuron->threshold));
        file.write(reinterpret_cast<const char*>(&neuron->learning_rate),
                   sizeof(neuron->learning_rate));
      }

      // Write synapse data
      size_t numSynapses = synapses.size();
      file.write(reinterpret_cast<const char*>(&numSynapses),
                 sizeof(numSynapses));
      for (const auto& synapse : synapses) {
        file.write(reinterpret_cast<const char*>(&synapse->preNeuron->name),
                   sizeof(synapse->preNeuron->name));
        file.write(reinterpret_cast<const char*>(&synapse->postNeuron->name),
                   sizeof(synapse->postNeuron->name));
        file.write(reinterpret_cast<const char*>(&synapse->weight),
                   sizeof(synapse->weight));
        file.write(reinterpret_cast<const char*>(&synapse->plasticity),
                   sizeof(synapse->plasticity));
      }

      file.close();
    } else {
      std::cerr << "Unable to open file: " << filename << std::endl;
    }
  }

  void loadNetwork(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (file.is_open()) {
      // Read learning rate and debug flag
      file.read(reinterpret_cast<char*>(&lr), sizeof(lr));
      file.read(reinterpret_cast<char*>(&debug), sizeof(debug));

      // Read neuron data
      size_t numNeurons;
      file.read(reinterpret_cast<char*>(&numNeurons), sizeof(numNeurons));
      neurons.clear();
      inputNeurons.clear();
      outputNeurons.clear();
      for (size_t i = 0; i < numNeurons; ++i) {
        size_t nameLength;
        file.read(reinterpret_cast<char*>(&nameLength), sizeof(nameLength));
        std::string name(nameLength, '\0');
        file.read(&name[0], nameLength);
        std::string type;
        std::string activationFunction;
        float threshold;
        float learningRate;
        file.read(reinterpret_cast<char*>(&type), sizeof(type));
        file.read(reinterpret_cast<char*>(&activationFunction),
                  sizeof(activationFunction));
        file.read(reinterpret_cast<char*>(&threshold), sizeof(threshold));
        file.read(reinterpret_cast<char*>(&learningRate), sizeof(learningRate));
        addNeuron(name, type, activationFunction);
        neurons[name]->threshold = threshold;
        neurons[name]->learning_rate = learningRate;
      }

      // Read synapse data
      size_t numSynapses;
      file.read(reinterpret_cast<char*>(&numSynapses), sizeof(numSynapses));
      synapses.clear();
      for (size_t i = 0; i < numSynapses; ++i) {
        std::string preNeuronName;
        std::string postNeuronName;
        float weight;
        float plasticity;
        file.read(reinterpret_cast<char*>(&preNeuronName),
                  sizeof(preNeuronName));
        file.read(reinterpret_cast<char*>(&postNeuronName),
                  sizeof(postNeuronName));
        file.read(reinterpret_cast<char*>(&weight), sizeof(weight));
        file.read(reinterpret_cast<char*>(&plasticity), sizeof(plasticity));
        addSynapse(preNeuronName, postNeuronName, weight);
        for (const auto& synapse : synapses) {
          if (synapse->preNeuron->name == preNeuronName &&
              synapse->postNeuron->name == postNeuronName) {
            synapse->plasticity = plasticity;
            break;
          }
        }
      }

      file.close();
    } else {
      std::cerr << "Unable to open file: " << filename << std::endl;
    }
  }

  py::dict toJson() const {
    py::gil_scoped_acquire acquire;
    try {
        json j;
        j["learning_rate"] = lr;
        j["debug"] = debug;
        j["neurons"] = json::array();

        for (const auto& kv : neurons) {
            json neuronJson;
            neuronJson["name"] = kv.first;
            neuronJson["type"] = kv.second->type;
            neuronJson["activation_function"] = kv.second->activation_function;
            neuronJson["threshold"] = kv.second->threshold;
            neuronJson["learning_rate"] = kv.second->learning_rate;
            j["neurons"].push_back(neuronJson);
        }

        j["synapses"] = json::array();
        for (const auto& synapse : synapses) {
            json synapseJson;
            synapseJson["preNeuron"] = synapse->preNeuron->name;
            synapseJson["postNeuron"] = synapse->postNeuron->name;
            synapseJson["weight"] = synapse->weight;
            synapseJson["plasticity"] = synapse->plasticity;
            j["synapses"].push_back(synapseJson);
        }

        return py::cast(j);
    } catch (const std::exception& e) {
            std::cerr << "Error in toJson: " << e.what() << std::endl;
            return py::dict();
        }
    }

  void fromJson(const py::dict& pyDict) {
    py::gil_scoped_acquire acquire;
    try {
        json j = py::cast<json>(pyDict);

        lr = j["learning_rate"].get<float>();
        debug = j["debug"].get<bool>();
        neurons.clear();
        synapses.clear();
        inputNeurons.clear();
        outputNeurons.clear();

        for (const auto& neuronJson : j["neurons"]) {
            std::string name = neuronJson["name"].get<std::string>();
            std::string type = neuronJson["type"].get<std::string>();
            std::string activation_function = neuronJson["activation_function"].get<std::string>();

            addNeuron(name, type, activation_function);
            neurons[name]->threshold = neuronJson["threshold"].get<float>();
            neurons[name]->learning_rate = neuronJson["learning_rate"].get<float>();
        }

        for (const auto& synapseJson : j["synapses"]) {
            std::string preNeuron = synapseJson["preNeuron"].get<std::string>();
            std::string postNeuron = synapseJson["postNeuron"].get<std::string>();
            float weight = synapseJson["weight"].get<float>();

            addSynapse(preNeuron, postNeuron, weight);

            for (const auto& synapse : synapses) {
                if (synapse->preNeuron->name == preNeuron &&
                    synapse->postNeuron->name == postNeuron) {
                    synapse->plasticity = synapseJson["plasticity"].get<float>();
                    break;
                }
            }
        }
    }   catch (const std::exception& e) {
            std::cerr << "Error in fromJson: " << e.what() << std::endl;
        }
    }

 private:
  void applySTDP() {
    for (const auto& synapse : synapses) {
      int preSpike = synapse->preNeuron->last_spike_time;
      int postSpike = synapse->postNeuron->last_spike_time;
      if (preSpike > 0 && postSpike > 0) {
        int timeDiff = postSpike - preSpike;
        if (timeDiff >= -20 && timeDiff <= 20) {
          float delta = timeDiff > 0 ? 0.1f * std::exp(-timeDiff / 10.0f)
                                     : -0.1f * std::exp(timeDiff / 10.0f);
          synapse->adjustWeight(delta);
          if (debug) {
            std::cout << "Adjusting synapse weight from "
                      << synapse->preNeuron->name << " to "
                      << synapse->postNeuron->name << " by " << delta
                      << std::endl;
          }
        }
      }
    }
  }

  std::map<std::string, std::unique_ptr<Neuron>> neurons;
  std::vector<std::unique_ptr<Synapse>> synapses;
  std::set<std::string> inputNeurons;
  std::set<std::string> outputNeurons;
  int timeStep = 0;
  float lr;
  bool debug;
};

PYBIND11_MODULE(neural_network, m) {
  py::class_<Neuron>(m, "Neuron")
      .def(py::init<const std::string&, const std::string&,
                    const std::string&>())
      .def("activate", &Neuron::activate)
      .def("reset", &Neuron::reset)
      .def("adjustThreshold", &Neuron::adjustThreshold)
      .def_readwrite("name", &Neuron::name)
      .def_readwrite("type", &Neuron::type)
      .def_readwrite("activation_function", &Neuron::activation_function)
      .def_readwrite("threshold", &Neuron::threshold)
      .def_readwrite("activation", &Neuron::activation)
      .def_readwrite("output", &Neuron::output)
      .def_readwrite("fired", &Neuron::fired)
      .def_readwrite("learning_rate", &Neuron::learning_rate)
      .def_readwrite("dendrites", &Neuron::dendrites)
      .def_readwrite("axons", &Neuron::axons)
      .def_readwrite("refractory_period", &Neuron::refractory_period)
      .def_readwrite("last_spike_time", &Neuron::last_spike_time)
      .def("updateWeights", &Neuron::updateWeights);

  py::class_<Synapse>(m, "Synapse")
      .def(py::init<Neuron*, Neuron*, float>())
      .def("transmit", &Synapse::transmit)
      .def("adjustWeight", &Synapse::adjustWeight)
      .def_readwrite("preNeuron", &Synapse::preNeuron)
      .def_readwrite("postNeuron", &Synapse::postNeuron)
      .def_readwrite("weight", &Synapse::weight)
      .def_readwrite("plasticity", &Synapse::plasticity)
      .def_readwrite("eligibilityTrace", &Synapse::eligibilityTrace);

  py::class_<NeuralNetwork>(m, "NeuralNetwork")
      .def(py::init<float, bool>())
      .def("addNeuron", &NeuralNetwork::addNeuron)
      .def("addSynapse", &NeuralNetwork::addSynapse)
      .def("propagate", &NeuralNetwork::propagate)
      .def("getOutput", &NeuralNetwork::getOutput)
      .def("resetNetwork", &NeuralNetwork::resetNetwork)
      .def("getLearningRate", &NeuralNetwork::getLearningRate)
      .def("setLearningRate", &NeuralNetwork::setLearningRate)
      .def("getDebug", &NeuralNetwork::getDebug)
      .def("setDebug", &NeuralNetwork::setDebug)
      .def("getNeurons", &NeuralNetwork::getNeurons)
      .def("train", &NeuralNetwork::train)
      .def("displayNetwork", &NeuralNetwork::displayNetwork)
      .def("toJson", &NeuralNetwork::toJson)
      .def("fromJson", &NeuralNetwork::fromJson)
      .def("manageSystem", &NeuralNetwork::manageSystem)
      .def("adapt_to_feedback", &NeuralNetwork::adapt_to_feedback)
      .def("feedback_from_system", &NeuralNetwork::feedback_from_system)
      .def("stimulate", &NeuralNetwork::stimulate)
      .def("saveNetwork", &NeuralNetwork::saveNetwork)
      .def("loadNetwork", &NeuralNetwork::loadNetwork);
}
