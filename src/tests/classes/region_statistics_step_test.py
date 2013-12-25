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
from unittest.mock import mock_open
from unittest.mock import patch

import nibabel as nib # Necessary to mock the calls to it
import numpy as np
from src.classes.region_statistics_step import RegionStatisticsStep
from src.classes.aux.tensor_statistics import TensorStatistics

class RegionStatisticsStepTestCase(unittest.TestCase):
    def setUp(self):
        self.region_statistics_step = RegionStatisticsStep()

    def test_validate_args(self):
        sys.argv = ['']
        with self.assertRaises(SystemExit) as cm:
            self.region_statistics_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv = ['', 'not a file', 'not a file']
        with self.assertRaises(SystemExit) as cm:
            self.region_statistics_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv[1] = sys.path[0]+"/classes/region_statistics_step_test.py"
        with self.assertRaises(SystemExit) as cm:
            self.region_statistics_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv[2] = sys.path[0]+"/classes/region_statistics_step_test.py"
        self.assertTrue(self.region_statistics_step.validate_args())

    def test_load_data(self):
        sys.argv = ['', 'tensor', 'mask']

        loaded = Mock(return_value=True)
        loaded.shape = (1,1,3)
        nib.load = Mock(return_value=loaded)

        self.region_statistics_step.load_data()

        nib.load.assert_called_with('mask')

    def test_process_partition(self):
        mask = Mock(return_value=True)
        mask_data = np.zeros((1,1,3), dtype=np.uint64)
        mask_data[(0,0,1)] = 1
        mask_data[(0,0,0)] = 1
        mask.get_data = Mock(return_value=mask_data)
        self.region_statistics_step.mask = mask

        tensor = Mock(return_value=True)
        tensor_data = np.zeros((1,1,3,6), dtype=np.float64)
        tensor_data[(0,0,0)] = (1.0,1.0,1.0,1.0,1.0,1.0)
        tensor.get_data = Mock(return_value=tensor_data)
        self.region_statistics_step.tensor = tensor

        self.region_statistics_step.process_partition((0,1),(0,1),(0,3))

    def test_save(self):
        self.region_statistics_step.regions[1] = [(0,0,0)]
        self.region_statistics_step.md_results[1] = [1.0]
        self.region_statistics_step.fa_results[1] = [1.0]

        open_mock = mock_open()

        with patch('builtins.open', open_mock, create=True):
            self.region_statistics_step.save()

        open_mock.assert_called_with('region_statistics.txt', 'w')
