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

"""Container for NormalizationStep class"""

import sys                      # Makes possible to get the arguments
import nibabel as nib           # Lib for reading and writing Nifit1
import numpy as np              # Nibabel is based on Numpy
import math as m

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.tensor_indexes import TensorIndexes
from src.classes.aux.input_validators import validate_tensor_and_mask

class NormalizationStep(CPUParallelStep):
    """Extracts the given region from a compound mask"""

    def __init__(self):
        super(NormalizationStep, self).__init__()
        self.__min = float("inf")
        self.__max = float("-inf")
        self.__mask = np.zeros((0, 0, 0))         # pylint: disable=E1101
        self.__map = np.zeros((0, 0, 0)) # pylint: disable=E1101
        self.__normalized_map = np.zeros((0, 0, 0)) # pylint: disable=E1101

    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects two arguments: '+
                  ' tensor file; mask_file.',
                  file=sys.stderr)
            exit(1)
        return validate_tensor_and_mask(1, 2)

    def load_data(self):
        self.__map = nib.load(str(sys.argv[1]))
        self.__mask = nib.load(str(sys.argv[2]))
        self.shape = (self.__mask.shape[0],
                      self.__mask.shape[1],
                      self.__mask.shape[2])
        self.__normalized_map = np.zeros(self.shape, dtype=np.float32)

        map_data = self.__map.get_data()
        mask_data = self.__mask.get_data()

        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    if mask_data[(x,y,z)] == 1:
                        if self.__min > map_data[(x,y,z)]:
                            self.__min = map_data[(x,y,z)]
                        if self.__max < map_data[(x,y,z)]:
                            self.__max = map_data[(x,y,z)]

    def process_partition(self, x_range, y_range, z_range):
        map_data = self.__map.get_data()
        mask_data = self.__mask.get_data()

        denominator = (self.__max - self.__min)

        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    if mask_data[(x,y,z)] == 1:
                        self.queue.put(((x, y, z), (map_data[(x, y, z)] - self.__min)/denominator))

    def consume_product(self, product):
        self.__normalized_map[product[0]] = product[1]

    def save(self):
        file_prefix = sys.argv[1].split('/')[-1].split('.')[0]

        normalized_map_img = nib.Nifti1Image(self.__normalized_map,
                                             self.__mask.get_affine())

        normalized_map_img.to_filename("%s_normalized.nii.gz" % (file_prefix))