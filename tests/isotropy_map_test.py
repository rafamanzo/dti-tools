import unittest
import 

class IsotropyMapTestCase(unittest.TestCase):
  def test_mean_diffusivity(self):
    self.assertEqual(mean_diffusivity((1,0,0,1,0,1)))