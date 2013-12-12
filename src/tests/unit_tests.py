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
sys.path.append(sys.path[0][:-9])

import unittest

from src.tests.classes.base.step_test import StepTestCase
from src.tests.classes.base.cpu_parallel_step_test import CPUParallelStepTestCase
from src.tests.classes.isotropy_map_step_test import IsotropyMapStepTestCase
from src.tests.classes.filter_mask_noise_step_test import FilterMaskNoiseStepTestCase
from src.tests.classes.aux.dbscan_test import DBSCANTestCase

class UnitTestsSuite(unittest.TestSuite):
    def __init__(self):
        self.addTest(StepTestCase())
        self.addTest(CPUParallelStepTestCase())
        self.addTest(IsotropyMapStepTestCase())
        self.addTest(FilterMaskNoiseStepTestCase())
        self.addTest(DBSCANTestCase())

if __name__ == '__main__':
    unittest.main()