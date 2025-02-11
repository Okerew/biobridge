#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/connected_components.hpp>
#include <boost/graph/graph_traits.hpp>
#include <iostream>
#include <memory>
#include <nlohmann/json.hpp>
#include <set>
#include <string>
#include <tuple>
#include <vector>

namespace py = pybind11;

class MetabolicNetwork {
 public:
  MetabolicNetwork(
      const std::vector<std::string>& metabolites,
      const std::vector<std::string>& enzymes,
      const std::vector<std::tuple<std::string, std::string, std::string>>&
          reactions);

  void add_reaction(const std::string& enzyme, const std::string& substrate,
                    const std::string& product);
  void remove_reaction(const std::string& enzyme, const std::string& substrate,
                       const std::string& product);
  std::vector<std::set<std::string>> get_connected_components() const;
  std::map<std::string, std::map<std::string, int>> get_metabolite_degrees()
      const;
  std::string to_json() const;
  static MetabolicNetwork from_json(const std::string& json_str);
  std::set<std::string> predict_outputs(
      const std::set<std::string>& input_metabolites, int steps) const;
  std::vector<std::vector<std::string>> get_possible_pathways(
      const std::string& start_metabolite, const std::string& end_metabolite,
      int max_steps) const;
  void reset();
  void visualize_network(const std::string& save_path = "") const;

 private:
  struct VertexProperties {
    std::string name;
    std::string node_type;
  };

  using Graph = boost::adjacency_list<boost::setS, boost::vecS,
                                      boost::bidirectionalS, VertexProperties>;
  using Vertex = boost::graph_traits<Graph>::vertex_descriptor;

  std::set<std::string> metabolites;
  std::set<std::string> enzymes;
  std::vector<std::tuple<std::string, std::string, std::string>> reactions;
  Graph graph;
  std::map<std::string, Vertex> vertex_map;
  static py::module_ networkx;
  static py::module_ matplotlib;

  void build_graph();
  Vertex add_vertex(const std::string& name, const std::string& node_type);
};

using json = nlohmann::json;

MetabolicNetwork::MetabolicNetwork(
    const std::vector<std::string>& metabolites,
    const std::vector<std::string>& enzymes,
    const std::vector<std::tuple<std::string, std::string, std::string>>&
        reactions)
    : metabolites(metabolites.begin(), metabolites.end()),
      enzymes(enzymes.begin(), enzymes.end()),
      reactions(reactions) {
  build_graph();
}

void MetabolicNetwork::build_graph() {
  for (const auto& metabolite : metabolites) {
    add_vertex(metabolite, "metabolite");
  }
  for (const auto& enzyme : enzymes) {
    add_vertex(enzyme, "enzyme");
  }
  for (const auto& [enzyme, substrate, product] : reactions) {
    boost::add_edge(vertex_map[substrate], vertex_map[enzyme], graph);
    boost::add_edge(vertex_map[enzyme], vertex_map[product], graph);
  }
}

MetabolicNetwork::Vertex MetabolicNetwork::add_vertex(
    const std::string& name, const std::string& node_type) {
  auto v = boost::add_vertex(graph);
  graph[v].name = name;
  graph[v].node_type = node_type;
  vertex_map[name] = v;
  return v;
}

void MetabolicNetwork::add_reaction(const std::string& enzyme,
                                    const std::string& substrate,
                                    const std::string& product) {
  reactions.emplace_back(enzyme, substrate, product);
  enzymes.insert(enzyme);
  metabolites.insert(substrate);
  metabolites.insert(product);

  if (vertex_map.find(enzyme) == vertex_map.end()) {
    add_vertex(enzyme, "enzyme");
  }
  if (vertex_map.find(substrate) == vertex_map.end()) {
    add_vertex(substrate, "metabolite");
  }
  if (vertex_map.find(product) == vertex_map.end()) {
    add_vertex(product, "metabolite");
  }

  boost::add_edge(vertex_map[substrate], vertex_map[enzyme], graph);
  boost::add_edge(vertex_map[enzyme], vertex_map[product], graph);
}

