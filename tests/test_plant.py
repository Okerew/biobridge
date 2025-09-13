import unittest
from biobridge.genes.dna import DNA
from biobridge.definitions.organ import Organ, Tissue
from biobridge.definitions.plant import Plant


class TestPlant(unittest.TestCase):
    def setUp(self):
        dna = DNA("ATCG" * 25)  # 100 base pairs
        self.plant = Plant("Test Plant", dna)
        tissues = [Tissue("Leaf", "leaf"), Tissue("Root", "root")]
        # Add some organs
        leaf = Organ("Leaf", tissues)
        root = Organ("Root", tissues)
        self.plant.add_leaf(leaf)
        self.plant.add_root(root)

    def test_initialization(self):
        self.assertEqual(self.plant.name, "Test Plant")
        self.assertEqual(self.plant.sunlight_exposure, 0.0)
        self.assertEqual(self.plant.water_level, 50.0)
        self.assertEqual(self.plant.nutrients, 50.0)
        self.assertEqual(self.plant.growth_rate, 0.05)

    def test_update(self):
        external_factors = [("sunlight", 10), ("water", 5), ("nutrients", 3)]
        self.plant.update(external_factors)

        self.assertEqual(self.plant.sunlight_exposure, 0)  # Should reset after photosynthesis
        self.assertGreater(self.plant.water_level, 50.0)
        self.assertGreater(self.plant.nutrients, 50.0)

    def test_grow(self):
        self.plant.water_level = 100
        self.plant.nutrients = 100
        self.plant.energy = 100
        initial_description = self.plant.describe()

        self.plant.grow()

        self.assertLess(self.plant.water_level, 100)
        self.assertLess(self.plant.nutrients, 100)
        self.assertLess(self.plant.energy, 100)
        self.assertNotEqual(initial_description, self.plant.describe())

    def test_json_serialization(self):
        json_str = self.plant.to_json()
        new_plant = Plant.from_json(json_str)

        self.assertEqual(self.plant.name, new_plant.name)
        self.assertEqual(self.plant.sunlight_exposure, new_plant.sunlight_exposure)
        self.assertEqual(self.plant.water_level, new_plant.water_level)
        self.assertEqual(self.plant.nutrients, new_plant.nutrients)
        self.assertEqual(self.plant.growth_rate, new_plant.growth_rate)


if __name__ == '__main__':
    unittest.main()
