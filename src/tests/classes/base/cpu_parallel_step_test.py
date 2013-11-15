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
from unittest.mock import MagicMock

from src.classes.base.cpu_parallel_step import CPUParallelStep

class CPUParallelStepTestCase(unittest.TestCase):
  def setUp(self):
    self.cpu_parallel_step = CPUParallelStep()

  def test_process_partition(self):
    with self.assertRaises(NotImplementedError):
      self.cpu_parallel_step.process_partition((0,1), (0,2), (0,3))