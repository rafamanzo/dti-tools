import numpy as np
import math as m

class AcquisitionDirection(object):
    """Diffusion Tensor Imaging AcquisitionDirection"""
    def __init__(self, x, y, z):
        super(AcquisitionDirection, self).__init__()
        self.__x = x
        self.__y = y
        self.__z = z

    def cartesian(self):
        return np.matrix([[self.__x], [self.__y], [self.__z]])

    def spherical(self):
        XsqPlusYsq = self.__x**2 + self.__y**2

        r = m.sqrt(XsqPlusYsq + self.__z**2)
        theta = m.atan2(self.__z,m.sqrt(XsqPlusYsq))
        phi = m.atan2(y,self.__x)

        return r, theta, phi