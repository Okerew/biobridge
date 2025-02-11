#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <csignal>
#include <iostream>
#include <memory>
#include <random>
#include <vector>

namespace py = pybind11;

volatile sig_atomic_t termination_requested = 0;

// SIGTERM handler
extern "C" void sigterm_handler(int signum) { termination_requested = 1; }

class ImmuneCell {
 public:
  ImmuneCell(const std::string& name, double strength, py::object py_cell)
      : name(name), strength(strength), py_cell(py_cell), activated(false) {}

  virtual ~ImmuneCell() = default;

  virtual void attack(py::object& infection) = 0;
  virtual std::string getType() const = 0;

  virtual void activate() {
    py::gil_scoped_acquire acquire;
    if (!activated) {
      activated = true;
      std::cout << getType() << " " << name << " is activated." << std::endl;
      strength *= 1.5;
      py_cell.attr("activated") = true;
    }
  }

  virtual void deactivate() {
    py::gil_scoped_acquire acquire;
    if (activated) {
      activated = false;
      std::cout << getType() << " " << name << " is deactivated." << std::endl;
      strength /= 1.5;
      py_cell.attr("activated") = false;
    }
  }

  std::string getName() const { return name; }
  double getStrength() const { return strength; }
  py::object getPyCell() const { return py_cell; }
  bool isActivated() const { return activated; }

 protected:
  std::string name;
  double strength;
  py::object py_cell;
  bool activated;
};

class Macrophage : public ImmuneCell {
 public:
  Macrophage(const std::string& name, double strength, py::object py_cell)
      : ImmuneCell(name, strength, py_cell) {}

  void attack(py::object& infection) override {
    py::gil_scoped_acquire acquire;
    std::cout << "Macrophage " << name << " is engulfing the infection."
              << std::endl;
    double current_spread_rate = infection.attr("spread_rate").cast<double>();
    double reduction_factor = activated ? 0.15 : 0.1;
    infection.attr("spread_rate") =
        std::max(0.0, current_spread_rate - reduction_factor * strength);

    int health_reduction = activated ? 3 : 5;
    py_cell.attr("health") =
        py_cell.attr("health").cast<int>() - health_reduction;
  }

  std::string getType() const override { return "Macrophage"; }

  void activate() override {
    ImmuneCell::activate();
    if (activated) {
      py::gil_scoped_acquire acquire;
      std::cout << "Macrophage " << name << " is releasing cytokines."
                << std::endl;
      py_cell.attr("add_surface_protein")("MHC-II");
    }
  }

  void deactivate() override {
    ImmuneCell::deactivate();
    if (!activated) {
      py::gil_scoped_acquire acquire;
      std::cout << "Macrophage " << name << " has stopped releasing cytokines."
                << std::endl;
      py_cell.attr("remove_surface_protein")("MHC-II");
    }
  }
};

class TCell : public ImmuneCell {
 public:
  TCell(const std::string& name, double strength, py::object py_cell)
      : ImmuneCell(name, strength, py_cell) {}

  void attack(py::object& infection) override {
    py::gil_scoped_acquire acquire;
    std::cout << "T Cell " << name << " is attacking infected cells."
              << std::endl;
    py::list infected_cells = infection.attr("infected_cells");
    int cells_to_remove = static_cast<int>(strength * (activated ? 3 : 2));
    for (int i = 0; i < cells_to_remove && !infected_cells.empty(); ++i) {
      infected_cells.attr("pop")();
    }

    int health_reduction = activated ? 2 : 3;
    py_cell.attr("health") =
        py_cell.attr("health").cast<int>() - health_reduction;
  }

  std::string getType() const override { return "T Cell"; }

  void activate() override {
    ImmuneCell::activate();
    if (activated) {
      py::gil_scoped_acquire acquire;
      std::cout << "T Cell " << name << " is producing cytokines." << std::endl;
      py_cell.attr("add_surface_protein")("CD28");
    }
  }

