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

from src.classes.fa_clustering_step import FAClusteringStep

import nibabel as nib # Necessary to mock the calls to it
import numpy as np
from src.classes.aux.clustering.fa_dbscan import FADBSCAN # Necessary to mock the calls to it

class FAClusteringStepTestCase(unittest.TestCase):
    def setUp(self):
        self.fa_clustering_step = FAClusteringStep()

    def test_validate_args(self):
        sys.argv = ['']
        with self.assertRaises(SystemExit) as cm:
            self.fa_clustering_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv = ['', 'not a file', 'not a file', '1', '26', '0.1']
        with self.assertRaises(SystemExit) as cm:
            self.fa_clustering_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv[1] = sys.path[0]+"/classes/fa_clustering_step_test.py"
        with self.assertRaises(SystemExit) as cm:
            self.fa_clustering_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv[2] = sys.path[0]+"/classes/fa_clustering_step_test.py"
        self.assertTrue(self.fa_clustering_step.validate_args())

    def test_load_data(self):
        sys.argv = ['', 'tensor', 'mask', '1', '26', '0.1']

        data = [[[1.0,0.0,1.0]]]
        loaded = Mock(return_value=True)
        loaded.get_data = Mock(return_value=data)
        loaded.shape = (1,1,3)
        nib.load = Mock(return_value=loaded)

        self.fa_clustering_step.load_data()

        nib.load.assert_called_with('mask')
        loaded.get_data.assert_called_with()

    def test_process(self):
        self.fa_clustering_step.eps=1
        self.fa_clustering_step.min_pts=0
        self.fa_clustering_step.mask_data=[[[1,1,0]]]
        self.fa_clustering_step.tensor = np.zeros((1,1,1,6), dtype=np.int16)
        self.fa_clustering_step.tensor[0][0][0][0] = 1
        self.fa_clustering_step.max_fa_difference = 0.1
        self.fa_clustering_step.shape=(1, 1, 3)

        FADBSCAN.fit = Mock(return_value=([[(0,1,0)]], [[[0,1,0]]]))

        self.fa_clustering_step.process()

        FADBSCAN.fit.assert_called_with()

    def test_save(self):
        sys.argv = ['', 'tensor', 'mask', '1', '26', '0.1']

        self.fa_clustering_step.shape=(1, 1, 3)
        self.fa_clustering_step.clusters = [[(0,0,0)]]
        mask = Mock(return_value=True)
        mask.to_filename = Mock(return_value=True)
        nib.Nifti1Image = Mock(return_value=mask)

        self.fa_clustering_step.save()

        mask.to_filename.assert_called_with('fa_clustered_mask')
