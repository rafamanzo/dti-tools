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

"""Container for RegionGrowStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

import sys                    # Makes possible to get the arguments
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy
import math as m

from src.classes.base.step import Step               # Base class
from src.classes.aux.input_validators import validate_tensor_and_mask
from queue import Queue

class RegionGrowStep(Step):
    """Applying the DBSCAN algorithm it elimates noise from a mask
       and clusters it"""

    def __init__(self):
        self.mask_data = []
        self.map_data = []
        self.shape = (0)
        self.sorted_regions = []
        self.affine = np.eye(4)
        self.means = []
        self.adjacency_matrix = []
        self.map_threshold = 0.0
        self.noise_threshold = 0

    def validate_args(self):
        if len(sys.argv) != 5:
            print('This program expects four arguments: map file; mask file; map_threshold value; and noise_threshold value',
                  file=sys.stderr)
            exit(1)
        validate_tensor_and_mask(1, 2)
        return True

    def load_data(self):
        mask = nib.load(str(sys.argv[2]))
        self.mask_data = mask.get_data()
        self.map_data = nib.load(str(sys.argv[1])).get_data()
        self.affine = mask.get_affine()
        self.shape = (mask.shape[0], mask.shape[1], mask.shape[2])
        self.sorted_regions = self.__sort_regions()
        self.means = {region: self.__region_mean(region) for region in self.sorted_regions.keys()}
        self.__generate_adjacency_matrix()
        self.map_threshold = float(sys.argv[3])
        self.noise_threshold = int(sys.argv[4])

    def process(self):
        mergeable = True

        while(mergeable):
            mergeable = False
            for region_a in range(1, self.mask_data.max() + 1):
                for region_b in range(1, self.mask_data.max() + 1):
                    if self.__homogeneous(region_a, region_b):
                        self.__merge(region_a, region_b)
                        mergeable = True
                        break

        for region_a in range(1, self.mask_data.max() + 1):
            if len(self.sorted_regions[region_a]) > 0 and len(self.sorted_regions[region_a]) <= self.noise_threshold:
                print("\nNoise found")
                region_b = None
                region_b_mean_difference = None

                for region in range(1, self.mask_data.max() + 1):
                    if self.adjacency_matrix[region_a][region]:
                        if region_b == None or region_b_mean_difference > m.fabs(self.means[region_a] - self.means[region]):
                            region_b = region
                            region_b_mean_difference = m.fabs(self.means[region_a] - self.means[region])

                if region_b != None:
                    print("Merging noise")
                    self.__merge(region_b, region_a)


    def save(self):
        region_grown = np.zeros(self.shape, dtype=np.uint32)

        for region, voxels in self.sorted_regions.items():
            for voxel in voxels:
                region_grown[voxel] = region

        file_prefix = sys.argv[2].split('/')[-1].split('.')[0]
        region_grown_img = nib.Nifti1Image(
                                region_grown,     # pylint: disable=E1101
                                self.affine) # pylint: disable=E1101
        region_grown_img.to_filename("%s_grown.nii.gz"%file_prefix)

    def __homogeneous(self, region_a, region_b):
        if self.adjacency_matrix[region_a][region_b] and (m.fabs(self.means[region_a] - self.means[region_b]) <= self.map_threshold):
            return True
        else:
            return False

    def __merge(self, region_a, region_b):
        print("Merging %d into %d\n"%(region_b, region_a))
        region_a_size = len(self.sorted_regions[region_a])
        region_b_size = len(self.sorted_regions[region_b])

        self.sorted_regions[region_a] = self.sorted_regions[region_a] + self.sorted_regions[region_b]
        self.sorted_regions[region_b] = []

        for region in range(1, self.mask_data.max() + 1):
            if self.adjacency_matrix[region_b][region] and not self.adjacency_matrix[region_a][region] and region != region_a:
                self.adjacency_matrix[region_a][region] = True
                self.adjacency_matrix[region][region_a] = True
            self.adjacency_matrix[region_b][region] = False
            self.adjacency_matrix[region][region_b] = False

        self.means[region_a] = (self.means[region_a]*region_a_size + self.means[region_b]*region_b_size)/(region_a_size + region_b_size)
        self.means[region_b] = None

    def __generate_adjacency_matrix(self):
        self.adjacency_matrix = [[False for j in range(self.mask_data.max() + 1)] for i in range(self.mask_data.max() + 1)]

        for region, voxels in self.sorted_regions.items():
            for voxel in voxels:
                value = region
                if value > 0:
                    for neighbour in self.__neighbourhood(voxel):
                        neighbour_value = self.mask_data[neighbour]
                        if neighbour_value > 0 and neighbour_value != value:
                            self.adjacency_matrix[value][neighbour_value] = True
                            self.adjacency_matrix[neighbour_value][value] = True

    def __sort_regions(self):
        h_min = self.mask_data.min()
        h_max = self.mask_data.max()

        sorted_regions = {i: [] for i in range(h_min, h_max + 1)}
        for x in range(0, self.shape[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.shape[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.shape[2]): # pylint: disable=C0103,C0301
                    value = self.mask_data[(x, y, z)]
                    if value > 0:
                        sorted_regions[value].append((x,y,z))

        return sorted_regions

    def __region_mean(self, region):
        total = 0.0
        count = 0

        for voxel in self.sorted_regions[region]:
            total = total + self.map_data[voxel]
            count = count + 1

        if count > 0:
            return total/count
        else:
            return None

    def __neighbourhood(self, voxel):
        neighbourhood = []

        for x in range(max(0,voxel[0] - 1), min(self.shape[0], voxel[0] + 2)):
            for y in range(max(0,voxel[1] - 1), min(self.shape[1], voxel[1] + 2)):
                for z in range(max(0,voxel[2] - 1), min(self.shape[2], voxel[2] + 2)):
                    neighbourhood.append((x, y, z))

        return neighbourhood
