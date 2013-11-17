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
sys.path.append(sys.path[0][:-22])

import unittest
from unittest.mock import MagicMock

from src.classes.base.step import Step

class StepTestCase(unittest.TestCase):
    def setUp(self):
        self.step = Step()

    def test_validate_args(self):
        self.assertTrue(self.step.validate_args())

    def test_load_data(self):
        self.assertTrue(self.step.load_data())

    def test_save(self):
        self.assertTrue(self.step.save())

    def test_process(self):
        with self.assertRaises(NotImplementedError):
            self.step.process()

    def test_run(self):
        self.step.validate_args = MagicMock(return_value=True)
        self.step.load_data = MagicMock(return_value=True)
        self.step.process = MagicMock(return_value=True)
        self.step.save = MagicMock(return_value=True)

        self.step.run()

        self.step.validate_args.assert_called_with()
        self.step.load_data.assert_called_with()
        self.step.process.assert_called_with()
        self.step.save.assert_called_with()

        self.step.validate_args = MagicMock(return_value=False)
        self.step.load_data = MagicMock(return_value=True)
        self.step.process = MagicMock(return_value=True)
        self.step.save = MagicMock(return_value=True)

        self.step.run()

        self.step.validate_args.assert_called_with()
        self.assertFalse(self.step.load_data.called)
        self.assertFalse(self.step.process.called)
        self.assertFalse(self.step.save.called)
