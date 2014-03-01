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

"""Container for ThresholdMapStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

import sys                    # Makes possible to get the arguments
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.input_validators import validate_tensor_and_mask

class ThresholdMapStep(CPUParallelStep):
    """Maps voxels with according to a given threshold"""

    def __init__(self, file_prefix):
        super(ThresholdMapStep, self).__init__()
        self.file_prefix = file_prefix
        self.threshold = 0.0
        self.tensor_data = [[[[]]]]
        self.mask_data = [[[[]]]]
        self.threshold_mask = [[[]]]
        self.affine = np.eye(4)      # pylint: disable=E1101

    def validate_args(self):
        if len(sys.argv) != 4:
            print('This program expects three arguments: tensor file;'+
                  ' mask file; and threshold.',
                  file=sys.stderr)
            exit(1)
        return validate_tensor_and_mask(1, 2)

    def load_data(self):
        tensor = nib.load(str(sys.argv[1]))
        self.tensor_data = tensor.get_data()
        self.affine = tensor.get_affine()
        mask = nib.load(str(sys.argv[2]))
        self.threshold = float(sys.argv[3])
        self.shape = (mask.shape[0], mask.shape[1], mask.shape[2])
        self.mask_data = mask.get_data()
        self.threshold_mask = np.zeros(self.shape,  # pylint: disable=E1101
                                    dtype=np.uint8) # pylint: disable=E1101

    def check_for_threshold(self, tensor):
        """checks for wheter a givens tensor should be filtered"""
        raise NotImplementedError("Please implement this method")

    def process_partition(self, x_range, y_range, z_range):
        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    if self.mask_data[x][y][z]:
                        if (self.check_for_threshold(self.tensor_data[x][y][z])):  # pylint: disable=C0301
                            self.queue.put((x, y, z))

    def consume_product(self, product):
        self.threshold_mask[product] = 1

    def save(self):
        isotropy_img = nib.Nifti1Image(
                            self.threshold_mask, # pylint: disable=E1101
                            self.affine)    # pylint: disable=E1101
        isotropy_img.to_filename('%s_mask.nii.gz'%self.file_prefix)
