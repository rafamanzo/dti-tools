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

"""Container for DBSCAN class"""

import numpy as np
from sets import Set

class DBSCAN(object):
    """Implementation of the DBSCAN clustering algorithm"""
    def __init__(self, eps, min_pts, mask, shape):
        self.__eps = eps
        self.__min_pts = min_pts
        self.__mask = mask
        self.__shape = shape
        self.__result = np.zeros(self.shape,    # pylint: disable-msg=E1101
                                 dtype=np.int16)# pylint: disable-msg=E1101

    def __neighbourhood(self, point):
        neighbourhood = {point}

        for x in range(max((point[0] - self.eps,0)),
                       min(self.__shape[0], point[0] + self.__eps + 1)):
            for y in range(max((point[1] - self.eps,0)),
                           min(self.__shape[1], point[1] + self.__eps + 1)):
                for z in range(max((point[2] - self.eps,0)),
                               min(self.__shape[2], point[2] + self.__eps + 1)):
                        if self.__mask[x][y][z]:
                            neighbourhood.add((x, y, z))

        return neighbourhood

    def __expand_cluster(self, point, neighbourhood, cluster):
        for neighbour in neighbourhood:
            if self.__result[neighbour[0]][neighbour[1]][neighbour[2]] == 0:
                self.__result[neighbour[0]][neighbour[1]][neighbour[2]] = 1
                cluster.add(neighbour)
                neighbour_neighbourhood = self.__neighbourhood(neighbour)
                if len(neighbour_neighbourhood) >= self.__min_pts:
                    neighbourhood.update(neighbour_neighbourhood)
                    self.__expand_cluster(point, neighbourhood, cluster)
                    break

    def fit():
        clusters = set()
        for x in range(x_range[0], x_range[1]):         # pylint: disable-msg=C0103,C0301
            for y in range(y_range[0], y_range[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(z_range[0], z_range[1]): # pylint: disable-msg=C0103,C0301
                    if self.__result[x][y][z] == 0:
                        neighbourhood = self.__neighbourhood((x, y, z))
                        if len(neighbourhood) < self.__min_pts
                            self.__result[x][y][z] = -1
                        else:
                            cluster = set()
                            self.__expand_cluster((x, y, z),
                                                  neighbourhood,
                                                  cluster)
                            clusters.add(cluster)

        return clusters, self.__result
