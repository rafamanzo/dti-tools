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

from src.classes.base.threshold_map_step import ThresholdMapStep

import nibabel as nib # Necessary to mock the calls to it
import numpy as np    # Necessary for assertions

class ThresholdMapStepTestCase(unittest.TestCase):
    def setUp(self):
        self.threshold_map_step = ThresholdMapStep("th")

    def test_validate_args(self):
        sys.argv = ['']
        with self.assertRaises(SystemExit) as cm:
            self.threshold_map_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv = ['', sys.path[0]+"/classes/base/threshold_map_step_test.py", sys.path[0]+"/classes/base/threshold_map_step_test.py", '0.75']
        
        self.assertTrue(self.threshold_map_step.validate_args())

    def test_load_data(self):
        sys.argv = ['', 'data', 'mask', '0.75']

        data = [[[1.0,0.0,1.0]]]
        loaded = Mock(return_value=True)
        loaded.get_data = Mock(return_value=data)
        loaded.shape = (1,1,3)
        nib.load = Mock(return_value=loaded)

        self.threshold_map_step.load_data()

        nib.load.assert_called_with('mask')
        loaded.get_data.assert_called_with()

    def test_save(self):
        self.threshold_map_step.threshold_mask = [[[0,0,0]]]
        mask = Mock(return_value=True)
        mask.to_filename = Mock(return_value=True)
        nib.Nifti1Image = Mock(return_value=mask)

        self.threshold_map_step.save()

        mask.to_filename.assert_called_with('th_mask.nii.gz')

    def test_check_for_threshold(self):
        with self.assertRaises(NotImplementedError):
            self.threshold_map_step.check_for_threshold((0,0,0,0,0,0))

    def test_process_partition(self):
        self.threshold_map_step.check_for_threshold = Mock(return_value=True)
        self.threshold_map_step.mask_data=[[[1,1,0]]]
        self.threshold_map_step.tensor_data = [[[
                                                    [1,1,1,1,1,1],
                                                    [0.1,0.1,0.1,0.1,0.1,0.1],
                                                    [1,1,1,1,1,1],
                                                 ]]]
        self.threshold_map_step.threshold = 0.5
        self.threshold_map_step.threshold_mask = [[[0,0,0]]]

        self.threshold_map_step.process_partition((0,1),(0,1),(0,3))

        self.assertEqual(self.threshold_map_step.threshold_mask, [[[1,1,0]]])

        # Test the other branch of execution
        self.threshold_map_step.check_for_threshold = Mock(return_value=False)
        self.threshold_map_step.mask_data=[[[1,1,0]]]
        self.threshold_map_step.tensor_data = [[[
                                                    [1,1,1,1,1,1],
                                                    [0.1,0.1,0.1,0.1,0.1,0.1],
                                                    [1,1,1,1,1,1],
                                                 ]]]
        self.threshold_map_step.threshold = 0.5
        self.threshold_map_step.threshold_mask = [[[0,0,0]]]
        
        self.threshold_map_step.process_partition((0,1),(0,1),(0,3))

        self.assertEqual(self.threshold_map_step.threshold_mask, [[[0,0,0]]])