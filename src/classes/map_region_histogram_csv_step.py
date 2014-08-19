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

"""Container for MapRegionHistogramCSVStep class"""

import sys                      # Makes possible to get the arguments
import nibabel as nib           # Lib for reading and writing Nifit1
import numpy as np              # Nibabel is based on Numpy
import math as m

from src.classes.base.cpu_parallel_step import CPUParallelStep
from src.classes.aux.input_validators import validate_tensor_and_mask
import matplotlib.pyplot as plt # Histogram ploting
from matplotlib.ticker import MaxNLocator

class MapRegionHistogramCSVStep(CPUParallelStep):
    """Extracts the given region from a compound mask"""

    def __init__(self):
        super(MapRegionHistogramCSVStep, self).__init__()
        self.__map = np.zeros((0, 0, 0)) # pylint: disable=E1101
        self.__mask = np.zeros((0, 0, 0)) # pylint: disable=E1101
        self.differences_map = np.zeros((0, 0, 0)) # pylint: disable=E1101

    def validate_args(self):
        if len(sys.argv) != 6:
            print('This program expects two arguments: '+
                  ' map file; mask file; bins count; x start; x end.',
                  file=sys.stderr)
            exit(1)
        return validate_tensor_and_mask(1, 2)

    def load_data(self):
        self.__map = nib.load(str(sys.argv[1]))
        self.__mask = nib.load(str(sys.argv[2]))
        self.__bins = int(sys.argv[3])
        self.__x_start = float(sys.argv[4])
        self.__x_end = float(sys.argv[5])
        self.shape = (self.__map.shape[0],
                      self.__map.shape[1],
                      self.__map.shape[2])
        self.values = []

    def process_partition(self, x_range, y_range, z_range):
        map_data = self.__map.get_data()
        mask_data = self.__mask.get_data()

        for x in range(x_range[0], x_range[1]):         # pylint: disable=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable=C0103,C0301
                    if mask_data[(x,y,z)] == 1:
                        self.queue.put(map_data[(x,y,z)])

    def consume_product(self, product):
        self.values.append(product)

    def save(self):
        map_name = sys.argv[1].split('/')[-1].split('.')[0]
        mask_name = sys.argv[2].split('/')[-1].split('.')[0]

        hist, labels = self.__histogram()

        out = open('%s_%s_hist.csv'%(map_name, mask_name), 'w')
        for value_index in range(0, len(hist)):
            out.write("%s,%d\n" % (labels[value_index], hist[value_index]))

    def __histogram(self):
        if self.__bins > 0:
            bin_count = self.__bins
        else:
            bin_count = len(data)

        if self.__x_start != self.__x_end:
            x_start = self.__x_start
            x_end = self.__x_end
        else:
            x_start = min(self.values)
            x_end = max(self.values)

        step_size = (x_end - x_start)/bin_count

        bins = [x_start]
        labels = []

        for step in range(1, bin_count + 1):
            bin = x_start + step*step_size
            bins.append(bin)
            labels.append(bin - step_size/2)

        hist, _ = np.histogram(self.values, bins=bins)

        return hist, labels