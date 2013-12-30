# This file is part of Improving Tractogrophy
# Copyright (C) 2013 it's respectives authors (please see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
sys.path.append(sys.path[0][:-17])

import unittest

from src.classes.aux.tensor_statistics import TensorStatistics

import math as m # Float point assertions

class TensorStatisticsTestCase(unittest.TestCase):
    def test_mean_diffusivity(self):
        tensor_statistics = TensorStatistics((1.0, 0.0, 0.0, 1.0, 0.0, 1.0))

        self.assertEqual(tensor_statistics.mean_diffusivity(), 1.0)

    def test_fractional_anisotropy(self):
        error = 0.000000000000001
        tensor_statistics = TensorStatistics((1.0, 0.0, 0.0, 1.0, 0.0, 1.0))

        self.assertTrue(m.fabs(tensor_statistics.fractional_anisotropy() - 0.0) <= error)

        tensor_statistics = TensorStatistics((1.0, 0.0, 0.0, 0.0, 0.0, 0.0))

        self.assertTrue(m.fabs(tensor_statistics.fractional_anisotropy() - 1.0) <= error)

        tensor_statistics = TensorStatistics((0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

        self.assertTrue(m.fabs(tensor_statistics.fractional_anisotropy() - 0.0) <= error)

    def test_radial_diffusivity(self):
        error = 0.000000000000001
        tensor_statistics = TensorStatistics((3.0, 0.0, 0.0, 2.0, 0.0, 1.0))

        self.assertTrue(m.fabs(tensor_statistics.radial_diffusivity() - 1.5) <= error)

    def test_toroidal_volume(self):
        error = 0.000000000000001
        tensor_statistics = TensorStatistics((1.0, 0.0, 0.0, 1.0, 0.0, 1.0))

        self.assertTrue(m.fabs(tensor_statistics.toroidal_volume() - ((3.0*m.pi)/6.0)) <= error)

    def test_toroidal_curvature(self):
        error = 0.000000000000001
        tensor_statistics = TensorStatistics((1.0, 0.0, 0.0, 1.0, 0.0, 1.0))

        self.assertTrue(m.fabs(tensor_statistics.toroidal_curvature() - 3.368420076723892) <= error)