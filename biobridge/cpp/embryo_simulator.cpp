#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <SFML/Graphics.hpp>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <random>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#elif __unix__ || __APPLE__
#include <unistd.h>
#endif

namespace py = pybind11;

std::string getConfigPath() {
#ifdef _WIN32
  char buffer[MAX_PATH];
  SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, buffer);
  return std::string(buffer) + "\\biobridge\\config.txt";
#elif __unix__ || __APPLE__
  char* homeDir = getenv("HOME");
  if (homeDir == NULL) {
    std::cerr << "Failed to get home directory" << std::endl;
    return "";
  }
  return std::string(homeDir) + "/.config/biobridge/config.txt";
#endif
}

std::string getFontPathFromConfig() {
  std::string configPath = getConfigPath();
  std::ifstream configFile(configPath);
  if (!configFile.is_open()) {
    std::cerr << "Failed to open config file" << std::endl;
    return "";
  }

  std::string line;
  while (std::getline(configFile, line)) {
    if (line.find("font_path=") == 0) {
      return line.substr(10);  // 10 is the length of "font_path="
    }
  }

  std::cerr << "Failed to find font path in config file" << std::endl;
  return "";
}

enum class DevelopmentalStage {
  Zygote,
  Cleavage,
  Blastula,
  Gastrula,
  Organogenesis,
  Fetus
};

class EmbryoSimulation {
 public:
  EmbryoSimulation(int initialCells = 1);
  void step();
  void run(int steps);
  void visualize();
  std::vector<py::object> getCells() const;
  std::vector<py::object> getTissues() const;
  std::vector<py::object> getOrgans() const;
  std::vector<py::object> getSystems() const;
  DevelopmentalStage getStage() const;

 private:
  std::vector<py::object> cells;
  std::vector<py::object> tissues;
  std::vector<py::object> organs;
  std::vector<py::object> systems;
  std::mt19937 rng;
  sf::RenderWindow window;
  DevelopmentalStage stage;
  int daysPassed;

  void divideCells();
  void formBlastula();
  void initiateGastrulation();
  void differentiateGermLayers();
  void initiateOrganogenesis();
  void developFetus();
  void developSystems();
  void handleEvents();
  void draw();

  // Python module and classes
  py::module_ cell_module;
  py::object Cell;
  py::module_ tissue_module;
  py::object Tissue;
  py::module_ organ_module;
  py::object Organ;
  py::module_ system_module;
  py::object System;
};

EmbryoSimulation::EmbryoSimulation(int initialCells)
    : rng(std::random_device{}()),
      stage(DevelopmentalStage::Zygote),
      daysPassed(0) {
  // Import Python modules and classes
  cell_module = py::module_::import("biobridge.blocks.cell");
  Cell = cell_module.attr("Cell");
  tissue_module = py::module_::import("biobridge.blocks.tissue");
  Tissue = tissue_module.attr("Tissue");
  organ_module = py::module_::import("biobridge.definitions.organ");
  Organ = organ_module.attr("Organ");
  system_module = py::module_::import("biobridge.networks.system");
  System = system_module.attr("System");

  for (int i = 0; i < initialCells; ++i) {
    cells.push_back(Cell("Zygote_" + std::to_string(i), "Zygote"));
  }
  window.create(sf::VideoMode(800, 600), "Embryo Simulation");
}

void EmbryoSimulation::developSystems() {
  // Simulate the formation of basic systems
  if (systems.empty()) {
    std::vector<std::string> systemNames = {
        "Nervous System", "Circulatory System", "Respiratory System",
        "Digestive System", "Immune System"};
    for (const auto& systemName : systemNames) {
      systems.push_back(System(systemName));
    }

    // Distribute organs to systems
    for (auto& organ : organs) {
      std::string organName = organ.attr("name").cast<std::string>();
      if (organName == "Brain" || organName == "Spinal Cord") {
        systems[0].attr("add_organ")(organ);
      } else if (organName == "Heart" || organName == "Blood Vessels") {
        systems[1].attr("add_organ")(organ);
      } else if (organName == "Lungs") {
        systems[2].attr("add_organ")(organ);
      } else if (organName == "Stomach" || organName == "Intestines") {
        systems[3].attr("add_organ")(organ);
      } else if (organName == "Thymus" || organName == "Lymph Nodes") {
        systems[4].attr("add_organ")(organ);
      }
    }
  }

  // Simulate system development and function
  for (auto& system : systems) {
    system.attr("simulate_time_step")();
  }
}