  void deactivate() override {
    ImmuneCell::deactivate();
    if (!activated) {
      py::gil_scoped_acquire acquire;
      std::cout << "T Cell " << name << " has stopped producing cytokines."
                << std::endl;
      py_cell.attr("remove_surface_protein")("CD28");
    }
  }
};

class BCell : public ImmuneCell {
 public:
  BCell(const std::string& name, double strength, py::object py_cell)
      : ImmuneCell(name, strength, py_cell) {}

  void attack(py::object& infection) override {
    py::gil_scoped_acquire acquire;
    std::cout << "B Cell " << name << " is producing antibodies." << std::endl;
    double current_spread_rate = infection.attr("spread_rate").cast<double>();
    double reduction_factor = activated ? 0.08 : 0.05;
    infection.attr("spread_rate") =
        std::max(0.0, current_spread_rate - reduction_factor * strength);

    int health_reduction = activated ? 1 : 2;
    py_cell.attr("health") =
        py_cell.attr("health").cast<int>() - health_reduction;
  }

  std::string getType() const override { return "B Cell"; }

  void activate() override {
    ImmuneCell::activate();
    if (activated) {
      py::gil_scoped_acquire acquire;
      std::cout << "B Cell " << name << " is differentiating into plasma cells."
                << std::endl;
      py_cell.attr("add_surface_protein")("CD19");
    }
  }

  void deactivate() override {
    ImmuneCell::deactivate();
    if (!activated) {
      py::gil_scoped_acquire acquire;
      std::cout << "B Cell " << name
                << " has stopped differentiating into plasma cells."
                << std::endl;
      py_cell.attr("remove_surface_protein")("CD19");
    }
  }
};

class ImmuneSystem {
 public:
  ImmuneSystem(
      py::object cell_class,
      const std::vector<std::tuple<std::string, double, std::string>>& cells)
      : cell_class(cell_class), immune_cells(cells) {
    createImmuneCells();
    py::module_ plt = py::module_::import("matplotlib.pyplot");
    py::module_ np = py::module_::import("numpy");

    fig = plt.attr("figure")();
    ax = fig.attr("add_subplot")(111);
  }

  void createImmuneCells() {
    py::gil_scoped_acquire acquire;
    for (const auto& immune_cell : immune_cells) {
      const std::string& name = std::get<0>(immune_cell);
      double strength = std::get<1>(immune_cell);
      const std::string& type = std::get<2>(immune_cell);

      if (type == "Macrophage") {
        createCell<Macrophage>(name, strength);
      } else if (type == "TCell") {
        createCell<TCell>(name, strength);
      } else if (type == "BCell") {
        createCell<BCell>(name, strength);
      }
    }
  }

