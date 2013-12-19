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

"""Container for FADBSCAN class"""

from src.classes.aux.clustering.dbscan import DBSCAN
from src.classes.aux.tensor_statistics import TensorStatistics

import math as m
import numpy as np

# pylint: disable-msg=R0903,R0922

class FADBSCAN(DBSCAN):
    """Implementation of the DBSCAN clustering algorithm
       considering the FA difference between points

    """

    def __init__(self, eps, min_pts, mask, shape, tensor, max_fa_difference):
        super(FADBSCAN, self).__init__(eps, min_pts, mask, shape)
        self.__tensor = tensor
        self.__max_fa_difference = max_fa_difference
        self.__memoized_fa = np.ones(shape, dtype=np.float16)*(-1)  # pylint: disable-msg=E1101,C0301

    def neighbourhood_criteria(self, centroid, point):
        centroid_fa = self.__get_fa(centroid)
        point_fa = self.__get_fa(point)

        if m.fabs(centroid_fa - point_fa) <= self.__max_fa_difference:
            return True
        else:
            return False

    def __get_fa(self, point):
        if self.__memoized_fa[point] < 0:
            self.__memoized_fa[point] = TensorStatistics(self.__tensor[point]).fractional_anisotropy() # pylint: disable-msg=C0301

        return self.__memoized_fa[point]