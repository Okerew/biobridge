#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

#include "consciousness_simulator.h"

namespace py = pybind11;

class Society;

enum class PoliticalBelief {
  AUTHORITARIANISM,
  LIBERALISM,
  SOCIALISM,
  CONSERVATISM,
  ENVIRONMENTALISM
};

class Individual : public ConsciousnessSimulator {
 private:
  PoliticalBelief politicalBelief_;

 public:
  Individual(int intelligence, int age, PoliticalBelief belief,
             double selfAwareness, const std::string& type, double knowledge,
             double experience, const Personality& personality,
             const GeneticPredisposition& genetics,
             const Environment& environment,
             const std::map<std::string, double>& cognitiveBiases = {},
             const std::map<std::string, std::string>& culturalContext = {},
             const std::vector<Emotion>& emotions = {},
             const std::map<std::string, double>& substanceEffects = {})
      : ConsciousnessSimulator(selfAwareness, type, age, knowledge, experience,
                               personality, genetics, environment,
                               cognitiveBiases, culturalContext, emotions,
                               substanceEffects),
        politicalBelief_(belief) {}

  int getIntelligence() const {
    return getGeneticPredisposition().getGene("intelligence") * 100;
  }
  int getAge() const { return ConsciousnessSimulator::getAge(); }
  PoliticalBelief getPoliticalBelief() const { return politicalBelief_; }
  void incrementAge() { ConsciousnessSimulator::incrementAge(); }
  void setPoliticalBelief(PoliticalBelief belief) { politicalBelief_ = belief; }

  double getSelfAwareness() const {
    return ConsciousnessSimulator::getSelfAwareness();
  }
  std::string getType() const { return ConsciousnessSimulator::getType(); }
  double getKnowledge() const { return ConsciousnessSimulator::getKnowledge(); }
  double getExperience() const {
    return ConsciousnessSimulator::getExperience();
  }
  const Personality& getPersonality() const {
    return ConsciousnessSimulator::getPersonality();
  }
  const GeneticPredisposition& getGeneticPredisposition() const {
    return ConsciousnessSimulator::getGeneticPredisposition();
  }
  const Environment& getEnvironment() const {
    return ConsciousnessSimulator::getEnvironment();
  }
};

class Obstacle {
 public:
  Obstacle(const std::string& name, int difficulty)
      : name_(name), difficulty_(difficulty), progress_(0) {}

  std::string getName() const { return name_; }
  int getDifficulty() const { return difficulty_; }
  int getProgress() const { return progress_; }
  void incrementProgress(int amount) { progress_ += amount; }
  bool isOvercome() const { return progress_ >= 100; }

 private:
  std::string name_;
  int difficulty_;
  int progress_;
};

// New enum for terrain types
enum class Terrain { PLAINS, MOUNTAINS, FOREST, DESERT, URBAN };

class MilitaryUnit {
 public:
  MilitaryUnit(int size, double technology, double mobility)
      : size_(size), technology_(technology), mobility_(mobility) {}

  int getSize() const { return size_; }
  double getTechnology() const { return technology_; }
  double getMobility() const { return mobility_; }

 private:
  int size_;
  double technology_;
  double mobility_;
};

class War : public Obstacle {
 public:
  War(const std::string& name, int difficulty, const Society& attacker,
      const Society& defender, Terrain terrain)
      : Obstacle(name, difficulty),
        attacker_(attacker),
        defender_(defender),
        terrain_(terrain) {}

  const Society& getAttacker() const { return attacker_; }
  const Society& getDefender() const { return defender_; }
  Terrain getTerrain() const { return terrain_; }

 private:
  const Society& attacker_;
  const Society& defender_;
  Terrain terrain_;
};

class Society {
 public:
  Society(const std::string& name, int developmentStage,
          const std::string& governmentType)
      : name_(name),
        developmentStage_(developmentStage),
        governmentType_(governmentType),
        resources_(1000),
        technology_(1) {}

  void addIndividual(const Individual& individual) {
    population_.push_back(individual);
  }

  void setMilitaryUnit(const MilitaryUnit& unit) { militaryUnit_ = unit; }
  const MilitaryUnit& getMilitaryUnit() const { return militaryUnit_; }

