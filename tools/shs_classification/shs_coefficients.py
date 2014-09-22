import numpy as np

from tools.shs_classification.sph_harm import sph_harm

class SHSCoefficients(object):
    """Spherical Harmonics Series Coefficients"""
    def __init__(self, acquisition_directions, order):
        super(SHSCoefficients, self).__init__()
        self.__m = self.__m(acquisition_directions, order)

    def coefficients(self, adcs):
        f = np.matrix(adcs).T

        return self.__m*f

    def __m(self, acquisition_directions, order):
        x = self.__x(acquisition_directions, order)
        x_conj_trans = x.conjugate().T

        return (x_conj_trans*x).I*x_conj_trans

    def __x(self, acquisition_directions, order):
        rows = []
        for acquisition_direction in acquisition_directions:
            row = []
            for l in range(order + 1):
                for m in range(-l, (l + 1)):
                    row.append(sph_harm(l,m,acquisition_direction))
            rows.append(row)

        return np.matrix(rows)