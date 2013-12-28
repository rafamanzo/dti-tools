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
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy
from threading import Lock    # Mutual exclusion

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.tensor_statistics import TensorStatistics
from src.classes.aux.input_validators import validate_tensor_and_mask

class RegionStatisticsStep(CPUParallelStep):
    """Calculates mean and standard deviation for many tensor metrics
            grouped by it's regions

    """

    def __init__(self):
        super(RegionStatisticsStep, self).__init__()
        self.__mutex = Lock()
        self.regions = {}
        self.md_results = {}
        self.fa_results = {}
        self.mask = np.zeros((0, 0, 0))      # pylint: disable-msg=E1101
        self.tensor = np.zeros((0, 0, 0, 0)) # pylint: disable-msg=E1101
        self.shape = (0, 0, 0)

    def validate_args(self):
        if len(sys.argv) != 3:
            print('This program expects three arguments: tensor file;'+
                  ' mask file.',
                  file=sys.stderr)
            exit(1)
        return validate_tensor_and_mask(1, 2)


    def load_data(self):
        self.tensor = nib.load(str(sys.argv[1]))
        self.mask = nib.load(str(sys.argv[2]))
        self.shape = (self.mask.shape[0],
                      self.mask.shape[1],
                      self.mask.shape[2])

    def __add_point_to_region(self, point):
        """Adds a point to it's corresponding region and
                calculates it's statistics

        """

        region = self.mask.get_data()[point]

        if not region in self.regions:
            self.regions[region] = []
            self.md_results[region] = []
            self.fa_results[region] = []

        tensor_statistics = TensorStatistics(self.tensor.get_data()[point])

        self.__mutex.acquire()

        self.regions[region].append(point)
        self.md_results[region].append(tensor_statistics.mean_diffusivity())
        self.fa_results[region].append(
            tensor_statistics.fractional_anisotropy())

        self.__mutex.release()

    def process_partition(self, x_range, y_range, z_range):
        for x in range(x_range[0], x_range[1]):         # pylint: disable-msg=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable-msg=C0103,C0301
                    if self.mask.get_data()[(x, y, z)] > 0:
                        self.__add_point_to_region((x, y, z))

    def save(self):
        out = open('region_statistics.txt', 'w')

        out.write('Region \t | # Voxels \t | MD mean \t |'+
                  'MD std \t | FA mean \t | FA std \t \n')

        for region in self.regions.keys():
            values = (region,
                      len(self.regions[region]),
                      np.mean(self.md_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.md_results[region]),  # pylint: disable-msg=E1101,C0301
                      np.mean(self.fa_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.fa_results[region]))  # pylint: disable-msg=E1101,C0301

            out.write(("%5d \t | %8d \t | %6.3f \t |"+
                      " %5.3f \t | %6.3f \t | %5.3f \n")%values)
