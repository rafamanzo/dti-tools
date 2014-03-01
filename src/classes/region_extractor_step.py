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

"""Container for RegionExtractorStep class"""

import sys                      # Makes possible to get the arguments
import nibabel as nib           # Lib for reading and writing Nifit1
import numpy as np              # Nibabel is based on Numpy

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.input_validators import validate_mask

class RegionExtractorStep(CPUParallelStep):
    """Extracts the given region from a compound mask"""

    def __init__(self):
        super(RegionExtractorStep, self).__init__()
        self.__region = 1
        self.__mask = np.zeros((0, 0, 0))         # pylint: disable=E1101
        self.__extracted = np.zeros((0, 0, 0, 0)) # pylint: disable=E1101

    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects two arguments: '+
                  ' mask file; region number.',
                  file=sys.stderr)
            exit(1)
        return validate_mask(1)

    def load_data(self):
        self.__mask = nib.load(str(sys.argv[1]))
        self.__region = int(sys.argv[2])
        self.shape = (self.__mask.shape[0],
                      self.__mask.shape[1],
                      self.__mask.shape[2])
        self.__extracted = np.zeros(self.shape, dtype=np.uint32)

    def process_partition(self, x_range, y_range, z_range):
        mask_data = self.__mask.get_data()

        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    if mask_data[(x, y, z)] == self.__region:
                        self.queue.put((x, y, z))

    def consume_product(self, product):
        self.__extracted[product] = 1

    def save(self):
        file_prefix = sys.argv[1].split('/')[-1].split('.')[0]

        extracted_mask_img = nib.Nifti1Image(self.__extracted,
                                             self.__mask.get_affine())

        extracted_mask_img.to_filename("%s_region_%d.nii.gz" % (file_prefix,
                                                                self.__region))