  void setTerrainFamiliarity(const std::map<Terrain, double>& familiarity) {
    terrainFamiliarity_ = familiarity;
  }
  double getTerrainFamiliarity(Terrain terrain) const {
    return terrainFamiliarity_.at(terrain);
  }

  void setStrategySkill(double skill) { strategySkill_ = skill; }
  double getStrategySkill() const { return strategySkill_; }

  void setDesperation(double desperation) { desperation_ = desperation; }
  double getDesperation() const { return desperation_; }

  void setNutrientAvailability(double nutrients) {
    nutrientAvailability_ = nutrients;
  }
  double getNutrientAvailability() const { return nutrientAvailability_; }

  void setSupplyLineEfficiency(double efficiency) {
    supplyLineEfficiency_ = efficiency;
  }
  double getSupplyLineEfficiency() const { return supplyLineEfficiency_; }

  void evolve() {
    developmentStage_++;
    resources_ += calculateResourceGrowth();
    technology_ *= 1.05;  // 5% technology growth per year

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> politicalShiftChance(0, 1);

    for (auto& individual : population_) {
      individual.incrementAge();
      if (politicalShiftChance(gen) < 0.1) {  // 10% chance of changing beliefs
        individual.setPoliticalBelief(getRandomPoliticalBelief());
      }
    }

    // Remove individuals older than 100 (simple death mechanism)
    population_.erase(
        std::remove_if(population_.begin(), population_.end(),
                       [](const Individual& i) { return i.getAge() > 100; }),
        population_.end());

    // Add new individuals (simple birth mechanism)
    if (population_.size() < 1000) {
      std::uniform_int_distribution<> intDist(50, 150);
      int newIndividuals =
          std::min(100, 1000 - static_cast<int>(population_.size()));
      for (int i = 0; i < newIndividuals; i++) {
        Individual parent = population_[rd() % population_.size()];
        addIndividual(createNewIndividual(parent, intDist(gen)));
      }
    }

    // Handle obstacles
    for (auto& obstacle : obstacles_) {
      if (!obstacle.isOvercome()) {
        int progressMade = calculateObstacleProgress(obstacle);
        obstacle.incrementProgress(progressMade);
        resources_ -=
            obstacle.getDifficulty();  // Overcoming obstacles costs resources
      }
    }

    // Remove overcome obstacles
    obstacles_.erase(
        std::remove_if(obstacles_.begin(), obstacles_.end(),
                       [](const Obstacle& o) { return o.isOvercome(); }),
        obstacles_.end());
  }

  void addObstacle(const Obstacle& obstacle) { obstacles_.push_back(obstacle); }

  double getAverageIntelligence() const {
    if (population_.empty()) return 0.0;
    double sum = 0.0;
    for (const auto& individual : population_) {
      sum += individual.getIntelligence();
    }
    return sum / population_.size();
  }

  std::map<PoliticalBelief, double> getPoliticalBeliefDistribution() const {
    std::map<PoliticalBelief, int> beliefCounts;
    for (const auto& individual : population_) {
      beliefCounts[individual.getPoliticalBelief()]++;
    }
    std::map<PoliticalBelief, double> distribution;
    for (const auto& [belief, count] : beliefCounts) {
      distribution[belief] = static_cast<double>(count) / population_.size();
    }
    return distribution;
  }

  PoliticalBelief getMostPopularBelief() const {
    auto distribution = getPoliticalBeliefDistribution();
    return std::max_element(distribution.begin(), distribution.end(),
                            [](const std::pair<PoliticalBelief, double>& a,
                               const std::pair<PoliticalBelief, double>& b) {
                              return a.second < b.second;
                            })
        ->first;
  }

  int getDevelopmentStage() const { return developmentStage_; }
  std::string getName() const { return name_; }
  size_t getPopulationSize() const { return population_.size(); }
  std::string getGovernmentType() const { return governmentType_; }
  int getResources() const { return resources_; }
  double getTechnology() const { return technology_; }
  const std::vector<Obstacle>& getObstacles() const { return obstacles_; }

