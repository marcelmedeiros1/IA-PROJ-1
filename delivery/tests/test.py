import unittest
from models.model import *
from utils.utils import *


# Dummy test to me removed
class TestUtils(unittest.TestCase):
    def test_get_x_from_valid_location(self):
        # Suponha que uma localização válida seja (latitude, longitude)
        location = Location(100, -8.611)
        expected_x = 100  # Substitua pelo valor esperado correspondente
        result = get_x_from_location(location)
        self.assertEqual(result, expected_x, "A função não retornou o valor esperado para uma localização válida.")

if __name__ == '__main__':
    unittest.main()
