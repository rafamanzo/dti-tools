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

"""Container for LEDBSCAN class"""

from src.classes.base.clustering.dbscan import DBSCAN # pylint: disable=C0301
from src.classes.aux.tensor_indexes import TensorIndexes

# pylint: disable=R0903,R0922

class LEDBSCAN(DBSCAN):
    """Implementation of the DBSCAN clustering algorithm
       considering the FA difference between points

    """

    def __init__(self, eps, min_pts, mask, shape, tensor, max_distance): # pylint: disable=R0913, C0301
        super(LEDBSCAN, self).__init__(eps, min_pts, mask, shape)
        self.tensor = tensor
        self.__max_distance = max_distance

    def neighbourhood_criteria(self, centroid, point):
        if TensorIndexes(self.tensor[centroid]).log_euclidean_distance(TensorIndexes(self.tensor[point]).tensor_matrix()) <= self.__max_distance:
            return True
        else:
            return False
