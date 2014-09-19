from tools.shs_classification.sph_harm import sph_harm

class Model(object):
    """Model"""
    def __init__(self, order, coefficients):
        super(Model, self).__init__()
        self.order = order
        self.__coefficients = coefficients

    def value(acquisition_direction):
        accum = complex(0, 0)

        for l in range(self.order + 1):
            if l%2 == 0:
                for m in range(-l, l + 1):
                    accum += self.__coefficients[self.__index(l,m), 0]*sph_harm(l, m, acquisition_direction)

        return accum

    def __index(self, l, m):
        return l**2 + l + m