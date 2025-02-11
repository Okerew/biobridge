#include <SFML/Graphics.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <fstream>

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
            return line.substr(10); // 10 is the length of "font_path="
        }
    }

    std::cerr << "Failed to find font path in config file" << std::endl;
    return "";
 }

class Visualizer {
public:
    Visualizer(int width, int height) : window(sf::VideoMode(width, height), "Cell Environment Visualizer") {
        std::string fontPath = getFontPathFromConfig();
        if (!font.loadFromFile(fontPath)) {
            std::cerr << "Failed to load font" << std::endl;
            if (!font.loadFromFile("arial.ttf")) {
                std::cerr << "Failed to load default font" << std::endl;
            }
        }
    }

    void update(const std::vector<std::map<std::string, py::object>>& cell_data) {
        cells.clear();
        for (const auto& cell : cell_data) {
            int x = cell.at("x").cast<int>();
            int y = cell.at("y").cast<int>();
            float health = cell.at("health").cast<float>();
            std::string type = cell.at("type").cast<std::string>();
            int64_t id = cell.at("id").cast<int64_t>();

            sf::CircleShape shape(10);
            shape.setPosition(x * 20, y * 20);
            shape.setFillColor(sf::Color(255, static_cast<sf::Uint8>(health * 2.55), 0));

            sf::Text text(type, font, 12);
            text.setPosition(x * 20, y * 20 + 20);
            text.setFillColor(sf::Color::White);

            cells[id] = {shape, text};
            cellPositions[id] = {x, y};
        }
    }

    bool run_once() {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
                return false;
            }
            if (event.type == sf::Event::MouseButtonPressed) {
                if (event.mouseButton.button == sf::Mouse::Left) {
                    int x = event.mouseButton.x / 20;
                    int y = event.mouseButton.y / 20;
                    selectCell(x, y);
                }
            }
            if (event.type == sf::Event::MouseButtonReleased) {
                if (event.mouseButton.button == sf::Mouse::Left) {
                    int x = event.mouseButton.x / 20;
                    int y = event.mouseButton.y / 20;
                    moveSelectedCell(x, y);
                }
            }
        }

        window.clear();
        for (const auto& cell : cells) {
            window.draw(cell.second.first);
            window.draw(cell.second.second);
        }
        window.display();
        return window.isOpen();
    }

    void selectCell(int x, int y) {
        for (const auto& cell : cells) {
            if (cell.second.first.getPosition() == sf::Vector2f(x * 20, y * 20)) {
                selectedCellId = cell.first;
                return;
            }
        }
        selectedCellId = -1;
    }

    void moveSelectedCell(int x, int y) {
        if (selectedCellId != -1 && m_moveCell) {
            m_moveCell(selectedCellId, x, y);
            cellPositions[selectedCellId] = {x, y};
        }
    }

    void setMoveCell(std::function<void(int64_t, int, int)> func) {
        m_moveCell = func;
    }

    std::map<int64_t, std::pair<int, int>> getCellPositions() const {
        return cellPositions;
    }

private:
    sf::RenderWindow window;
    sf::Font font;
    std::map<int64_t, std::pair<sf::CircleShape, sf::Text>> cells;
    std::map<int64_t, std::pair<int, int>> cellPositions;
    int64_t selectedCellId = -1;
    std::function<void(int64_t, int, int)> m_moveCell;
};

PYBIND11_MODULE(visualizer, m) {
    py::class_<Visualizer>(m, "Visualizer")
        .def(py::init<int, int>())
        .def("update", &Visualizer::update)
        .def("run_once", &Visualizer::run_once)
        .def("setMoveCell", &Visualizer::setMoveCell)
        .def("getCellPositions", &Visualizer::getCellPositions);
}
