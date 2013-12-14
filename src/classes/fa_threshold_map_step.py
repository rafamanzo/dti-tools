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

"""Container for FAThresholdMapStep class"""

from src.classes.base.threshold_map_step import ThresholdMapStep
from src.classes.aux.tensor_statistics import TensorStatistics

class FAThresholdMapStep(ThresholdMapStep):
    """Maps voxels with fractional anisotropy higher then a given threshold"""

    def __init__(self):
        super(FAThresholdMapStep, self).__init__("fa")

    def check_for_threshold(self, tensor):
        return (TensorStatistics(tensor).
                    fractional_anisotropy() >= self.threshold)
