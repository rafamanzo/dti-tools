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

import numpy as np # Linear algebra
import math as m   # Basic calculations

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

    def fractional_anisotropy(self):
        """Tensor's fractional anisotropy (FA)"""
        mean_diffusivity = self.mean_diffusivity()
        eigenvalue, _ = np.linalg.eig(self.__tensor_matrix()) # pylint: disable-msg=E1101,C0301

        numerator = m.sqrt(m.pow(eigenvalue[0] - mean_diffusivity, 2) +
                           m.pow(eigenvalue[1] - mean_diffusivity, 2) +
                           m.pow(eigenvalue[2] - mean_diffusivity, 2))
        denominator = m.sqrt(m.pow(eigenvalue[0], 2) +
                             m.pow(eigenvalue[1], 2) +
                             m.pow(eigenvalue[2], 2))
        if(denominator > 0):
            return m.sqrt(3/2)*(numerator/denominator)
        else:
            return 0.0

    def __tensor_matrix(self):
        """Returns the compact tensor array into it's full symetric matrix"""
        return np.array([ # pylint: disable-msg=E1101
                         [self.tensor[0], self.tensor[1], self.tensor[2]],
                         [self.tensor[1], self.tensor[3], self.tensor[4]],
                         [self.tensor[2], self.tensor[4], self.tensor[5]]
                        ])
