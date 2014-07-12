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
from queue import Queue

class WatershedSegmentationStep(Step):
    """Applying the DBSCAN algorithm it elimates noise from a mask
       and clusters it"""

    def __init__(self):
        self.mask_data = []
        self.discretized_data = []
        self.shape = (0)
        self.watersheds = []
        self.affine = np.eye(4)
        self.queue = Queue()

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
        FICTITIOUS_VOXEL = (-1,-1,-1)

        current_label = 0
        current_dist = 0
        img_d = np.zeros(self.shape,    # pylint: disable=E1101
                        dtype=np.int32) # pylint: disable=E1101

        sorted_pixels = self.__sort_pixels()

        h_min = self.discretized_data.min()
        h_max = self.discretized_data.max()

        for h in range(h_min, h_max + 1):
            for voxel in sorted_pixels[h]:
                self.watersheds[voxel] = MASK

                for neighbour in self.__neighbourhood(voxel):
                    if self.watersheds[neighbour] > 0 or self.watersheds[neighbour] == WSHED:
                        img_d[voxel] = 1
                        self.queue.put(voxel)
                        break

            current_dist = 1
            self.queue.put(FICTITIOUS_VOXEL)

            while True:
                voxel = self.queue.get(block=False)

                if voxel == FICTITIOUS_VOXEL:
                    if self.queue.empty():
                        break
                    else:
                        self.queue.put(FICTITIOUS_VOXEL)
                        current_dist = current_dist + 1
                        voxel = self.queue.get(block=False)

                for neighbour in self.__neighbourhood(voxel):
                    if img_d[neighbour] < current_dist and (self.watersheds[neighbour] > 0 or self.watersheds[neighbour] == WSHED):
                        if self.watersheds[neighbour] > 0:
                            if self.watersheds[voxel] == MASK or self.watersheds[voxel] == WSHED:
                                self.watersheds[voxel] = self.watersheds[neighbour]
                            elif self.watersheds[voxel] != self.watersheds[neighbour]:
                                self.watersheds[voxel] = WSHED
                        elif self.watersheds[voxel] == MASK:
                            self.watersheds[voxel] = WSHED
                    elif self.watersheds[neighbour] == MASK and img_d[neighbour] == 0:
                        img_d[neighbour] = current_dist + 1
                        self.queue.put(neighbour)

            for voxel in sorted_pixels[h]:
                img_d[voxel] = 0

                if self.watersheds[voxel] == MASK:
                    current_label = current_label + 1
                    self.queue.put(voxel)
                    self.watersheds[voxel] = current_label

                while not self.queue.empty():
                    voxel_1 = self.queue.get(block= False)

                    for neighbour in self.__neighbourhood(voxel_1):
                        if self.watersheds[neighbour] == MASK:
                            self.queue.put(neighbour)
                            self.watersheds[neighbour] = current_label

    def save(self):
        file_prefix = sys.argv[1].split('/')[-1].split('.')[0]
        watersheds_img = nib.Nifti1Image(
                                self.watersheds,     # pylint: disable=E1101
                                self.affine) # pylint: disable=E1101
        watersheds_img.to_filename("%s_watersheds.nii.gz"%file_prefix)

    def __sort_pixels(self):
        h_min = self.discretized_data.min()
        h_max = self.discretized_data.max()

        sorted_pixels = {i: [] for i in range(h_min, h_max + 1)}
        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    if self.mask_data[(x, y, z)] > 0:
                        value = self.discretized_data[(x, y, z)]
                        sorted_pixels[value].append((x,y,z))

        return sorted_pixels

    def __neighbourhood(self, voxel):
        neighbourhood = []

        for x in range(max(0,voxel[0] - 1), min(self.shape[0], voxel[0] + 2)):
            for y in range(max(0,voxel[1] - 1), min(self.shape[1], voxel[1] + 2)):
                for z in range(max(0,voxel[2] - 1), min(self.shape[2], voxel[2] + 2)):
                    neighbourhood.append((x, y, z))

        return neighbourhood