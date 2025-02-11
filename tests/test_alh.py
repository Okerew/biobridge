import unittest
from biobridge.tools.alh import AutomatedLiquidHandler


class TestAutomatedLiquidHandler(unittest.TestCase):
    def setUp(self):
        self.handler = AutomatedLiquidHandler(num_channels=8, max_volume=1000)

    def test_move_to(self):
        self.handler.move_to(10, 20)
        self.assertEqual(self.handler.position, (10, 20))

    def test_aspirate_and_dispense(self):
        self.handler.change_tip(1)
        self.handler.aspirate(500, 1)
        self.assertEqual(self.handler.get_current_volume(1), 500)

        self.handler.dispense(200, 1)
        self.assertEqual(self.handler.get_current_volume(1), 300)

    def test_change_tip(self):
        self.handler.change_tip(1)
        self.assertTrue(self.handler.tips_attached[0])

    def test_wash_tip(self):
        self.handler.change_tip(1)
        self.handler.aspirate(500, 1)
        self.handler.wash_tip(1)
        self.assertEqual(self.handler.get_current_volume(1), 0)

    def test_get_status(self):
        self.handler.change_tip(1)
        self.handler.aspirate(500, 1)
        status = self.handler.get_status()
        self.assertEqual(status['position'], (0, 0))
        self.assertEqual(status['current_volume'], [500, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(status['tips_attached'], [True, False, False, False, False, False, False, False])

    def test_invalid_channel(self):
        with self.assertRaises(ValueError):
            self.handler.aspirate(500, 9)

    def test_exceed_max_volume(self):
        with self.assertRaises(ValueError):
            self.handler.change_tip(1)
            self.handler.aspirate(1500, 1)

    def test_no_tip_attached(self):
        with self.assertRaises(ValueError):
            self.handler.aspirate(500, 1)


if __name__ == '__main__':
    unittest.main()
