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

"""Container for FAClusteringStep class"""

# disable complaints about Module 'numpy' has no 'zeros' member

from src.classes.aux.clustering.fa_dbscan import FADBSCAN
                                                     # Algorithm used for
                                                     #   clustering and noise
                                                     #   reduction
from src.classes.tensor_statistics_clustering_step import TensorStatisticsClusteringStep # pylint: disable-msg=C0301

class FAClusteringStep(TensorStatisticsClusteringStep):
    """Applying the DBSCAN algorithm it elimates clusters points
         according to FA values

    """

    def __init__(self):
        super(FAClusteringStep, self).__init__("fa")

    def get_clusterer(self):
        return FADBSCAN(self.eps, self.min_pts, self.mask.get_data(),
                       self.shape(), self.tensor.get_data(),
                       self.maximum_fa_difference)