void MetabolicNetwork::remove_reaction(const std::string& enzyme,
                                       const std::string& substrate,
                                       const std::string& product) {
  auto it = std::find(reactions.begin(), reactions.end(),
                      std::make_tuple(enzyme, substrate, product));
  if (it != reactions.end()) {
    reactions.erase(it);
    boost::remove_edge(vertex_map[substrate], vertex_map[enzyme], graph);
    boost::remove_edge(vertex_map[enzyme], vertex_map[product], graph);

    // Remove isolated vertices
    std::vector<Vertex> isolated_vertices;
    for (auto [v, v_end] = boost::vertices(graph); v != v_end; ++v) {
      if (boost::degree(*v, graph) == 0) {
        isolated_vertices.push_back(*v);
      }
    }
    for (auto v : isolated_vertices) {
      std::string name = graph[v].name;
      boost::remove_vertex(v, graph);
      vertex_map.erase(name);
      if (graph[v].node_type == "metabolite") {
        metabolites.erase(name);
      } else {
        enzymes.erase(name);
      }
    }
  }
}

std::vector<std::set<std::string>> MetabolicNetwork::get_connected_components()
    const {
  std::vector<int> component(boost::num_vertices(graph));
  int num_components = boost::connected_components(graph, &component[0]);

  std::vector<std::set<std::string>> result(num_components);
  auto vertex_range = boost::vertices(graph);
  for (auto v = vertex_range.first; v != vertex_range.second; ++v) {
    result[component[*v]].insert(graph[*v].name);
  }
  return result;
}

std::map<std::string, std::map<std::string, int>>
MetabolicNetwork::get_metabolite_degrees() const {
  std::map<std::string, std::map<std::string, int>> degrees;
  for (const auto& metabolite : metabolites) {
    auto v = vertex_map.at(metabolite);
    degrees[metabolite]["in_degree"] = boost::in_degree(v, graph);
    degrees[metabolite]["out_degree"] = boost::out_degree(v, graph);
  }
  return degrees;
}

std::string MetabolicNetwork::to_json() const {
  json j;
  j["metabolites"] = metabolites;
  j["enzymes"] = enzymes;
  j["reactions"] = reactions;
  return j.dump(2);
}

MetabolicNetwork MetabolicNetwork::from_json(const std::string& json_str) {
  json j = json::parse(json_str);
  return MetabolicNetwork(
      j["metabolites"].get<std::vector<std::string>>(),
      j["enzymes"].get<std::vector<std::string>>(),
      j["reactions"]
          .get<std::vector<
              std::tuple<std::string, std::string, std::string>>>());
}

std::set<std::string> MetabolicNetwork::predict_outputs(
    const std::set<std::string>& input_metabolites, int steps) const {
  std::set<std::string> unknown_metabolites;
  for (const auto& metabolite : input_metabolites) {
    if (metabolites.find(metabolite) == metabolites.end()) {
      unknown_metabolites.insert(metabolite);
    }
  }
  if (!unknown_metabolites.empty()) {
    throw std::invalid_argument(
        "Unknown metabolites: " +
        std::accumulate(unknown_metabolites.begin(), unknown_metabolites.end(),
                        std::string(),
                        [](const std::string& a, const std::string& b) {
                          return a.empty() ? b : a + ", " + b;
                        }));
  }

  std::set<std::string> current_metabolites = input_metabolites;
  for (int i = 0; i < steps; ++i) {
    std::set<std::string> new_metabolites;
    for (const auto& metabolite : current_metabolites) {
      for (const auto& [enzyme, substrate, product] : reactions) {
        if (metabolite == substrate) {
          new_metabolites.insert(product);
        }
      }
    }
    current_metabolites.insert(new_metabolites.begin(), new_metabolites.end());
  }
  return current_metabolites;
}

std::vector<std::vector<std::string>> MetabolicNetwork::get_possible_pathways(
    const std::string& start_metabolite, const std::string& end_metabolite,
    int max_steps) const {
  if (metabolites.find(start_metabolite) == metabolites.end()) {
    throw std::invalid_argument("Start metabolite '" + start_metabolite +
                                "' not found in the network");
  }
  if (metabolites.find(end_metabolite) == metabolites.end()) {
    throw std::invalid_argument("End metabolite '" + end_metabolite +
                                "' not found in the network");
  }

  std::vector<std::vector<std::string>> paths;
  std::vector<std::string> current_path;
  std::set<std::string> visited;

  std::function<void(const std::string&, int)> dfs =
      [&](const std::string& current, int depth) {
        if (depth > max_steps) {
          return;
        }
        if (current == end_metabolite) {
          paths.push_back(current_path);
          return;
        }
        for (auto [v, v_end] =
                 boost::adjacent_vertices(vertex_map.at(current), graph);
             v != v_end; ++v) {
          std::string neighbor = graph[*v].name;
          if (visited.find(neighbor) == visited.end()) {
            visited.insert(neighbor);
            current_path.push_back(neighbor);
            dfs(neighbor, depth + 1);
            current_path.pop_back();
            visited.erase(neighbor);
          }
        }
      };

  visited.insert(start_metabolite);
  current_path.push_back(start_metabolite);
  dfs(start_metabolite, 0);

  return paths;
}

