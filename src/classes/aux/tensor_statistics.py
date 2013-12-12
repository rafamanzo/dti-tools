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

"""Container for TensorStatistics class"""

# pylint: disable-msg=R0903,R0922

class TensorStatistics(object):
    """Calculates some tensor statistics"""

    def __init__(self, tensor):
        super(TensorStatistics, self).__init__()
        self.tensor = tensor

    def mean_diffusivity(self):
        """Receives an six element array that represents the tensor matrix of
           a given voxel and returns it's mean diffusivity

        """
        # The sum of the three eigenvalues is equal to the trace of the tensor
        return (self.tensor[0] + self.tensor[3] + self.tensor[5])/3