void EmbryoSimulation::step() {
  pybind11::gil_scoped_acquire acquire;
  daysPassed++;

  switch (stage) {
    case DevelopmentalStage::Zygote:
      if (daysPassed >= 1) {
        stage = DevelopmentalStage::Cleavage;
      }
      break;
    case DevelopmentalStage::Cleavage:
      divideCells();
      if (cells.size() >= 32) {
        stage = DevelopmentalStage::Blastula;
      }
      break;
    case DevelopmentalStage::Blastula:
      formBlastula();
      if (daysPassed >= 5) {
        stage = DevelopmentalStage::Gastrula;
      }
      break;
    case DevelopmentalStage::Gastrula:
      initiateGastrulation();
      differentiateGermLayers();
      if (daysPassed >= 14) {
        stage = DevelopmentalStage::Organogenesis;
      }
      break;
    case DevelopmentalStage::Organogenesis:
      initiateOrganogenesis();
      if (daysPassed >= 56) {
        stage = DevelopmentalStage::Fetus;
      }
      break;
    case DevelopmentalStage::Fetus:
      developFetus();
      developSystems();
      break;
  }

  for (auto& tissue : tissues) {
    tissue.attr("simulate_time_step")();
  }
  for (auto& organ : organs) {
    // Simulate organ development and function
    if (std::uniform_real_distribution<>(0, 1)(rng) < 0.05) {
      organ.attr("heal")(std::uniform_real_distribution<>(0, 5)(rng));
    }
    if (std::uniform_real_distribution<>(0, 1)(rng) < 0.02) {
      organ.attr("damage")(std::uniform_real_distribution<>(0, 3)(rng));
    }
  }
  for (auto& system : systems) {
    system.attr("simulate_time_step")();
  }
}

void EmbryoSimulation::run(int steps) {
  pybind11::gil_scoped_acquire acquire;
  for (int i = 0; i < steps; ++i) {
    step();
    if (i % 1 == 0) {  // Visualize every 1 step
      visualize();
    }
  }
}

void EmbryoSimulation::visualize() {
  window.clear(sf::Color::White);
  draw();
  window.display();
  handleEvents();
}

std::vector<py::object> EmbryoSimulation::getCells() const { return cells; }

std::vector<py::object> EmbryoSimulation::getTissues() const { return tissues; }

DevelopmentalStage EmbryoSimulation::getStage() const { return stage; }

void EmbryoSimulation::divideCells() {
  std::vector<py::object> newCells;
  for (const auto& cell : cells) {
    if (std::uniform_real_distribution<>(0, 1)(rng) < 0.8) {
      newCells.push_back(cell.attr("divide")());
    }
  }
  cells.insert(cells.end(), newCells.begin(), newCells.end());
}

void EmbryoSimulation::formBlastula() {
  if (tissues.empty()) {
    tissues.push_back(Tissue("Trophoblast", "Epithelial"));
    tissues.push_back(Tissue("Inner Cell Mass", "Pluripotent"));

    // Distribute cells to tissues
    for (const auto& cell : cells) {
      if (std::uniform_real_distribution<>(0, 1)(rng) < 0.7) {
        tissues[0].attr("add_cell")(cell);
        cell.attr("cell_type") = "Trophoblast";
      } else {
        tissues[1].attr("add_cell")(cell);
        cell.attr("cell_type") = "Inner Cell Mass";
      }
    }
  }
}

void EmbryoSimulation::initiateGastrulation() {
  if (tissues.size() == 2) {
    tissues.push_back(Tissue("Ectoderm", "Epithelial"));
    tissues.push_back(Tissue("Mesoderm", "Connective"));
    tissues.push_back(Tissue("Endoderm", "Epithelial"));

    py::list icm_cells = tissues[1].attr("cells");
    for (auto& cell : icm_cells) {
      int layer = std::uniform_int_distribution<>(0, 2)(rng);
      tissues[layer + 2].attr("add_cell")(cell);
    }
    tissues.erase(tissues.begin() + 1);  // Remove Inner Cell Mass
  }
}

void EmbryoSimulation::differentiateGermLayers() {
  for (auto& tissue : tissues) {
    py::list tissue_cells = tissue.attr("cells");
    for (auto& cell : tissue_cells) {
      std::string tissue_name = tissue.attr("name").cast<std::string>();
      if (tissue_name == "Ectoderm") {
        cell.attr("cell_type") =
            std::uniform_real_distribution<>(0, 1)(rng) < 0.5 ? "Neuron"
                                                              : "Epidermis";
      } else if (tissue_name == "Mesoderm") {
        cell.attr("cell_type") =
            std::uniform_real_distribution<>(0, 1)(rng) < 0.5 ? "Muscle"
                                                              : "Bone";
      } else if (tissue_name == "Endoderm") {
        cell.attr("cell_type") =
            std::uniform_real_distribution<>(0, 1)(rng) < 0.5 ? "Intestinal"
                                                              : "Lung";
      }
    }
  }
}

