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
sys.path.append(sys.path[0][:-17])

import unittest

from src.classes.aux.input_validators import validate_mask, validate_tensor, validate_tensor_and_mask

class InputValidatorsTestCase(unittest.TestCase):
    def test_validate_tensor(self):
        sys.argv = ['', 'not a file']
        with self.assertRaises(SystemExit) as cm:
            validate_tensor(1)
        self.assertEqual(cm.exception.code, 1)

        sys.argv[1] = sys.argv[1] = sys.path[0]+"/classes/aux/input_validators_test.py"
        self.assertTrue(validate_tensor(1))

    def test_validate_mask(self):
        sys.argv = ['', 'not a file']
        with self.assertRaises(SystemExit) as cm:
            validate_mask(1)
        self.assertEqual(cm.exception.code, 1)

        sys.argv[1] = sys.argv[1] = sys.path[0]+"/classes/aux/input_validators_test.py"
        self.assertTrue(validate_mask(1))

    def test_validate_tensor_and_mask(self):
        sys.argv = ['', sys.path[0]+"/classes/aux/input_validators_test.py", sys.path[0]+"/classes/aux/input_validators_test.py"]

        self.assertTrue(validate_tensor_and_mask(1,2))