  void respond(py::object infection, py::object cells) {
    if (termination_requested) {
      std::cout << "Termination requested. Stopping immune system response."
                << std::endl;
      return;
    }

    std::cout << "Immune system responding to infection:" << std::endl;

    double totalATPProduced = 0.0;

    try {
      py::gil_scoped_acquire acquire;

      if (!py::isinstance<py::list>(cells)) {
        throw std::runtime_error("Error: 'cells' is not a list.");
      }

      py::list cellList = py::cast<py::list>(cells);

      std::vector<py::object> allCells;
      for (auto cellHandle : cellList) {
        allCells.push_back(py::reinterpret_borrow<py::object>(cellHandle));
      }
      for (const auto& immuneCell : this->cells) {
        allCells.push_back(immuneCell->getPyCell());
      }

      // Process infection and cell responses
      for (auto& cell : allCells) {
        if (termination_requested) {
          std::cout << "Termination requested. Stopping cell processing."
                    << std::endl;
          return;
        }

        if (!cell) {
          std::cerr << "Error: Cell is null." << std::endl;
          continue;
        }

        try {
          py::object result = infection.attr("infect")(cell);

          if (py::isinstance<py::float_>(result)) {
            float float_result = result.cast<float>();
            std::cout << "Cell "
                      << py::str(cell.attr("name")).cast<std::string>()
                      << " infection result (float): " << float_result
                      << std::endl;
          } else if (py::isinstance<py::bool_>(result)) {
            bool success = result.cast<bool>();
            std::cout << "Cell "
                      << py::str(cell.attr("name")).cast<std::string>()
                      << " was "
                      << (success ? "successfully infected." : "not infected.")
                      << std::endl;
          } else {
            throw std::runtime_error("Error: Unexpected result type.");
          }
        } catch (const py::error_already_set& e) {
          std::cerr << "Python error during infection: " << e.what()
                    << std::endl;
        }
      }

      // Immune cell actions
      for (const auto& immuneCell : this->cells) {
        if (termination_requested) {
          std::cout << "Termination requested. Stopping immune cell actions."
                    << std::endl;
          return;
        }

        immuneCell->attack(infection);
        immuneCell->activate();
      }

      // Cell division (if needed)
      if (py::len(cellList) < 10) {
        try {
          py::object new_cell = cellList[0].attr("divide")();

          if (!new_cell.is_none()) {
            createCell<TCell>("TCell" + std::to_string(py::len(cellList) + 1),
                              0.8, new_cell);
          } else {
            std::cerr << "Error: Failed to create new cell." << std::endl;
          }
        } catch (const py::error_already_set& e) {
          std::cerr << "Python error during cell division: " << e.what()
                    << std::endl;
        }
      }

      // Update all cells and calculate ATP production
      for (auto& cell : allCells) {
        if (termination_requested) {
          std::cout << "Termination requested. Stopping cell updates."
                    << std::endl;
          return;
        }

        if (!cell) {
          std::cerr << "Error: Cell is null." << std::endl;
          continue;
        }

        try {
          updateCell(cell, totalATPProduced);
        } catch (const std::exception& e) {
        }
      }

      // Update immune cells
      for (auto& immuneCell : this->cells) {
        if (termination_requested) {
          std::cout << "Termination requested. Stopping immune cell updates."
                    << std::endl;
          return;
        }

        updateImmuneCell(immuneCell);
      }

      std::cout << "Total ATP produced: " << totalATPProduced << std::endl;

    } catch (const std::exception& e) {
      std::cerr << "Exception occurred: " << e.what() << std::endl;
    }
  }

  void updateImmuneCell(const std::unique_ptr<ImmuneCell>& cell) {
    py::object py_cell = cell->getPyCell();
    py_cell.attr("metabolize")();
    py_cell.attr("update_structural_integrity")();

    // Remove dead cells
    if (py_cell.attr("health").cast<int>() <= 0) {
      cells.erase(std::remove_if(cells.begin(), cells.end(),
                                 [&](const std::unique_ptr<ImmuneCell>& c) {
                                   return c.get() == cell.get();
                                 }),
                  cells.end());
    }
  }

  void updateCell(py::object cell, double& totalATPProduced) {
    double atpProduced = cell.attr("getATPProduction")().cast<double>();

    // Update the total ATP production
    totalATPProduced += atpProduced;

    std::cout << "Cell " << py::str(cell.attr("getName")()).cast<std::string>()
              << " produced " << atpProduced << " ATP." << std::endl;
  }

