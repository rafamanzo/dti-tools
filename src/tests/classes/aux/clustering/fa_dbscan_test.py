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

from src.classes.aux.clustering.fa_dbscan import FADBSCAN

import numpy as np    # Necessary for assertions

class FADBSCANTestCase(unittest.TestCase):
    def setUp(self):
        self.shape = (2,2,2)
        self.mask = np.ones(self.shape, dtype=np.int16)
        self.tensor = np.zeros((2,2,2,6), dtype=np.int16)
        self.tensor[0][0][0][0] = 1
        self.mask[1][1][1] = 0
        self.max_fa_difference = 0.1
        self.mask_dbscan = FADBSCAN(1,1,self.mask, self.shape, self.tensor, self.max_fa_difference)

    def test_neighbourhood_criteria(self):
        self.assertTrue(self.mask_dbscan.neighbourhood_criteria((0,0,0), (0,0,0)))
        self.assertFalse(self.mask_dbscan.neighbourhood_criteria((0,0,0), (1,0,0)))