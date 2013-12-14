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
from unittest.mock import Mock

from src.classes.aux.clustering.dbscan import DBSCAN

import numpy as np    # Necessary for assertions

class DBSCANTestCase(unittest.TestCase):
    def setUp(self):
        self.shape = (2,2,2)
        self.mask = np.ones(self.shape, dtype=np.int16)
        self.mask[1][1][1] = 0
        self.dbscan = DBSCAN(1,1,self.mask, self.shape)

    def test_neighbourhood_criteria(self):
        with self.assertRaises(NotImplementedError):
            self.dbscan.neighbourhood_criteria((0,0,0))

    def test_fit(self):
        expected_clusters = [
                                {
                                    (0,0,0), (1,0,0),
                                    (0,1,0), (1,1,0),
                                    (0,0,1), (1,0,1),
                                    (0,1,1)
                                }
                            ]
        expected_result_matrix = np.ones(self.shape, dtype=np.int16)
        expected_result_matrix[1][1][1] = -1
        self.dbscan.neighbourhood_criteria = Mock(return_value=True)

        actual_clusters, actual_result_matrix = self.dbscan.fit()
        self.assertEqual((expected_clusters, expected_result_matrix.any()), (actual_clusters, actual_result_matrix.any()))

        self.shape = (3,3,3)
        self.mask = np.zeros(self.shape, dtype=np.int16)
        self.mask[0][0][0] = 1
        self.mask[0][0][1] = 1
        self.mask[0][0][2] = 1
        self.dbscan = DBSCAN(1,3,self.mask, self.shape)
        self.dbscan.neighbourhood_criteria = Mock(return_value=True)
        expected_clusters = [{(0, 0, 1), (0, 0, 2)}]
        expected_result_matrix = np.ones(self.shape, dtype=np.int16)
        expected_result_matrix = expected_result_matrix*-1
        expected_result_matrix[0][0][1] = 1
        expected_result_matrix[0][0][2] = 1

        actual_clusters, actual_result_matrix = self.dbscan.fit()
        self.assertEqual((expected_clusters, expected_result_matrix.any()), (actual_clusters, actual_result_matrix.any()))