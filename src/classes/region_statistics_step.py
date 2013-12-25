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

"""Container for RegionStatisticsStep class"""

import sys                    # Makes possible to get the arguments
import os                     # File existence checking
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy
from threading import Lock    # Mutual exclusion

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.tensor_statistics import TensorStatistics

class RegionStatisticsStep(CPUParallelStep):
    """Calculates mean and standard deviation for many tensor metrics
            grouped by it's regions

    """

    def __init__(self):
        super(RegionStatisticsStep, self).__init__()
        self.regions = {}
        self.__mutex = Lock()
        self.md_results = {}
        self.fa_results = {}
        self.mask = [[[]]]
        self.tensor = [[[[]]]]
        self.__affine = np.eye(4)
        self.shape = (0,0,0)


    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects three arguments: tensor file;'+
                  ' mask file.',
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
        tensor = nib.load(str(sys.argv[1]))
        self.tensor = tensor.get_data()
        self.__affine = tensor.get_affine()
        mask = nib.load(str(sys.argv[2]))
        self.shape = (mask.shape[0], mask.shape[1], mask.shape[2])
        self.mask = mask.get_data()

    def __add_point_to_region(self, point):
        region = self.mask[point]

        if not region in self.regions:
            self.regions[region] = []
            self.md_results[region] = []
            self.fa_results[region] = []

        tensor_statistics = TensorStatistics(self.tensor[point])

        self.__mutex.acquire()

        self.regions[region].append(point)
        self.md_results[region].append(tensor_statistics.mean_diffusivity())
        self.fa_results[region].append(tensor_statistics.fractional_anisotropy())
        
        self.__mutex.release()

    def process_partition(self, x_range, y_range, z_range):
        for x in range(x_range[0], x_range[1]):         # pylint: disable-msg=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable-msg=C0103,C0301
                    if self.mask[(x, y, z)] > 0:
                        self.__add_point_to_region((x, y, z))

    def save(self):
        out = open('region_statistics.txt', 'w')

        out.write('Region \t | # Voxels \t | MD mean \t | MD std \t | FA mean \t | FA std \t \n')

        for region in self.regions.keys():
            values = (region,
                      len(self.regions[region]),
                      np.mean(self.md_results[region]),
                      np.std(self.md_results[region]),
                      np.mean(self.fa_results[region]),
                      np.std(self.fa_results[region]))

            out.write("%d \t | %d \t | %.3f \t | %.3f \t | %.3f \t | %.3f \n"%values)
