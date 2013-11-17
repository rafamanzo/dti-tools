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

from src.classes.isotropy_map_step import IsotropyMapStep

import nibabel as nib # Necessary to mock the calls to it
import numpy as np    # Necessary for assertions

class IsotropyMapStepTestCase(unittest.TestCase):
    def setUp(self):
        self.isotropy_map_step = IsotropyMapStep()

    def test_validate_args(self):
        sys.argv = ['']
        with self.assertRaises(SystemExit) as cm:
            self.isotropy_map_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv = ['', 'not a file', 'not a file', '0.75']
        with self.assertRaises(SystemExit) as cm:
            self.isotropy_map_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv[1] = sys.path[0]+"/classes/isotropy_map_step_test.py"
        with self.assertRaises(SystemExit) as cm:
            self.isotropy_map_step.validate_args()
        self.assertEqual(cm.exception.code, 1)

        sys.argv[2] = sys.path[0]+"/classes/isotropy_map_step_test.py"
        self.assertTrue(self.isotropy_map_step.validate_args())

    def test_load_data(self):
        sys.argv = ['', 'data', 'mask', '0.75']

        data = [[[1.0,0.0,1.0]]]
        loaded = Mock(return_value=True)
        loaded.get_data = Mock(return_value=data)
        loaded.shape = (1,1,3)
        nib.load = Mock(return_value=loaded)

        self.isotropy_map_step.load_data()

        nib.load.assert_called_with('mask')
        loaded.get_data.assert_called_with()

    def test_save(self):
        self.isotropy_map_step.isotropy_mask = [[[0,0,0]]]
        mask = Mock(return_value=True)
        mask.to_filename = Mock(return_value=True)
        nib.Nifti1Image = Mock(return_value=mask)

        self.isotropy_map_step.save()

        mask.to_filename.assert_called_with('isotropy_mask.nii.gz')

    def test_process_partition(self):
        self.isotropy_map_step.mask_data=[[[1,1,0]]]
        self.isotropy_map_step.tensor_data = [[[
                                                [1,1,1,1,1,1],
                                                [0.1,0.1,0.1,0.1,0.1,0.1],
                                                [1,1,1,1,1,1],
                                             ]]]
        self.isotropy_map_step.threshold = 0.5
        self.isotropy_map_step.isotropy_mask = [[[0,0,0]]]

        self.isotropy_map_step.process_partition((0,1),(0,1),(0,3))

        self.assertEquals(self.isotropy_map_step.isotropy_mask, [[[0,1,0]]])