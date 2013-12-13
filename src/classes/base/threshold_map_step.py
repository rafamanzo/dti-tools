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

"""Container for ThresholdMapStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

import sys                    # Makes possible to get the arguments
import os                     # File existence checking
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy

from src.classes.base.cpu_parallel_step import CPUParallelStep

class ThresholdMapStep(CPUParallelStep):
    """Maps voxels with according to a given threshold"""

    def __init__(self, file_prefix):
        super(ThresholdMapStep, self).__init__()
        self.file_prefix = file_prefix
        self.threshold = 0.0
        self.tensor_data = [[[[]]]]
        self.mask_data = [[[[]]]]
        self.threshold_mask = [[[]]]

    def validate_args(self):
        if len(sys.argv) != 4:
            print('This program expects three arguments: tensor file;'+
                  ' mask file; and threshold.',
                  file=sys.stderr)
            exit(1)
        elif not os.path.isfile(str(sys.argv[1])):
            print('The given tensor file does not exists:\n%s'%
                  str(sys.argv[1]), file=sys.stderr)
            exit(1)
        elif not os.path.isfile(str(sys.argv[2])):
            print('The given mask file does not exists:\n%s'%
                  str(sys.argv[2]), file=sys.stderr)
            exit(1)
        return True

    def load_data(self):
        self.tensor_data = nib.load(str(sys.argv[1])).get_data()
        mask = nib.load(str(sys.argv[2]))
        self.threshold = float(sys.argv[3])
        self.shape = (mask.shape[0], mask.shape[1], mask.shape[2])
        self.mask_data = mask.get_data()
        self.threshold_mask = np.zeros(self.shape,  # pylint: disable-msg=E1101
                                    dtype=np.uint8) # pylint: disable-msg=E1101

    def check_for_threshold(self, tensor):
        """checks for wheter a givens tensor should be filtered"""
        raise NotImplementedError("Please implement this method")

    def process_partition(self, x_range, y_range, z_range):
        for x in range(x_range[0], x_range[1]):         # pylint: disable-msg=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable-msg=C0103,C0301
                    if self.mask_data[x][y][z]:
                        if (self.check_for_threshold(self.tensor_data[x][y][z])):  # pylint: disable-msg=C0301
                            self.threshold_mask[x][y][z] = 1

    def save(self):
        isotropy_img = nib.Nifti1Image(
                            self.threshold_mask, # pylint: disable-msg=E1101
                            np.eye(4))    # pylint: disable-msg=E1101
        isotropy_img.to_filename('%s_mask.nii.gz'%self.file_prefix)
