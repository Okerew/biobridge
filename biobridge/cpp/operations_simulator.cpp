#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <chrono>
#include <thread>
#include <map>
#include <SFML/Graphics.hpp>
#include <fstream>

namespace py = pybind11;
enum class OperationType { CELL, TISSUE, ORGAN };

#ifdef _WIN32
    #include <windows.h>
#elif __unix__ || __APPLE__
    #include <unistd.h>
#endif

class SurgicalTool {
public:
    SurgicalTool() : name(""), precision(0.0), damage(0.0) {}
    SurgicalTool(const std::string& name, double precision, double damage)
        : name(name), precision(precision), damage(damage) {}

    std::string getName() const { return name; }
    double getPrecision() const { return precision; }
    double getDamage() const { return damage; }

private:
    std::string name;
    double precision;
    double damage;
};

class OperationResult {
public:
    OperationResult(bool success, const std::string& message, double healthChange)
        : success(success), message(message), healthChange(healthChange) {}

    bool getSuccess() const { return success; }
    std::string getMessage() const { return message; }
    double getHealthChange() const { return healthChange; }

private:
    bool success;
    std::string message;
    double healthChange;
};

class OperationTarget {
public:
    OperationTarget(const std::string& name, double health)
        : name(name), health(health) {}

    std::string getName() const { return name; }
    double getHealth() const { return health; }
    void setHealth(double newHealth) { health = newHealth; }

private:
    std::string name;
    double health;
};

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

class SurgicalSimulator {
public:
    SurgicalSimulator() {
        tools["scalpel"] = SurgicalTool("Scalpel", 0.9, 5.0);
        tools["forceps"] = SurgicalTool("Forceps", 0.95, 1.0);
        tools["suture"] = SurgicalTool("Suture", 0.85, 2.0);
        tools["laser"] = SurgicalTool("Laser", 0.8, 10.0);

        std::string fontPath = getFontPathFromConfig();
        if (!font.loadFromFile(fontPath)) {
            std::cerr << "Failed to load font" << std::endl;
            if (!font.loadFromFile("arial.ttf")) {
                std::cerr << "Failed to load default font" << std::endl;
            }
        }
    }

    OperationResult operate(OperationTarget& target, const std::string& toolName) {
        if (tools.find(toolName) == tools.end()) {
            return OperationResult(false, "Unknown tool", 0.0);
        }

        const SurgicalTool& tool = tools[toolName];
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(0.0, 1.0);

        bool success = dis(gen) < tool.getPrecision();
        double healthChange = success ? tool.getDamage() : -tool.getDamage();
        target.setHealth(target.getHealth() + healthChange);

        std::string message = success ?
            "Operation successful. Used " + tool.getName() + "." :
            "Operation failed. Damage caused by " + tool.getName() + ".";

        return OperationResult(success, message, healthChange);
    }

    void printOperation(OperationTarget& target, const std::string& toolName) {
        std::cout << "Operating on " << target.getName() << " with " << toolName << std::endl;
        std::cout << "Initial health: " << target.getHealth() << std::endl;

        for (int i = 0; i < 10; ++i) {
            std::cout << "." << std::flush;
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }
        std::cout << std::endl;

        OperationResult result = operate(target, toolName);
        std::cout << result.getMessage() << std::endl;
        std::cout << "Health change: " << result.getHealthChange() << std::endl;
        std::cout << "Final health: " << target.getHealth() << std::endl;
    }

    void visualizeOperation(OperationTarget& target) {
        sf::RenderWindow window(sf::VideoMode(800, 600), "Da Vinci Surgical Simulator");
        sf::Text statusText;
        statusText.setFont(font);
        statusText.setCharacterSize(20);
        statusText.setFillColor(sf::Color::White);
        statusText.setPosition(10, 10);

        sf::RectangleShape healthBar(sf::Vector2f(200, 20));
        healthBar.setPosition(10, 50);
        healthBar.setFillColor(sf::Color::Green);

        sf::CircleShape operationArea(100);
        operationArea.setPosition(300, 200);
        operationArea.setFillColor(sf::Color::Red);

        sf::CircleShape cursor(5);
        cursor.setFillColor(sf::Color::White);

        std::string currentTool = "scalpel";
        bool isOperating = false;

        while (window.isOpen()) {
            sf::Event event;
            while (window.pollEvent(event)) {
                if (event.type == sf::Event::Closed)
                    window.close();
                if (event.type == sf::Event::KeyPressed) {
                    switch (event.key.code) {
                        case sf::Keyboard::Num1: currentTool = "scalpel"; break;
                        case sf::Keyboard::Num2: currentTool = "forceps"; break;
                        case sf::Keyboard::Num3: currentTool = "suture"; break;
                        case sf::Keyboard::Num4: currentTool = "laser"; break;
                        case sf::Keyboard::Space: isOperating = true; break;
                    }
                }
                if (event.type == sf::Event::KeyReleased) {
                    if (event.key.code == sf::Keyboard::Space) {
                        isOperating = false;
                    }
                }
            }

            if (isOperating) {
                OperationResult result = operate(target, currentTool);
                statusText.setString(result.getMessage() + "\nHealth: " + std::to_string(target.getHealth()));
                healthBar.setSize(sf::Vector2f(target.getHealth() * 2, 20));
            }

            cursor.setPosition(sf::Mouse::getPosition(window).x - 5, sf::Mouse::getPosition(window).y - 5);

            window.clear(sf::Color::Black);
            window.draw(statusText);
            window.draw(healthBar);
            window.draw(operationArea);
            window.draw(cursor);
            window.display();
        }
    }

    std::map<std::string, py::object> getOperationData(const OperationTarget& target) const {
        std::map<std::string, py::object> data;
        data["targetName"] = py::cast(target.getName());
        data["finalHealth"] = py::cast(target.getHealth());
        return data;
    }

private:
    std::map<std::string, SurgicalTool> tools;
    sf::Font font;
};

PYBIND11_MODULE(operations_simulator, m) {
    py::enum_<OperationType>(m, "OperationType")
        .value("CELL", OperationType::CELL)
        .value("TISSUE", OperationType::TISSUE)
        .value("ORGAN", OperationType::ORGAN);

    py::class_<SurgicalTool>(m, "SurgicalTool")
        .def(py::init<const std::string&, double, double>())
        .def("getName", &SurgicalTool::getName)
        .def("getPrecision", &SurgicalTool::getPrecision)
        .def("getDamage", &SurgicalTool::getDamage);

    py::class_<OperationTarget>(m, "OperationTarget")
        .def(py::init<const std::string&, double>())
        .def("getName", &OperationTarget::getName)
        .def("getHealth", &OperationTarget::getHealth)
        .def("setHealth", &OperationTarget::setHealth);

    py::class_<OperationResult>(m, "OperationResult")
        .def(py::init<bool, const std::string&, double>())
        .def("getSuccess", &OperationResult::getSuccess)
        .def("getMessage", &OperationResult::getMessage)
        .def("getHealthChange", &OperationResult::getHealthChange);

    py::class_<SurgicalSimulator>(m, "SurgicalSimulator")
        .def(py::init<>())
        .def("operate", &SurgicalSimulator::operate)
        .def("visualizeOperation", &SurgicalSimulator::visualizeOperation)
        .def("printOperation", &SurgicalSimulator::printOperation)
        .def("getOperationData", &SurgicalSimulator::getOperationData);
}