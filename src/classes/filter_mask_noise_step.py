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

"""Container for IsotropyMapStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

import sys                    # Makes possible to get the arguments
import os                     # File existence checking
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy

from src.classes.base.step import Step    # Base class
from src.classes.aux.dbscan import DBSCAN # Algorithm used for clustering 
                                          #   and noise reduction

class FilterMaskNoiseStep(Step):
    def validate_args(self):
        if len(sys.argv) != 4:
            print('This program expects three arguments: mask file;'+
                  ' DBSCAN eps; and DBSCAN min_pts.',
                  file=sys.stderr)
            exit(1)
        elif not os.path.isfile(str(sys.argv[1])):
            print('The given mask file does not exists:\n%s'%
                  str(sys.argv[1]), file=sys.stderr)
            exit(1)
        return True