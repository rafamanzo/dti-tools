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

"""Container for FilterMaskNoiseStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

import sys                    # Makes possible to get the arguments
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy

from src.classes.base.step import Step               # Base class
from src.classes.aux.clustering.mask_dbscan import MaskDBSCAN
                                                     # Algorithm used for
                                                     #   clustering and noise
                                                     #   reduction
from src.classes.aux.input_validators import validate_mask

class FilterMaskNoiseStep(Step):
    """Applying the DBSCAN algorithm it elimates noise from a mask
       and clusters it"""

    def __init__(self):
        self.min_pts = 0
        self.eps = 0
        self.mask_data = []
        self.shape = (0)
        self.filtered_mask = []

    def validate_args(self):
        if len(sys.argv) != 4:
            print('This program expects three arguments: mask file;'+
                  ' DBSCAN eps; and DBSCAN min_pts.',
                  file=sys.stderr)
            exit(1)
        validate_mask(1)
        return True

    def load_data(self):
        mask = nib.load(str(sys.argv[1]))
        self.mask_data = nib.load(str(sys.argv[1])).get_data()
        self.shape = (mask.shape[0], mask.shape[1], mask.shape[2])
        self.eps = int(sys.argv[2])
        self.min_pts = int(sys.argv[3])
        self.filtered_mask = np.zeros(self.shape,    # pylint: disable-msg=E1101
                                      dtype=np.uint8)# pylint: disable-msg=E1101

    def process(self):
        dbs = MaskDBSCAN(self.eps, self.min_pts, self.mask_data, self.shape)
        _, dbs_result = dbs.fit()
        self.__convert_dbs_result_to_mask(dbs_result)

    def save(self):
        filtered_mask_img = nib.Nifti1Image(
                                self.filtered_mask, # pylint: disable-msg=E1101
                                np.eye(4))          # pylint: disable-msg=E1101
        filtered_mask_img.to_filename('filtered_'+sys.argv[1].split('/')[-1])

    def __convert_dbs_result_to_mask(self, dbs_result):
        """Gets the result from DBSCAN and converts it into a mask"""

        for x in range(0, self.shape[0]):          # pylint: disable-msg=C0103,C0301
            for y in range(0, self.shape[1]):      # pylint: disable-msg=C0103,C0301
                for z in range(0, self.shape[2]):  # pylint: disable-msg=C0103,C0301
                    if dbs_result[x][y][z] == 1:
                        self.filtered_mask[x][y][z] = 1
                    else:
                        self.filtered_mask[x][y][z] = 0
