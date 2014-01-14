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

from src.classes.md_threshold_map_step import MDThresholdMapStep

class MDThresholdMapStepTestCase(unittest.TestCase):
    def setUp(self):
        self.md_threshold_map_step = MDThresholdMapStep()

    def test_check_threshold_for(self):
        self.md_threshold_map_step.threshold = 0.5

        self.assertFalse(self.md_threshold_map_step.check_for_threshold((1,1,1,1,1,1)))
        self.assertTrue(self.md_threshold_map_step.check_for_threshold((1,1,1,0.25,1,0.25)))