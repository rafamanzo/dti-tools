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

"""Container for NormalizedEigenvaluesMapStep class"""

import sys                      # Makes possible to get the arguments
import nibabel as nib           # Lib for reading and writing Nifit1
import numpy as np              # Nibabel is based on Numpy
import math as m

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.tensor_indexes import TensorIndexes
from src.classes.aux.input_validators import validate_tensor_and_mask

class NormalizedEigenvaluesMapStep(CPUParallelStep):
    """Extracts the given region from a compound mask"""

    def __init__(self):
        super(NormalizedEigenvaluesMapStep, self).__init__()
        self.__coefficient = 1
        self.__mask = np.zeros((0, 0, 0))         # pylint: disable=E1101
        self.__tensor = np.zeros((0, 0, 0, 0)) # pylint: disable=E1101
        self.__eigenvalues_map = np.zeros((0, 0, 0, 0)) # pylint: disable=E1101

    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects two arguments: '+
                  ' tensor file; mask_file.',
                  file=sys.stderr)
            exit(1)
        return validate_tensor_and_mask(1, 2)

    def load_data(self):
        self.__tensor = nib.load(str(sys.argv[1]))
        self.__mask = nib.load(str(sys.argv[2]))
        self.shape = (self.__mask.shape[0],
                      self.__mask.shape[1],
                      self.__mask.shape[2])
        self.__eigenvalues_map = np.zeros(self.shape + (3,), dtype=np.float32)
        self.__min = float("inf")
        self.__max = float("-inf")

    def process_partition(self, x_range, y_range, z_range):
        tensor_data = self.__tensor.get_data()
        mask_data = self.__mask.get_data()

        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    if mask_data[(x,y,z)] == 1:
                        eigenvalues, _ = TensorIndexes(tensor_data[(x, y, z)]).eigensystem()
                        self.queue.put(((x, y, z), eigenvalues))

    def consume_product(self, product):
        self.__eigenvalues_map[product[0]] = product[1]

    def save(self):
        self.__normalize()
        extracted_mask_img = nib.Nifti1Image(self.__eigenvalues_map,
                                             self.__mask.get_affine())

        extracted_mask_img.to_filename("eigenvalues_map.nii.gz")

    def __normalize(self):
        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    for u in range(0, 3): # pylint: disable=C0103,C0301
                        if self.__min > self.__eigenvalues_map[(x,y,z,u)]:
                            self.__min = self.__eigenvalues_map[(x,y,z,u)]
                        if self.__max < self.__eigenvalues_map[(x,y,z,u)]:
                            self.__max = self.__eigenvalues_map[(x,y,z,u)]

        denominator = self.__max - self.__min

        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    for u in range(0, 3): # pylint: disable=C0103,C0301
                        self.__eigenvalues_map[(x,y,z,u)] = (self.__eigenvalues_map[(x,y,z,u)] - self.__min)/denominator