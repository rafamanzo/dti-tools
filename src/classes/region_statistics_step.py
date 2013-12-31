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

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.tensor_statistics import TensorStatistics
from src.classes.aux.input_validators import validate_tensor_and_mask

class RegionStatisticsStep(CPUParallelStep):
    """Calculates mean and standard deviation for many tensor metrics
            grouped by it's regions

    """

    def __init__(self):
        super(RegionStatisticsStep, self).__init__()
        self.regions = {}
        self.md_results = {}
        self.fa_results = {}
        self.rd_results = {}
        self.tv_results = {}
        self.tc_results = {}
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

    def __get_point_results(self, point):
        """Calculates statistics for the given point"""

        region = self.mask.get_data()[point]

        tensor_statistics = TensorStatistics(self.tensor.get_data()[point])

        return {(region, point): (tensor_statistics.mean_diffusivity(),
                                  tensor_statistics.fractional_anisotropy(),
                                  tensor_statistics.radial_diffusivity(),
                                  tensor_statistics.toroidal_volume(),
                                  tensor_statistics.toroidal_curvature())}

    def process_partition(self, x_range, y_range, z_range):
        for x in range(x_range[0], x_range[1]):         # pylint: disable-msg=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable-msg=C0103,C0301
                    if self.mask.get_data()[(x, y, z)] > 0:
                        self.queue.put(self.__get_point_results((x, y, z)))

    def consume_product(self, product):
        key = list(product)[0]
        region = key[0]
        point = key[1]
        results = product[key]

        if not region in self.regions:
            self.regions[region] = []
            self.md_results[region] = []
            self.fa_results[region] = []
            self.rd_results[region] = []
            self.tv_results[region] = []
            self.tc_results[region] = []

        self.regions[region].append(point)
        self.md_results[region].append(results[0])
        self.fa_results[region].append(results[1])
        self.rd_results[region].append(results[2])
        self.tv_results[region].append(results[3])
        self.tc_results[region].append(results[4])

    def save(self):
        out = open('%s_statistics.txt' %
                   (sys.argv[2].split('/')[-1].split('.')[0]), 'w')

        out.write('Region \t | # Voxels \t | MD mean   \t |'+
                  ' MD std   \t | FA mean  \t | FA std   \t |'+
                  ' RD mean  \t | RD std   \t | TV mean  \t | TV std   \t |'+
                  ' TC mean  \t | TC std   \t \n')

        for region in self.regions.keys():
            values = (region,
                      len(self.regions[region]),
                      np.mean(self.md_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.md_results[region]),  # pylint: disable-msg=E1101,C0301
                      np.mean(self.fa_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.fa_results[region]),  # pylint: disable-msg=E1101,C0301
                      np.mean(self.rd_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.rd_results[region]),  # pylint: disable-msg=E1101,C0301
                      np.mean(self.tv_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.tv_results[region]),  # pylint: disable-msg=E1101,C0301
                      np.mean(self.tc_results[region]), # pylint: disable-msg=E1101,C0301
                      np.std(self.tc_results[region]))  # pylint: disable-msg=E1101,C0301

            out.write(("%5d \t | %8d \t | %2.7f \t |"+
                      " %2.6f \t | %2.7f \t | %2.7f \t |"+
                      " %2.7f \t | %2.7f \t | %2.7f \t | %2.7f \t |"+
                      " %2.7f \t | %2.7f \t \n")%values)
