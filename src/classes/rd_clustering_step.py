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

"""Container for TVClusteringStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

from src.classes.aux.clustering.rd_dbscan import RDDBSCAN
                                                     # Algorithm used for
                                                     #   clustering and noise
                                                     #   reduction
from src.classes.tensor_statistics_clustering_step import TensorStatisticsClusteringStep # pylint: disable=C0301

class RDClusteringStep(TensorStatisticsClusteringStep):
    """Applying the DBSCAN algorithm it elimates clusters points
         according to RD values

    """

    def __init__(self):
        super(RDClusteringStep, self).__init__("rd")

    def get_clusterer(self):
        return RDDBSCAN(self.eps, self.min_pts, self.mask.get_data(),
                       self.shape(), self.tensor.get_data(),
                       self.maximum_fa_difference)
