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

"""Container for MaskDBSCAN class"""

from src.classes.aux.clustering.dbscan import DBSCAN

# pylint: disable-msg=R0903,R0922

class MaskDBSCAN(DBSCAN):
    """Implementation of the DBSCAN clustering algorithm
       considering just the mask

    """

    def neighbourhood_criteria(self, centroid, point):
        return True
