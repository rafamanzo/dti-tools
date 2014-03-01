# This file is part of Improving Tractogrophy
# Copyright (C) 2013-2014 it's respectives authors (please see the AUTHORS file)
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

from src.classes.tensor_statistics_clustering_step import TensorStatisticsClusteringStep

import nibabel as nib # Necessary to mock the calls to it
import numpy as np

class TensorStatisticsClusteringStepTestCase(unittest.TestCase):
    def setUp(self):
        self.tensor_statistics_clustering_step = TensorStatisticsClusteringStep("tt")

    def test_validate_args(self):
        sys.argv = ['']
        with self.assertRaises(SystemExit) as cm:
            self.tensor_statistics_clustering_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv = ['', sys.path[0]+"/../tests/classes/tensor_statistics_clustering_step_test.py", sys.path[0]+"/../tests/classes/tensor_statistics_clustering_step_test.py", '1', '26', '0.1']
        self.assertTrue(self.tensor_statistics_clustering_step.validate_args())

    def test_load_data(self):
        sys.argv = ['', 'tensor', 'mask', '1', '26', '0.1']

        loaded = Mock(return_value=True)
        nib.load = Mock(return_value=loaded)

        self.tensor_statistics_clustering_step.load_data()

        nib.load.assert_called_with('mask')

    def test_get_clusterer(self):
        with self.assertRaises(NotImplementedError):
            self.tensor_statistics_clustering_step.get_clusterer()

    def test_process(self):
        clusterer = Mock(return_value=True)
        clusterer.fit = Mock(return_value=([],[]))
        self.tensor_statistics_clustering_step.get_clusterer = Mock(return_value=clusterer)

        self.tensor_statistics_clustering_step.process()

        clusterer.fit.assert_called_with()

    def test_save(self):
        sys.argv = ['', 'tensor', 'mask', '1', '26', '0.1']

        mask_shape = (1, 1, 3)
        mask = Mock(return_value=True)
        mask.shape = mask_shape
        self.tensor_statistics_clustering_step.mask = mask
        tensor = Mock(return_value=True)
        tensor.get_affine = Mock(return_value=np.eye(4))
        self.tensor_statistics_clustering_step.tensor = tensor
        self.tensor_statistics_clustering_step.clusters = [[(0,0,0)]]
        mask_img = Mock(return_value=True)
        mask_img.to_filename = Mock(return_value=True)
        nib.Nifti1Image = Mock(return_value=mask_img)

        self.tensor_statistics_clustering_step.save()

        mask_img.to_filename.assert_called_with('tt_clustered_mask')
