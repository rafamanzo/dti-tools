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

"""Container for WatershedSegmentationStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

import sys                    # Makes possible to get the arguments
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy

from src.classes.base.step import Step               # Base class
from src.classes.aux.input_validators import validate_tensor_and_mask

class WatershedSegmentationStep(Step):
    """Applying the DBSCAN algorithm it elimates noise from a mask
       and clusters it"""

    def __init__(self):
        self.mask_data = []
        self.discretized_data = []
        self.shape = (0)
        self.watersheds = []
        self.affine = np.eye(4)

    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects two arguments: discretized file; and mask file',
                  file=sys.stderr)
            exit(1)
        validate_tensor_and_mask(1, 2)
        return True

    def load_data(self):
        tensor = nib.load(str(sys.argv[1]))
        mask = nib.load(str(sys.argv[2]))
        self.mask_data = mask.get_data()
        self.discretized_data = tensor.get_data()
        self.affine = mask.get_affine()
        self.shape = (mask.shape[0], mask.shape[1], mask.shape[2])
        self.watersheds = -1*np.ones(self.shape,    # pylint: disable=E1101
                                      dtype=np.int32)# pylint: disable=E1101

    def process(self):
        MASK = -2
        WSHED = 0

        current_label = 0
        img_d = np.zeros(self.shape,    # pylint: disable=E1101
                        dtype=np.int32) # pylint: disable=E1101

        sorted_pixels = __sort_pixels()

    def save(self):
        file_prefix = sys.argv[1].split('/')[-1].split('.')[0]
        watersheds_img = nib.Nifti1Image(
                                self.watersheds,     # pylint: disable=E1101
                                self.affine) # pylint: disable=E1101
        watersheds_img.to_filename("%s_watersheds.nii.gz"%file_prefix)

    def __sort_pixels(self):
        bin_count = self.discretized_data.max() + 1
        hist = np.zeros(bin_count, dtype=np.uint32)

        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    value = self.discretized_data[(x, y, z)]
                    hist[value] = hist[value] + 1

        cumu_hist = hist
        for i in range(1, bin_count):
            cumu_hist[i] = cumu_hist[i] + cumu_hist[i - 1]

        sorted_pixels = [None for i in range(self.shape[0]*self.shape[1]*self.shape[2])]
        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    value = self.discretized_data[(x, y, z)]
                    sorted_pixels[cumu_hist[value] - 1] = (x,y,z)
                    cumu_hist[value] = cumu_hist[value] - 1

        return sorted_pixels