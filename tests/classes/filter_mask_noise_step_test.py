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

from src.classes.filter_mask_noise_step import FilterMaskNoiseStep

import nibabel as nib # Necessary to mock the calls to it
from src.classes.base.clustering.base.dbscan import DBSCAN # Necessary to mock the calls to it

class FilterMaskNoiseStepTestCase(unittest.TestCase):
    def setUp(self):
        self.filter_mask_noise_step = FilterMaskNoiseStep()

    def test_validate_args(self):
        sys.argv = ['']
        with self.assertRaises(SystemExit) as cm:
            self.filter_mask_noise_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv = ['', sys.path[0]+"/classes/filter_mask_noise_step_test.py", '1', '26']

        self.assertTrue(self.filter_mask_noise_step.validate_args())

    def test_load_data(self):
        sys.argv = ['', 'mask', '1', '26']

        data = [[[1.0,0.0,1.0]]]
        loaded = Mock(return_value=True)
        loaded.get_data = Mock(return_value=data)
        loaded.shape = (1,1,3)
        nib.load = Mock(return_value=loaded)

        self.filter_mask_noise_step.load_data()

        nib.load.assert_called_with('mask')
        loaded.get_data.assert_called_with()

    def test_process(self):
        self.filter_mask_noise_step.eps=1
        self.filter_mask_noise_step.min_pts=26
        self.filter_mask_noise_step.mask_data=[[[1,1,0]]]
        self.filter_mask_noise_step.shape=(1, 1, 3)
        self.filter_mask_noise_step.filtered_mask=[[[0,0,0]]]

        DBSCAN.fit = Mock(return_value=([], [[[0,1,0]]]))

        self.filter_mask_noise_step.process()

        DBSCAN.fit.assert_called_with()

    def test_save(self):
        sys.argv = ['', 'mask', '1', '26']

        self.filter_mask_noise_step.filtered_mask = [[[0,0,0]]]
        mask = Mock(return_value=True)
        mask.to_filename = Mock(return_value=True)
        nib.Nifti1Image = Mock(return_value=mask)

        self.filter_mask_noise_step.save()

        mask.to_filename.assert_called_with('filtered_mask')
