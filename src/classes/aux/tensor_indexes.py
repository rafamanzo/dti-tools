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

"""Container for TensorIndexes class"""

import numpy as np # Linear algebra
import math as m   # Basic calculations

# pylint: disable=R0903,R0922

class TensorIndexes(object):
    """Calculates some tensor indexes"""

    def __init__(self, tensor):
        super(TensorIndexes, self).__init__()
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
        eigenvalue, _ = self.__eigensystem()

        numerator = m.sqrt(m.pow(eigenvalue[0] - mean_diffusivity, 2) +
                           m.pow(eigenvalue[1] - mean_diffusivity, 2) +
                           m.pow(eigenvalue[2] - mean_diffusivity, 2))
        denominator = m.sqrt(m.pow(eigenvalue[0], 2) +
                             m.pow(eigenvalue[1], 2) +
                             m.pow(eigenvalue[2], 2))
        if(denominator > 0):
            value = m.sqrt(3/2)*(numerator/denominator)
            if value > 1.0:
                return 0.0
            else:
                return value
        else:
            return 0.0

    def radial_diffusivity(self):
        """Tensor's radial diffusivity (RD)"""

        eigenvalues, _ = self.__eigensystem()

        return (eigenvalues[1] + eigenvalues[2]) / 2

    def toroidal_volume(self):
        """Tensor's toroidal volume (TV)"""

        eigenvalues, _ = self.__eigensystem()

        return ((m.pi / 3.0) *
                    eigenvalues[0] *
                    ((eigenvalues[1] * eigenvalues[2]) +
                        (m.pow(eigenvalues[2], 2) / 2.0)))

    def toroidal_curvature(self):
        """Tensor's toroidal curvature (TC)"""

        eigenvalues, _ = self.__eigensystem()

        phi = self.__argmax_tc()
        alpha_denominator = (4.0 * eigenvalues[0])
        if alpha_denominator != 0.0:
            alpha = (((2.0 * eigenvalues[1]) + eigenvalues[2]) /
                        alpha_denominator)
        else:
            alpha = 0.0
        beta = eigenvalues[2] * (4 * eigenvalues[0])
        gama = 1.0 / 2.0

        # Avoiding repeating calculations
        beta_2 = m.pow(beta, 2)
        gama_2 = m.pow(gama, 2)
        cos_phi = m.cos(phi)

        numerator = 4.0 * beta * gama_2 * cos_phi
        denominator = ((alpha + beta * cos_phi) *
                      m.pow((beta_2 + gama_2 +
                                ((gama_2 - beta_2) * m.cos(2.0  * phi))), 2))

        if denominator != 0.0:
            return numerator / denominator
        else:
            return 0.0

    def log_euclidean_distance(self, matrix):
        self_matrix = self.tensor_matrix()

        return np.power(np.trace(np.power(np.log10(self_matrix) - np.log10(matrix), 2)), 1/2)

    def tensor_matrix(self):
        """Returns the compact tensor array into it's full symetric matrix"""
        return np.array([ # pylint: disable=E1101
                         [self.tensor[0], self.tensor[1], self.tensor[2]],
                         [self.tensor[1], self.tensor[3], self.tensor[4]],
                         [self.tensor[2], self.tensor[4], self.tensor[5]]
                        ])

    def __argmax_tc(self): # Maybe the first and second derivates are faster
        """Searches for the angles that maximizes the tc value"""

        error = 0.0001 # Three decimal points precision

        start = 0.0
        end = m.pi

        while (end - start) > error:
            if self.__tc(start) >= self.__tc(end):
                end = (start + end) / 2.0
            else:
                start = (start + end) / 2.0

        return (start + end) / 2.0

    def __tc(self, alpha):
        """Torus maximum gaussian curvature at angle alpha"""

        params = self.__torus_params()

        denominator = (params[1]*(params[0] + params[1]*m.cos(alpha)))

        if denominator != 0.0:
            return m.cos(alpha) / denominator
        else:
            return 0.0

    def __torus_params(self):
        """Tensor's corresponding torus parameters"""

        eigenvalues, _ = self.__eigensystem()

        alpha = (2.0*eigenvalues[1] + eigenvalues[2])/4.0
        beta = eigenvalues[2]/4.0
        gama = eigenvalues[0]/2.0

        return (alpha, beta, gama)

    def __eigensystem(self):
        """Tensor's eigensystem ordered by eigenvalues"""
        eigenvalues, eigenevctors = np.linalg.eig(self.tensor_matrix()) # pylint: disable=E1101,C0301

        # descendat order
        ordered_indexes = list(reversed(eigenvalues.argsort()))

        return eigenvalues[ordered_indexes], eigenevctors[:, ordered_indexes]