  void visualize(py::object infection, py::object cells) {
    py::gil_scoped_acquire acquire;

    // Clear previous plot
    ax.attr("clear")();

    // Plot infection
    double spread_rate = infection.attr("spread_rate").cast<double>();
    ax.attr("scatter")(0, 0, py::arg("s") = spread_rate * 1000,
                       py::arg("c") = "red", py::arg("alpha") = 0.5,
                       py::arg("label") = "Infection");

    // Plot cells
    std::vector<double> x, y;
    std::vector<std::string> colors;
    std::vector<double> sizes;

    for (const auto& cell : cells) {
      x.push_back(((double)rand() / (RAND_MAX)) * 10 - 5);
      y.push_back(((double)rand() / (RAND_MAX)) * 10 - 5);

      std::string cell_type =
          py::str(cell.attr("cell_type")).cast<std::string>();
      if (cell_type == "Macrophage") {
        colors.push_back("blue");
      } else if (cell_type == "TCell") {
        colors.push_back("green");
      } else if (cell_type == "BCell") {
        colors.push_back("yellow");
      } else {
        colors.push_back("gray");
      }

      sizes.push_back(cell.attr("health").cast<double>() * 10);
    }

    ax.attr("scatter")(x, y, py::arg("c") = colors, py::arg("s") = sizes,
                       py::arg("alpha") = 0.7);

    ax.attr("set_xlim")(-10, 10);
    ax.attr("set_ylim")(-10, 10);
    ax.attr("set_title")("Immune System Simulation");
    ax.attr("legend")();

    // Display the plot
    py::module_::import("matplotlib.pyplot").attr("draw")();
    py::module_::import("matplotlib.pyplot").attr("pause")(0.001);
  }

  py::list getCells() const {
    py::gil_scoped_acquire acquire;
    py::list result;
    for (const auto& cell : cells) {
      result.append(cell->getPyCell());
    }
    return result;
  }

 private:
  template <typename T, typename... Args>
  std::unique_ptr<T> make_unique(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
  }

  template <typename T>
  void createCell(const std::string& name, double strength,
                  py::object py_cell = py::none()) {
    py::gil_scoped_acquire acquire;

    if (py_cell.is_none()) {
      // Create a temporary object to get the type from the class
      T tempCell(name, strength, py::none());
      py_cell = cell_class(name, tempCell.getType(), py::list(), py::list(),
                           py::dict());
    }

    // Ensure T refers to the correct type and create the cell
    cells.push_back(make_unique<T>(name, strength, py_cell));
  }

  py::object fig;
  py::object ax;
  std::vector<std::unique_ptr<ImmuneCell>> cells;
  py::object cell_class;
  std::vector<std::tuple<std::string, double, std::string>>
      immune_cells;  // List of cells (name, strength, type)
};

PYBIND11_MODULE(immune_system, m) {
  signal(SIGTERM, sigterm_handler);
  py::class_<ImmuneSystem>(m, "ImmuneSystem")
      .def(
          py::init<py::object,
                   std::vector<std::tuple<std::string, double, std::string>>>(),
          py::arg("cell_class"), py::arg("cells"))
      .def("respond", &ImmuneSystem::respond)
      .def("visualize", &ImmuneSystem::visualize)
      .def("getCells", &ImmuneSystem::getCells);

  py::class_<ImmuneCell>(m, "ImmuneCell")
      .def("getName", &ImmuneCell::getName)
      .def("getStrength", &ImmuneCell::getStrength)
      .def("getPyCell", &ImmuneCell::getPyCell)
      .def("activate", &ImmuneCell::activate)
      .def("deactivate", &ImmuneCell::deactivate);

  py::class_<Macrophage>(m, "Macrophage")
      .def(py::init<const std::string&, double, py::object>())
      .def("getType", &Macrophage::getType)
      .def("attack", &Macrophage::attack)
      .def("activate", &Macrophage::activate)
      .def("deactivate", &Macrophage::deactivate);

  py::class_<TCell>(m, "TCell")
      .def(py::init<const std::string&, double, py::object>())
      .def("getType", &TCell::getType)
      .def("attack", &TCell::attack)
      .def("activate", &TCell::activate)
      .def("deactivate", &TCell::deactivate);

  py::class_<BCell>(m, "BCell")
      .def(py::init<const std::string&, double, py::object>())
      .def("getType", &BCell::getType)
      .def("attack", &BCell::attack)
      .def("activate", &BCell::activate)
      .def("deactivate", &BCell::deactivate);
}