 private:
  std::string name_;
  int developmentStage_;
  std::string governmentType_;
  std::vector<Individual> population_;
  std::vector<Obstacle> obstacles_;
  int resources_;
  double technology_;
  MilitaryUnit militaryUnit_{0, 0.0, 0.0};
  std::map<Terrain, double> terrainFamiliarity_;
  double strategySkill_ = 0.0;
  double desperation_ = 0.0;
  double nutrientAvailability_ = 0.0;
  double supplyLineEfficiency_ = 0.0;

  PoliticalBelief getRandomPoliticalBelief() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(0, 4);
    return static_cast<PoliticalBelief>(dist(gen));
  }

  int calculateResourceGrowth() const {
    return static_cast<int>(resources_ * 0.05 * (technology_ / 10.0));
  }

  int calculateObstacleProgress(const Obstacle& obstacle) const {
    double progressFactor = (getAverageIntelligence() / 100.0) *
                            (technology_ / 10.0) * (developmentStage_ / 10.0);
    return static_cast<int>(
        std::min(100.0, 100.0 / obstacle.getDifficulty() * progressFactor));
  }

  Individual createNewIndividual(const Individual& parent, int intelligence) {
    return Individual(
        intelligence, 0, getRandomPoliticalBelief(), parent.getSelfAwareness(),
        parent.getType(), parent.getKnowledge(), parent.getExperience(),
        parent.getPersonality(), parent.getGeneticPredisposition(),
        parent.getEnvironment(), std::map<std::string, double>(),
        std::map<std::string, std::string>());
  }
};

template <typename T>
constexpr const T& clamp(const T& v, const T& lo, const T& hi) {
  return (v < lo) ? lo : (v > hi) ? hi : v;
}

class World {
 public:
  void addSociety(const Society& society) { societies_.push_back(society); }

  void simulateYear() {
    for (auto& society : societies_) {
      society.evolve();
    }
  }

  std::vector<Society>& getSocieties() { return societies_; }

  double predictWarOutcome(const War& war) {
    const Society& attacker = war.getAttacker();
    const Society& defender = war.getDefender();
    Terrain terrain = war.getTerrain();

    double attackerScore = calculateWarScore(attacker, terrain, true);
    double defenderScore = calculateWarScore(defender, terrain, false);

    // Normalize scores
    double totalScore = attackerScore + defenderScore;
    double attackerProbability = attackerScore / totalScore;

    // Add some randomness to the outcome
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);
    double randomFactor =
        dis(gen) * 0.2 - 0.1;  // Random factor between -0.1 and 0.1

    return clamp(attackerProbability + randomFactor, 0.0, 1.0);
  }

 private:
  std::vector<Society> societies_;
  double calculateWarScore(const Society& society, Terrain terrain,
                           bool isAttacker) {
    const MilitaryUnit& unit = society.getMilitaryUnit();

    double score = 0.0;

    // Base factors
    score += unit.getSize() * 0.3;
    score += unit.getTechnology() * 0.2;
    score += society.getTechnology() * 0.1;
    score += society.getTerrainFamiliarity(terrain) * 0.1;
    score += society.getStrategySkill() * 0.1;
    score += society.getDesperation() * 0.05;
    score += society.getNutrientAvailability() * 0.05;
    score += society.getSupplyLineEfficiency() * 0.05;
    score += unit.getMobility() * 0.05;

    // Terrain modifiers
    switch (terrain) {
      case Terrain::MOUNTAINS:
        score *=
            isAttacker ? 0.8 : 1.2;  // Defenders have advantage in mountains
        break;
      case Terrain::FOREST:
        score *=
            isAttacker ? 0.9 : 1.1;  // Slight defender advantage in forests
        break;
      case Terrain::URBAN:
        score *=
            isAttacker ? 0.7 : 1.3;  // Strong defender advantage in urban areas
        break;
      // Plains and desert are neutral
      default:
        break;
    }

    // Attacker/Defender modifiers
    score *= isAttacker ? 0.9 : 1.1;  // Slight defender advantage

    return score;
  }
};

