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

"""Container for TensorStatisticsDBSCAN class"""

from src.classes.aux.clustering.base.dbscan import DBSCAN

import math as m
import numpy as np

# pylint: disable=R0903,R0922

class TensorStatisticsDBSCAN(DBSCAN):
    """Implementation of the DBSCAN clustering algorithm
       considering the FA difference between points

    """

    def __init__(self, eps, min_pts, mask, shape, tensor, max_value_difference): # pylint: disable=R0913, C0301
        super(TensorStatisticsDBSCAN, self).__init__(eps, min_pts, mask, shape)
        self.tensor = tensor
        self.__max_value_difference = max_value_difference
        self.__memoized_value = np.ones(shape, dtype=np.float16)*(-1)  # pylint: disable=E1101,C0301

    def neighbourhood_criteria(self, centroid, point):
        centroid_value = self.__get_value(centroid)
        point_value = self.__get_value(point)

        if m.fabs(centroid_value - point_value) <= self.__max_value_difference:
            return True
        else:
            return False

    def calculate_value(self, point):
        """Calculates the statistic value for the given point"""
        raise NotImplementedError("Please implement this method")

    def __get_value(self, point):
        """Gets the FA value for the tensor of a given point"""

        if self.__memoized_value[point] < 0:
            self.__memoized_value[point] = self.calculate_value(point)

        return self.__memoized_value[point]
