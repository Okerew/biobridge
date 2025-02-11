#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <random>
#include <cmath>
#include <algorithm>
#include <memory>
#include <SFML/Graphics.hpp>
#include <fstream>
#include <iostream>

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

namespace py = pybind11;

// Forward declaration of the Infection class
class Infection;

class Person {
public:
    Person(float x, float y, float health, float hunger, float medicine_access)
        : x(x), y(y), health(health), hunger(hunger), medicine_access(medicine_access), infected(false), dead(false) {}

    float x, y;
    float health;
    float hunger;
    float medicine_access;
    bool infected;
    bool dead;
    std::shared_ptr<Infection> infection;
};

// Population class to manage all persons
class Population {
public:
    Population(int size, float width, float height)
        : width(width), height(height), rng(std::random_device{}()) {
        for (int i = 0; i < size; ++i) {
            float x = std::uniform_real_distribution<>(0, width)(rng);
            float y = std::uniform_real_distribution<>(0, height)(rng);
            float health = std::uniform_real_distribution<>(50, 100)(rng);
            float hunger = std::uniform_real_distribution<>(0, 50)(rng);
            float medicine_access = std::uniform_real_distribution<>(0, 1)(rng);
            persons.emplace_back(x, y, health, hunger, medicine_access);
        }
    }

    std::vector<Person>& getPersons() { return persons; }
    float getWidth() const { return width; }
    float getHeight() const { return height; }

private:
    std::vector<Person> persons;
    float width, height;
    std::mt19937 rng;
};

template <typename T>
const T& clamp(const T& value, const T& min, const T& max) {
    if (value < min) {
        return min;
    } else if (value > max) {
        return max;
    } else {
        return value;
    }
}

class Simulator {
public:
    Simulator(Population& population, py::object infection_class)
        : population(population), infection_class(infection_class), rng(std::random_device{}()),
          deathCount(0), infectionCount(0) {}

    void update() {
        for (auto& person : population.getPersons()) {
            updatePerson(person);
        }
    }

    void infect(int index) {
        if (index >= 0 && index < population.getPersons().size()) {
            auto& person = population.getPersons()[index];
            if (!person.infected && !person.dead) {
                person.infected = true;
                person.infection = createInfection();
                infectionCount++;
            }
        }
    }

    int getInfectedCount() const { return infectionCount; }
    int getDeathCount() const { return deathCount; }

    py::list getPopulationState() const {
        py::list state;
        for (const auto& person : population.getPersons()) {
            py::dict person_state;
            person_state["x"] = person.x;
            person_state["y"] = person.y;
            person_state["health"] = person.health;
            person_state["hunger"] = person.hunger;
            person_state["medicine_access"] = person.medicine_access;
            person_state["infected"] = person.infected;
            person_state["dead"] = person.dead;
            state.append(person_state);
        }
        return state;
    }

    int getInfectionRisk(int index) const {
        return calculateInfectionRisk(population.getPersons()[index], population.getPersons()[index]);
    }

private:
    Population& population;
    py::object infection_class;
    std::mt19937 rng;
    int deathCount;
    int infectionCount;

    void updatePerson(Person& person) {
        if (person.dead) return;

        if (person.infected) {
            // Simulate infection progression
            person.health -= std::uniform_real_distribution<>(0, 1)(rng) * (1 - person.medicine_access);
            if (person.health <= 0) {
                person.dead = true;
                person.infected = false;
                person.infection.reset();
                deathCount++;
                infectionCount--;
            } else {
                // Attempt to spread infection
                for (auto& other : population.getPersons()) {
                    if (!other.infected && !other.dead && calculateDistance(person, other) < 10) {
                        float infectionRisk = calculateInfectionRisk(person, other);
                        if (std::uniform_real_distribution<>(0, 1)(rng) < infectionRisk) {
                            other.infected = true;
                            other.infection = createInfection();
                            infectionCount++;
                        }
                    }
                }
            }
        }

        // Update hunger and health
        person.hunger += std::uniform_real_distribution<>(0, 0.1)(rng);
        if (person.hunger > 100) {
            person.health -= std::uniform_real_distribution<>(0, 1)(rng);
        }

        // Random movement
        person.x += std::uniform_real_distribution<>(-1, 1)(rng);
        person.y += std::uniform_real_distribution<>(-1, 1)(rng);
        person.x = clamp(person.x, 0.0f, population.getWidth());
        person.y = clamp(person.y, 0.0f, population.getHeight());
    }

