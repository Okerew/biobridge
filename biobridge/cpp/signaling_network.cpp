#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <fstream>
#include <iostream>
#include <map>
#include <nlohmann/json.hpp>
#include <set>
#include <string>
#include <vector>

namespace py = pybind11;

class SignalingNetwork {
 public:
  SignalingNetwork(
      const std::vector<std::string>& molecules,
      const std::map<std::string, std::vector<std::string>>& interactions);

  void activate_molecules(const std::vector<std::string>& molecule_list);
  void propagate_signals(int steps = 10);
  void visualize_network() const;
  void save_network(const std::string& file_path) const;
  static SignalingNetwork load_network(const std::string& file_path);
  std::string to_json() const;
  static SignalingNetwork from_json(const std::string& json_str);
  void reset();

 private:
  std::set<std::string> molecules;
  std::map<std::string, std::vector<std::string>> interactions;
  std::set<std::string> active_molecules;

  static py::module_ networkx;
  static py::module_ matplotlib;
};

using json = nlohmann::json;

py::module_ SignalingNetwork::networkx = py::module_::import("networkx");
py::module_ SignalingNetwork::matplotlib =
    py::module_::import("matplotlib.pyplot");

SignalingNetwork::SignalingNetwork(
    const std::vector<std::string>& molecules,
    const std::map<std::string, std::vector<std::string>>& interactions)
    : molecules(molecules.begin(), molecules.end()),
      interactions(interactions) {}

void SignalingNetwork::activate_molecules(
    const std::vector<std::string>& molecule_list) {
  for (const auto& molecule : molecule_list) {
    if (molecules.find(molecule) != molecules.end()) {
      active_molecules.insert(molecule);
      std::cout << "Molecule " << molecule << " activated." << std::endl;
    } else {
      std::cout << "Molecule " << molecule << " is not in the network."
                << std::endl;
    }
  }
}

void SignalingNetwork::propagate_signals(int steps) {
  for (int step = 0; step < steps; ++step) {
    std::set<std::string> new_activations;
    for (const auto& molecule : active_molecules) {
      auto it = interactions.find(molecule);
      if (it != interactions.end()) {
        for (const auto& target_molecule : it->second) {
          if (active_molecules.find(target_molecule) ==
              active_molecules.end()) {
            new_activations.insert(target_molecule);
            std::cout << "Step " << step + 1 << ": " << molecule << " signals "
                      << target_molecule << "." << std::endl;
          }
        }
      }
    }

    if (new_activations.empty()) {
      break;
    }

    active_molecules.insert(new_activations.begin(), new_activations.end());
  }
}

void SignalingNetwork::visualize_network() const {
  py::gil_scoped_acquire acquire;

  py::object G = networkx.attr("DiGraph")();

  // Add molecules as nodes
  for (const auto& molecule : molecules) {
    G.attr("add_node")(molecule);
  }

  // Add interactions as edges
  for (const auto& [molecule, targets] : interactions) {
    for (const auto& target : targets) {
      G.attr("add_edge")(molecule, target);
    }
  }

  py::object pos = networkx.attr("spring_layout")(G, py::arg("seed") = 42);

  matplotlib.attr("figure")(py::arg("figsize") = py::make_tuple(12, 8));

  // Create node colors list
  py::list node_colors;
  for (const auto& molecule : molecules) {
    if (active_molecules.find(molecule) != active_molecules.end()) {
      node_colors.append("red");
    } else {
      node_colors.append("lightblue");
    }
  }

  networkx.attr("draw")(G, pos, py::arg("with_labels") = true,
                        py::arg("node_color") = node_colors,
                        py::arg("edge_color") = "gray",
                        py::arg("font_weight") = "bold");

  matplotlib.attr("title")("Signaling Network");
  matplotlib.attr("show")();
}

void SignalingNetwork::save_network(const std::string& file_path) const {
  std::ofstream file(file_path, std::ios::binary);
  if (!file) {
    throw std::runtime_error("Unable to open file for writing");
  }

  // Serialize the object
  json j;
  j["molecules"] = std::vector<std::string>(molecules.begin(), molecules.end());
  j["interactions"] = interactions;
  j["active_molecules"] = std::vector<std::string>(active_molecules.begin(),
                                                   active_molecules.end());

  std::string serialized = j.dump();
  file.write(serialized.c_str(), serialized.size());
  std::cout << "Network saved to " << file_path << std::endl;
}

SignalingNetwork SignalingNetwork::load_network(const std::string& file_path) {
  std::ifstream file(file_path, std::ios::binary);
  if (!file) {
    throw std::runtime_error("Unable to open file for reading");
  }

  std::string serialized((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());
  json j = json::parse(serialized);

  SignalingNetwork network(
      j["molecules"].get<std::vector<std::string>>(),
      j["interactions"].get<std::map<std::string, std::vector<std::string>>>());
  network.active_molecules = std::set<std::string>(
      j["active_molecules"].begin(), j["active_molecules"].end());

  std::cout << "Network loaded from " << file_path << std::endl;
  return network;
}

std::string SignalingNetwork::to_json() const {
  json j;
  j["molecules"] = std::vector<std::string>(molecules.begin(), molecules.end());
  j["interactions"] = interactions;
  return j.dump(2);
}

SignalingNetwork SignalingNetwork::from_json(const std::string& json_str) {
  json j = json::parse(json_str);
  return SignalingNetwork(
      j["molecules"].get<std::vector<std::string>>(),
      j["interactions"].get<std::map<std::string, std::vector<std::string>>>());
}

void SignalingNetwork::reset() {
  active_molecules.clear();
  interactions.clear();
}

PYBIND11_MODULE(signaling_network, m) {
  py::class_<SignalingNetwork>(m, "SignalingNetwork")
      .def(py::init<const std::vector<std::string>&,
                    const std::map<std::string, std::vector<std::string>>&>())
      .def("activate_molecules", &SignalingNetwork::activate_molecules)
      .def("propagate_signals", &SignalingNetwork::propagate_signals,
           py::arg("steps") = 10)
      .def("visualize_network", &SignalingNetwork::visualize_network)
      .def("save_network", &SignalingNetwork::save_network)
      .def_static("load_network", &SignalingNetwork::load_network)
      .def("to_json", &SignalingNetwork::to_json)
      .def_static("from_json", &SignalingNetwork::from_json)
      .def("reset", &SignalingNetwork::reset);
}