PYBIND11_MODULE(individuals, m) {
  py::enum_<PoliticalBelief>(m, "PoliticalBelief")
      .value("AUTHORITARIANISM", PoliticalBelief::AUTHORITARIANISM)
      .value("LIBERALISM", PoliticalBelief::LIBERALISM)
      .value("SOCIALISM", PoliticalBelief::SOCIALISM)
      .value("CONSERVATISM", PoliticalBelief::CONSERVATISM)
      .value("ENVIRONMENTALISM", PoliticalBelief::ENVIRONMENTALISM);

  py::class_<Individual>(m, "Individual")
      .def(py::init<
           int, int, PoliticalBelief, double, const std::string&, double,
           double, const Personality&, const GeneticPredisposition&,
           const Environment&, const std::map<std::string, double>&,
           const std::map<std::string, std::string>&,
           const std::vector<Emotion>&, const std::map<std::string, double>&>())
      .def("get_intelligence", &Individual::getIntelligence)
      .def("get_age", &Individual::getAge)
      .def("get_political_belief", &Individual::getPoliticalBelief)
      .def("increment_age", &Individual::incrementAge)
      .def("set_political_belief", &Individual::setPoliticalBelief)
      .def("get_self_awareness", &Individual::getSelfAwareness)
      .def("get_type", &Individual::getType)
      .def("get_knowledge", &Individual::getKnowledge)
      .def("get_experience", &Individual::getExperience)
      .def("get_personality", &Individual::getPersonality,
           py::return_value_policy::reference)
      .def("get_genetic_predisposition", &Individual::getGeneticPredisposition,
           py::return_value_policy::reference)
      .def("get_environment", &Individual::getEnvironment,
           py::return_value_policy::reference);

  py::class_<Obstacle>(m, "Obstacle")
      .def(py::init<const std::string&, int>())
      .def("get_name", &Obstacle::getName)
      .def("get_difficulty", &Obstacle::getDifficulty)
      .def("get_progress", &Obstacle::getProgress)
      .def("is_overcome", &Obstacle::isOvercome);

  py::enum_<Terrain>(m, "Terrain")
      .value("PLAINS", Terrain::PLAINS)
      .value("MOUNTAINS", Terrain::MOUNTAINS)
      .value("FOREST", Terrain::FOREST)
      .value("DESERT", Terrain::DESERT)
      .value("URBAN", Terrain::URBAN);

  py::class_<MilitaryUnit>(m, "MilitaryUnit")
      .def(py::init<int, double, double>())
      .def("get_size", &MilitaryUnit::getSize)
      .def("get_technology", &MilitaryUnit::getTechnology)
      .def("get_mobility", &MilitaryUnit::getMobility);

  py::class_<War, Obstacle>(m, "War")
      .def(py::init<const std::string&, int, const Society&, const Society&,
                    Terrain>())
      .def("get_attacker", &War::getAttacker,
           py::return_value_policy::reference)
      .def("get_defender", &War::getDefender,
           py::return_value_policy::reference)
      .def("get_terrain", &War::getTerrain);

  py::class_<Society>(m, "Society")
      .def(py::init<const std::string&, int, const std::string&>())
      .def("add_individual", &Society::addIndividual)
      .def("evolve", &Society::evolve)
      .def("add_obstacle", &Society::addObstacle)
      .def("get_average_intelligence", &Society::getAverageIntelligence)
      .def("get_political_belief_distribution",
           &Society::getPoliticalBeliefDistribution)
      .def("get_most_popular_belief", &Society::getMostPopularBelief)
      .def("get_development_stage", &Society::getDevelopmentStage)
      .def("get_name", &Society::getName)
      .def("get_population_size", &Society::getPopulationSize)
      .def("get_government_type", &Society::getGovernmentType)
      .def("get_resources", &Society::getResources)
      .def("get_technology", &Society::getTechnology)
      .def("get_obstacles", &Society::getObstacles)
      .def("set_military_unit", &Society::setMilitaryUnit)
      .def("get_military_unit", &Society::getMilitaryUnit)
      .def("set_terrain_familiarity", &Society::setTerrainFamiliarity)
      .def("get_terrain_familiarity", &Society::getTerrainFamiliarity)
      .def("set_strategy_skill", &Society::setStrategySkill)
      .def("get_strategy_skill", &Society::getStrategySkill)
      .def("set_desperation", &Society::setDesperation)
      .def("get_desperation", &Society::getDesperation)
      .def("set_nutrient_availability", &Society::setNutrientAvailability)
      .def("get_nutrient_availability", &Society::getNutrientAvailability)
      .def("set_supply_line_efficiency", &Society::setSupplyLineEfficiency)
      .def("get_supply_line_efficiency", &Society::getSupplyLineEfficiency);

  py::class_<World>(m, "World")
      .def(py::init<>())
      .def("add_society", &World::addSociety)
      .def("simulate_year", &World::simulateYear)
      .def("get_societies", &World::getSocieties)
      .def("predict_war_outcome", &World::predictWarOutcome);

  py::class_<Personality>(m, "Personality")
      .def(py::init<>())
      .def_readwrite("traits", &Personality::traits)
      .def("getTrait", &Personality::getTrait);

  py::class_<Emotion>(m, "Emotion")
      .def(py::init<const std::string&, double>())
      .def_readwrite("name", &Emotion::name)
      .def_readwrite("intensity", &Emotion::intensity)
      .def("addInteraction", &Emotion::addInteraction)
      .def("getIntensity", &Emotion::getIntensity);

  py::class_<GeneticPredisposition>(m, "GeneticPredisposition")
      .def(py::init<>())
      .def_readwrite("genes", &GeneticPredisposition::genes)
      .def("getGene", &GeneticPredisposition::getGene);

  py::class_<Environment>(m, "Environment")
      .def(py::init<>())
      .def_readwrite("safety", &Environment::safety)
      .def_readwrite("stimulation", &Environment::stimulation)
      .def_readwrite("social", &Environment::social)
      .def_readwrite("nutrition", &Environment::nutrition)
      .def("getStimulation", &Environment::getStimulation);

  py::class_<NeuralNetwork>(m, "NeuralNetwork")
      .def(py::init<const std::vector<int>&>())
      .def("forward", &NeuralNetwork::forward)
      .def("initialize", &NeuralNetwork::initializeWeightsAndBiases)
      .def("train", &NeuralNetwork::train);

  py::class_<ConsciousnessSimulator>(m, "ConsciousnessSimulator")
      .def(py::init<double, std::string, int, double, double,
                    const Personality&, const GeneticPredisposition&,
                    const Environment&, const std::map<std::string, double>&,
                    const std::map<std::string, std::string>&,
                    const std::vector<Emotion>&,
                    const std::map<std::string, double>&>(),

           // Specify arguments as optional with default values
           py::arg("selfAwareness"), py::arg("type"), py::arg("age"),
           py::arg("knowledge"), py::arg("experience"), py::arg("personality"),
           py::arg("genetics"), py::arg("environment"),

           // Define optional arguments with defaults
           py::arg("cognitiveBiases") = std::map<std::string, double>(),
           py::arg("culturalContext") = std::map<std::string, std::string>(),
           py::arg("emotions") = std::vector<Emotion>(),
           py::arg("substanceEffects") = std::map<std::string, double>())
      .def("add_substance", &ConsciousnessSimulator::addSubstance)
      .def("update_physiological_state",
           &ConsciousnessSimulator::updatePhysiologicalState)
      .def("learn", &ConsciousnessSimulator::learn)
      .def("add_fear", &ConsciousnessSimulator::addFear)
      .def("remove_fear", &ConsciousnessSimulator::removeFear)
      .def("add_mental_illness", &ConsciousnessSimulator::addMentalIllness)
      .def("analyze_situation", &ConsciousnessSimulator::analyzeSituation)
      .def("respond_to_situation", &ConsciousnessSimulator::respondToSituation)
      .def("calculate_consciousness_level",
           &ConsciousnessSimulator::calculateConsciousnessLevel)
      .def("get_state", &ConsciousnessSimulator::getState)
      .def("update_emotions", &ConsciousnessSimulator::updateEmotions)
      .def("add_memory", &ConsciousnessSimulator::addMemory)
      .def("retrieve_memories", &ConsciousnessSimulator::retrieveMemories)
      .def("sleep", &ConsciousnessSimulator::sleep)
      .def("add_social_connection",
           &ConsciousnessSimulator::addSocialConnection)
      .def("social_interaction", &ConsciousnessSimulator::socialInteraction)
      .def("recognize_emotion", &ConsciousnessSimulator::recognizeEmotion);
}