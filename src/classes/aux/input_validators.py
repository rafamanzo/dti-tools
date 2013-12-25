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

"""Input validation functions"""

import sys # Makes possible to get the arguments
import os  # File existence checking

def validate_tensor(argv_index):
    """Checks if the given tensor file do exists"""

    if not os.path.isfile(str(sys.argv[argv_index])):
        print('The given tensor file does not exists:\n%s'%
              str(sys.argv[1]), file=sys.stderr)
        exit(1)

    return True

def validate_mask(argv_index):
    """Checks if the given mask file do exists"""

    if not os.path.isfile(str(sys.argv[argv_index])):
        print('The given mask file does not exists:\n%s'%
              str(sys.argv[1]), file=sys.stderr)
        exit(1)

    return True

def validate_tensor_and_mask(argv_tensor_index, argv_mask_index):
    """Checks both tensor and mask file existence"""

    return (validate_tensor(argv_tensor_index) and
            validate_mask(argv_mask_index))