void EmbryoSimulation::initiateOrganogenesis() {
  // Simulate the formation of basic organ structures
  if (organs.empty()) {
    std::vector<std::string> organNames = {"Brain", "Heart", "Liver", "Lungs",
                                           "Kidneys"};
    for (const auto& organName : organNames) {
      py::list organ_tissues;
      for (int i = 0; i < 3; ++i) {
        organ_tissues.append(
            Tissue(organName + "_Tissue_" + std::to_string(i), "Specialized"));
      }
      organs.push_back(Organ(organName, organ_tissues));
    }

    // Distribute some cells from germ layers to organ structures
    for (auto& tissue : tissues) {
      py::list tissue_cells = tissue.attr("cells");
      for (auto& cell : tissue_cells) {
        if (std::uniform_real_distribution<>(0, 1)(rng) < 0.3) {
          int organ_index =
              std::uniform_int_distribution<>(0, organs.size() - 1)(rng);
          py::list organ_tissues = organs[organ_index].attr("tissues");
          int tissue_index =
              std::uniform_int_distribution<>(0, organ_tissues.size() - 1)(rng);
          organ_tissues[tissue_index].attr("add_cell")(cell);
          cell.attr("cell_type") =
              organs[organ_index].attr("name").cast<std::string>() + " Cell";
        }
      }
    }
  }
}

void EmbryoSimulation::developFetus() {
  // Simulate fetal growth and development
  for (auto& organ : organs) {
    py::list organ_tissues = organ.attr("tissues");
    for (auto& tissue : organ_tissues) {
      py::list tissue_cells = tissue.attr("cells");
      if (std::uniform_real_distribution<>(0, 1)(rng) < 0.1) {
        tissue_cells.append(
            Cell(organ.attr("name").cast<std::string>() + "_New",
                 organ.attr("name").cast<std::string>() + " Cell"));
      }
    }
    // Simulate organ growth
    if (std::uniform_real_distribution<>(0, 1)(rng) < 0.05) {
      organ.attr("heal")(std::uniform_real_distribution<>(0, 2)(rng));
    }
  }
}

void EmbryoSimulation::handleEvents() {
  sf::Event event;
  while (window.pollEvent(event)) {
    if (event.type == sf::Event::Closed) {
      window.close();
    }
  }
}

