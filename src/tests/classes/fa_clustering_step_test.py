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
sys.path.append(sys.path[0][:-18])

import unittest
from unittest.mock import Mock
from unittest.mock import patch

from src.classes.fa_clustering_step import FAClusteringStep

import nibabel as nib # Necessary to mock the calls to it
import numpy as np
from src.classes.aux.clustering.fa_dbscan import FADBSCAN # Necessary to mock the calls to it

class FAClusteringStepTestCase(unittest.TestCase):
    def setUp(self):
        self.fa_clustering_step = FAClusteringStep()

    def test_get_cluster(self):
        mask_data = [[[1,1,0]]]
        mask_shape = (1, 1, 3)
        mask = Mock(return_value=True)
        mask.get_data = Mock(return_value=mask_data)
        mask.shape = mask_shape

        tensor_data = np.zeros((1,1,1,6), dtype=np.int16)
        tensor_data[0][0][0][0] = 1
        tensor = Mock(return_value=True)
        tensor.get_data = Mock(return_value=tensor_data)

        self.fa_clustering_step.eps = 1
        self.fa_clustering_step.min_pts = 0
        self.fa_clustering_step.mask = mask
        self.fa_clustering_step.tensor = tensor
        self.fa_clustering_step.max_fa_difference = 0.1

        fa_dbscan_mock = Mock()

        with patch('__main__.FADBSCAN', fa_dbscan_mock, create=True):
            self.fa_clustering_step.get_clusterer()
