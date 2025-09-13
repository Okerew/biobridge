import unittest
from biobridge.enviromental.infection import Infection, InfectionType, Cell


class MockCell:
    def __init__(self, name: str):
        self.name = name
        self.health = 100


class TestInfection(unittest.TestCase):
    def setUp(self):
        self.infection = Infection("Test Infection", InfectionType.VIRUS, 0.5, "ATCG")
        self.cell = Cell("Test Cell", "Human", health=100)

    def test_initialization(self):
        self.assertEqual(self.infection.name, "Test Infection")
        self.assertEqual(self.infection.infection_type, InfectionType.VIRUS)
        self.assertEqual(self.infection.spread_rate, 0.5)
        self.assertEqual(self.infection.genetic_code, "ATCG")
        self.assertEqual(self.infection.infected_cells, [])

    def test_infect(self):
        # Test multiple times due to randomness
        successes = sum(self.infection.infect(self.cell) for _ in range(1000))
        # Expect roughly 50% success rate
        self.assertTrue(400 < successes < 600)

    def test_replicate(self):
        self.infection.infected_cells.append(self.cell.name)
        initial_health = self.cell.health
        self.infection.replicate(self.cell)
        self.assertLess(self.cell.health, initial_health)
        self.assertGreaterEqual(self.cell.health, 0)

    def test_exit_cell(self):
        self.infection.infected_cells.append(self.cell.name)
        # Test multiple times due to randomness
        exits = [self.infection.exit_cell(self.cell) for _ in range(10000)]
        successful_exits = [e for e in exits if e is not None]

        if successful_exits:
            new_infection = successful_exits[0]
            self.assertIsInstance(new_infection, Infection)
            self.assertEqual(new_infection.infection_type, self.infection.infection_type)
            self.assertEqual(new_infection.spread_rate, self.infection.spread_rate)
            self.assertEqual(new_infection.genetic_code, self.infection.genetic_code)

    def test_mutate_spread_rate(self):
        initial_rate = self.infection.spread_rate
        for _ in range(1000):
            self.infection.mutate()
        # After many mutations, spread_rate should still be between 0 and 1
        self.assertGreaterEqual(self.infection.spread_rate, 0)
        self.assertLessEqual(self.infection.spread_rate, 1)
        # It's highly unlikely the spread_rate remains exactly the same after 1000 mutations
        self.assertNotEqual(self.infection.spread_rate, initial_rate)

    def test_mutate_genetic_code(self):
        initial_code = self.infection.genetic_code
        for _ in range(100):
            self.infection.mutate()
        # After mutations, the length of the genetic code should remain the same
        self.assertEqual(len(self.infection.genetic_code), len(initial_code))
        # It's highly unlikely the genetic_code remains exactly the same after 100 mutations
        self.assertNotEqual(self.infection.genetic_code, initial_code)

    def test_describe(self):
        description = self.infection.describe()
        self.assertIn(self.infection.name, description)
        self.assertIn(self.infection.infection_type.value, description)
        self.assertIn(str(self.infection.spread_rate), description)
        self.assertIn(self.infection.genetic_code, description)


if __name__ == '__main__':
    unittest.main()