    float calculateDistance(const Person& p1, const Person& p2) const {
        float dx = p1.x - p2.x;
        float dy = p1.y - p2.y;
        return std::sqrt(dx*dx + dy*dy);
    }

    float calculateInfectionRisk(const Person& infected, const Person& target) const {
        float distance = calculateDistance(infected, target);

        // Base risk decreases with distance
        float baseRisk = 1.0f / (1.0f + distance);

        // Modify risk based on target's health and hunger
        float healthFactor = 1.0f - (target.health / 100.0f);
        float hungerFactor = target.hunger / 100.0f;

        // Medicine access reduces risk
        float medicineAccessFactor = 1.0f - target.medicine_access;

        // Combine all factors
        float risk = baseRisk * (1.0f + healthFactor) * (1.0f + hungerFactor) * medicineAccessFactor;

        // Scale risk based on infected person's health (sicker people might be more contagious)
        float infectedHealthFactor = 1.0f - (infected.health / 100.0f);
        risk *= (1.0f + infectedHealthFactor);

        // Ensure risk is between 0 and 1
        return clamp(risk, 0.0f, 1.0f);
    }

    std::shared_ptr<Infection> createInfection() {
        py::object infection = infection_class("New Infection", py::cast("virus"), 0.5, "ATCG");
        return std::make_shared<Infection>(infection);
    }
};

// Wrapper for the Python Infection class
class Infection {
public:
    Infection(py::object pyInfection) : pyInfection(pyInfection) {}

    py::object getPyObject() const { return pyInfection; }

private:
    py::object pyInfection;
};

// Visualizer class using SFML
class Visualizer {
public:
    Visualizer(Population& population, int windowWidth, int windowHeight)
        : window(sf::VideoMode(windowWidth, windowHeight), "Infection Simulator"),
          population(population), font() {
        std::string fontPath = getFontPathFromConfig();
        if (!font.loadFromFile(fontPath)) {
            std::cerr << "Failed to load font" << std::endl;
            if (!font.loadFromFile("arial.ttf")) {
                std::cerr << "Failed to load default font" << std::endl;
            }
        }
        statsText.setFont(font);
        statsText.setCharacterSize(20);
        statsText.setFillColor(sf::Color::White);
        statsText.setPosition(10, 10);
    }

    void render(const Simulator& simulator) {
        window.clear(sf::Color::Black);
        for (auto& person : population.getPersons()) {
            sf::CircleShape shape(3);
            shape.setPosition(person.x, person.y);
            if (person.dead) {
                shape.setFillColor(sf::Color::White);
            } else if (person.infected) {
                shape.setFillColor(sf::Color::Red);
            } else {
                shape.setFillColor(sf::Color::Green);
            }
            window.draw(shape);
        }

        // Update and draw stats
        std::string stats = "Infected: " + std::to_string(simulator.getInfectedCount()) +
                            "\nDeaths: " + std::to_string(simulator.getDeathCount());
        statsText.setString(stats);
        window.draw(statsText);

        window.display();
    }

    bool isOpen() const { return window.isOpen(); }

    void handleEvents() {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            }
        }
    }

private:
    sf::RenderWindow window;
    Population& population;
    sf::Font font;
    sf::Text statsText;
};

PYBIND11_MODULE(infection_simulator, m) {
    py::class_<Population>(m, "Population")
        .def(py::init<int, float, float>())
        .def("get_width", &Population::getWidth)
        .def("get_height", &Population::getHeight);

    py::class_<Simulator>(m, "Simulator")
        .def(py::init<Population&, py::object>())
        .def("update", &Simulator::update)
        .def("infect", &Simulator::infect)
        .def("get_infected_count", &Simulator::getInfectedCount)
        .def("get_death_count", &Simulator::getDeathCount)
        .def("get_population_state", &Simulator::getPopulationState)
        .def("get_infection_risk", &Simulator::getInfectionRisk);


    py::class_<Visualizer>(m, "Visualizer")
        .def(py::init<Population&, int, int>())
        .def("render", &Visualizer::render)
        .def("is_open", &Visualizer::isOpen)
        .def("handle_events", &Visualizer::handleEvents);
}