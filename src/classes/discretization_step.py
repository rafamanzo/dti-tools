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

"""Container for DiscretizationStep class"""

import sys                      # Makes possible to get the arguments
import nibabel as nib           # Lib for reading and writing Nifit1
import numpy as np              # Nibabel is based on Numpy
import math as m

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.input_validators import validate_mask

class DiscretizationStep(CPUParallelStep):
    """Extracts the given region from a compound mask"""

    def __init__(self):
        super(DiscretizationStep, self).__init__()
        self.__coefficient = 1
        self.__map = np.zeros((0, 0, 0))         # pylint: disable=E1101
        self.__discretized = np.zeros((0, 0, 0, 0)) # pylint: disable=E1101

    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects two arguments: '+
                  ' map file; multiplication coefficient.',
                  file=sys.stderr)
            exit(1)
        return validate_mask(1)

    def load_data(self):
        self.__map = nib.load(str(sys.argv[1]))
        self.__coefficient = int(sys.argv[2])
        self.shape = (self.__map.shape[0],
                      self.__map.shape[1],
                      self.__map.shape[2])
        self.__discretized = np.zeros(self.shape, dtype=np.uint32)

    def process_partition(self, x_range, y_range, z_range):
        map_data = self.__map.get_data()

        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    self.queue.put(((x, y, z), m.floor(map_data[(x, y, z)] * self.__coefficient)))

    def consume_product(self, product):
        self.__discretized[product[0]] = product[1]

    def save(self):
        file_prefix = sys.argv[1].split('/')[-1].split('.')[0]

        extracted_mask_img = nib.Nifti1Image(self.__discretized,
                                             self.__map.get_affine())

        extracted_mask_img.to_filename("%s_discretized_by_%d.nii.gz" % (file_prefix,
                                                                self.__coefficient))