void MetabolicNetwork::reset() {
  metabolites.clear();
  enzymes.clear();
  reactions.clear();
  graph.clear();
  vertex_map.clear();
}

py::module_ MetabolicNetwork::networkx = py::module_::import("networkx");
py::module_ MetabolicNetwork::matplotlib =
    py::module_::import("matplotlib.pyplot");

void MetabolicNetwork::visualize_network(const std::string& save_path) const {
  py::object G = networkx.attr("DiGraph")();

  // Add nodes
  for (const auto& [name, v] : vertex_map) {
    py::dict node_attrs;
    node_attrs["node_type"] = graph[v].node_type;
    G.attr("add_node")(name);
  }

  // Add edges
  for (const auto& [enzyme, substrate, product] : reactions) {
    G.attr("add_edge")(substrate, enzyme);
    G.attr("add_edge")(enzyme, product);
  }

  py::object pos = networkx.attr("spring_layout")(G, py::arg("k") = 0.5,
                                                  py::arg("iterations") = 50);

  matplotlib.attr("figure")(py::arg("figsize") = py::make_tuple(12, 8));

  // Draw metabolites
  py::list metabolite_nodes;
  for (const auto& [name, v] : vertex_map) {
    if (graph[v].node_type == "metabolite") {
      metabolite_nodes.append(name);
    }
  }
  networkx.attr("draw_networkx_nodes")(
      G, pos, py::arg("nodelist") = metabolite_nodes,
      py::arg("node_color") = "lightblue", py::arg("node_size") = 500,
      py::arg("alpha") = 0.8);

  // Draw enzymes
  py::list enzyme_nodes;
  for (const auto& [name, v] : vertex_map) {
    if (graph[v].node_type == "enzyme") {
      enzyme_nodes.append(name);
    }
  }
  networkx.attr("draw_networkx_nodes")(
      G, pos, py::arg("nodelist") = enzyme_nodes,
      py::arg("node_color") = "lightgreen", py::arg("node_size") = 500,
      py::arg("node_shape") = "s", py::arg("alpha") = 0.8);

  // Draw edges
  networkx.attr("draw_networkx_edges")(G, pos, py::arg("edge_color") = "gray",
                                       py::arg("arrows") = true);

  // Add labels
  networkx.attr("draw_networkx_labels")(G, pos, py::arg("font_size") = 10);

  matplotlib.attr("title")("Metabolic Network");
  matplotlib.attr("axis")("off");

  if (!save_path.empty()) {
    matplotlib.attr("savefig")(save_path, py::arg("format") = "png",
                               py::arg("dpi") = 300,
                               py::arg("bbox_inches") = "tight");
    std::cout << "Network visualization saved to " << save_path << std::endl;
  } else {
    matplotlib.attr("show")();
  }
}

// Python bindings
PYBIND11_MODULE(metabolic_network, m) {
  py::class_<MetabolicNetwork>(m, "MetabolicNetwork")
      .def(py::init<const std::vector<std::string>&,
                    const std::vector<std::string>&,
                    const std::vector<
                        std::tuple<std::string, std::string, std::string>>&>())
      .def("add_reaction", &MetabolicNetwork::add_reaction)
      .def("remove_reaction", &MetabolicNetwork::remove_reaction)
      .def("get_connected_components",
           &MetabolicNetwork::get_connected_components)
      .def("get_metabolite_degrees", &MetabolicNetwork::get_metabolite_degrees)
      .def("to_json", &MetabolicNetwork::to_json)
      .def_static("from_json", &MetabolicNetwork::from_json)
      .def("predict_outputs", &MetabolicNetwork::predict_outputs)
      .def("get_possible_pathways", &MetabolicNetwork::get_possible_pathways)
      .def("reset", &MetabolicNetwork::reset)
      .def("visualize_network", &MetabolicNetwork::visualize_network);
}