void EmbryoSimulation::draw() {
  pybind11::gil_scoped_acquire acquire;
  float cellRadius = 5.0f;
  float spacing = 15.0f;
  int cellsPerRow =
      std::sqrt(window.getSize().x * window.getSize().y / (spacing * spacing));

  std::vector<py::handle> allCells;

  // Collect cells from all tissues and organs
  for (const auto& tissue : tissues) {
    py::list tissue_cells = tissue.attr("cells");
    for (const auto& cell : tissue_cells) {
      allCells.push_back(cell.inc_ref());
    }
  }

  for (const auto& organ : organs) {
    py::list organ_tissues = organ.attr("tissues");
    for (const auto& tissue : organ_tissues) {
      py::list tissue_cells = tissue.attr("cells");
      for (const auto& cell : tissue_cells) {
        allCells.push_back(cell.inc_ref());
      }
    }
  }

  for (size_t i = 0; i < allCells.size(); ++i) {
    sf::CircleShape shape(cellRadius);
    shape.setPosition(spacing + (i % cellsPerRow) * spacing,
                      spacing + (i / cellsPerRow) * spacing);

    std::string cellType = py::str(allCells[i].attr("cell_type"));
    sf::Color cellColor;

    if (cellType == "Zygote" || cellType == "Inner Cell Mass") {
      cellColor = sf::Color::Yellow;
    } else if (cellType == "Trophoblast") {
      cellColor = sf::Color::Cyan;
    } else if (cellType == "Neuron" || cellType == "Epidermis" ||
               cellType == "Neural Tube Cell") {
      cellColor = sf::Color::Blue;
    } else if (cellType == "Muscle" || cellType == "Bone" ||
               cellType == "Heart Cell") {
      cellColor = sf::Color::Red;
    } else if (cellType == "Intestinal" || cellType == "Lung" ||
               cellType == "Gut Tube Cell") {
      cellColor = sf::Color::Green;
    } else if (cellType.find("Brain") != std::string::npos) {
      cellColor = sf::Color(128, 0, 128);  // Purple for brain cells
    } else if (cellType.find("Liver") != std::string::npos) {
      cellColor = sf::Color(165, 42, 42);  // Brown for liver cells
    } else if (cellType.find("Kidney") != std::string::npos) {
      cellColor = sf::Color(255, 140, 0);  // Dark orange for kidney cells
    } else {
      cellColor = sf::Color::White;
    }

    shape.setFillColor(cellColor);
    window.draw(shape);
  }

  // Clean up Python object references
  for (auto& cell : allCells) {
    cell.dec_ref();
  }

  sf::Font font;
  std::string fontPath = getFontPathFromConfig();
  if (!font.loadFromFile(fontPath)) {
    std::cerr << "Failed to load font" << std::endl;
    if (!font.loadFromFile("arial.ttf")) {
      std::cerr << "Failed to load default font" << std::endl;
    }
  }

  float textStartY =
      window.getSize().y * 0.7f;  // Start at 70% of the window height

  // Draw stage information
  sf::Text stageText;
  stageText.setFont(font);
  stageText.setString("Stage: " + std::to_string(static_cast<int>(stage)) +
                      " | Day: " + std::to_string(daysPassed));
  stageText.setCharacterSize(20);
  stageText.setFillColor(sf::Color::Black);
  stageText.setPosition(10.f, textStartY);
  window.draw(stageText);

  // Draw cell count information
  sf::Text cellCountText;
  cellCountText.setFont(font);
  cellCountText.setString("Total Cells: " + std::to_string(allCells.size()));
  cellCountText.setCharacterSize(16);
  cellCountText.setFillColor(sf::Color::Black);
  cellCountText.setPosition(10.f, textStartY + 30.f);
  window.draw(cellCountText);

  // Draw organ and system information
  sf::Text infoText;
  infoText.setFont(font);
  infoText.setCharacterSize(12);
  infoText.setFillColor(sf::Color::Black);

  float yPos = textStartY + 60.f;
  float xPos = 10.f;
  int itemsPerColumn = 5;
  int currentItem = 0;

  for (const auto& organ : organs) {
    std::string organName = organ.attr("name").cast<std::string>();
    float organHealth = organ.attr("get_health")().cast<float>();
    std::string organInfo =
        organName + ": " + std::to_string(static_cast<int>(organHealth)) + "%";
    infoText.setString(organInfo);
    infoText.setPosition(xPos, yPos);
    window.draw(infoText);

    currentItem++;
    if (currentItem % itemsPerColumn == 0) {
      xPos += 200.f;             // Move to next column
      yPos = textStartY + 60.f;  // Reset Y position
    } else {
      yPos += 20.f;
    }
  }

  for (const auto& system : systems) {
    std::string systemName = system.attr("name").cast<std::string>();
    float systemStatus = system.attr("get_status")().cast<float>();
    std::string systemInfo =
        systemName + ": " +
        std::to_string(static_cast<int>(systemStatus * 100)) + "%";
    infoText.setString(systemInfo);
    infoText.setPosition(xPos, yPos);
    window.draw(infoText);

    currentItem++;
    if (currentItem % itemsPerColumn == 0) {
      xPos += 200.f;             // Move to next column
      yPos = textStartY + 60.f;  // Reset Y position
    } else {
      yPos += 20.f;
    }
  }
}

std::vector<py::object> EmbryoSimulation::getOrgans() const { return organs; }

std::vector<py::object> EmbryoSimulation::getSystems() const { return systems; }

PYBIND11_MODULE(embryo_simulator, m) {
  py::class_<EmbryoSimulation>(m, "EmbryoSimulation")
      .def(py::init<int>())
      .def("step", &EmbryoSimulation::step)
      .def("run", &EmbryoSimulation::run)
      .def("visualize", &EmbryoSimulation::visualize)
      .def("getCells", &EmbryoSimulation::getCells)
      .def("getTissues", &EmbryoSimulation::getTissues)
      .def("getStage", &EmbryoSimulation::getStage)
      .def("getOrgans", &EmbryoSimulation::getOrgans)
      .def("getSystems", &EmbryoSimulation::getSystems);

  py::enum_<DevelopmentalStage>(m, "DevelopmentalStage")
      .value("Zygote", DevelopmentalStage::Zygote)
      .value("Cleavage", DevelopmentalStage::Cleavage)
      .value("Blastula", DevelopmentalStage::Blastula)
      .value("Gastrula", DevelopmentalStage::Gastrula)
      .value("Organogenesis", DevelopmentalStage::Organogenesis)
      .value("Fetus", DevelopmentalStage::Fetus)
      .export_values();
}