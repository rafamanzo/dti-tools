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

"""Container for DBSCANBase class"""

import numpy as np

class DBSCANBase(object):
    """Encapsulates DBSCAN related information and procedures"""

    def __init__(self, eps, min_pts, mask, shape, neighbourhood_criteria):
        self.__eps = eps
        self.__min_pts = min_pts
        self.__mask = mask
        self.__shape = shape
        self.__result = np.zeros(self.__shape,  # pylint: disable-msg=E1101
                                 dtype=np.int8) # pylint: disable-msg=E1101
        self.__neighbourhood_criteria = neighbourhood_criteria

    def set_result(self, point, result):
        """Sets a given result"""
        self.__result[point] = result

    def get_result(self, point):
        """Returns the result at the given point"""
        return self.__result[point]

    def get_results(self):
        """Returns the whole results matrix"""
        return self.__result

    def get_neighbourhood(self, point):
        """Receive a point and returns a set with it's neighbourhood"""
        neighbourhood = {point}

        for x in range(max((point[0] - self.__eps, 0)),                       # pylint: disable-msg=C0103,C0301
                       min(self.__shape[0], point[0] + self.__eps + 1)):
            for y in range(max((point[1] - self.__eps, 0)),                   # pylint: disable-msg=C0103,C0301
                           min(self.__shape[1], point[1] + self.__eps + 1)):
                for z in range(max((point[2] - self.__eps, 0)),               # pylint: disable-msg=C0103,C0301
                               min(self.__shape[2], point[2] + self.__eps + 1)):
                    if (self.__mask[x][y][z] and
                            self.__neighbourhood_criteria(point, (x, y, z))):
                        neighbourhood.add((x, y, z))

        return neighbourhood

    def get_min_pts(self):
        """Returns the minimum points value"""
        return self.__min_pts

    def get_shape(self):
        """Returns the shape"""
        return self.__shape

    def get_mask_val(self, point):
        """Returns the mask value at a given point"""
        return self.__mask[point]
