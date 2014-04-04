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

"""Container for RegionStatisticsStep class"""

import sys                      # Makes possible to get the arguments
import nibabel as nib           # Lib for reading and writing Nifit1
import numpy as np              # Nibabel is based on Numpy

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.input_validators import validate_mask

class CropMaskStep(CPUParallelStep):
    def __init__(self):
        super(CropMaskStep, self).__init__()
        self.mask = np.zeros((0, 0, 0))      # pylint: disable=E1101
        self.shape = (0, 0, 0)
        self.croped_mask = [[[]]]
        self.__x_start = -1
        self.__x_end = -1
        self.__y_start = -1
        self.__y_end = -1
        self.__z_start = -1
        self.__z_end = -1

    def validate_args(self):
        if len(sys.argv) != 8:
            print('This program expects seven arguments: mask file;'+
                  ' start X; end X; start Y; end Y; start Z; end Z.',
                  file=sys.stderr)
            exit(1)
        return validate_mask(1)

    def load_data(self):
        self.mask = nib.load(str(sys.argv[1]))
        self.shape = (self.mask.shape[0],
                      self.mask.shape[1],
                      self.mask.shape[2])
        self.croped_mask = np.zeros(self.shape, np.uint32)

        self.__x_start = int(sys.argv[2])
        self.__x_end = int(sys.argv[3])
        self.__y_start = int(sys.argv[4])
        self.__y_end = int(sys.argv[5])
        self.__z_start = int(sys.argv[6])
        self.__z_end = int(sys.argv[7])

    def process_partition(self, x_range, y_range, z_range):
        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    if (self.mask.get_data()[(x, y, z)] > 0 and
                        (x >= self.__x_start and x <= self.__x_end) and
                        (y >= self.__y_start and y <= self.__y_end) and
                        (z >= self.__z_start and z <= self.__z_end)):
                        self.queue.put((x, y, z))

    def consume_product(self, product):
        self.croped_mask[product] = self.mask.get_data()[product]

    def save(self):
        file_prefix = sys.argv[1].split('/')[-1].split('.')[0]
        croped_img = nib.Nifti1Image(
                            self.croped_mask, # pylint: disable=E1101
                            self.mask.get_affine())    # pylint: disable=E1101
        croped_img.to_filename('%s_croped.nii.gz'%file_prefix)
