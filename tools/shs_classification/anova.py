from tools.shs_classification.adc import adc
from scipy.stats import f as f_dist

class Anova(object):
    """Analysis of Variance"""
    def __init__(self, model_a, model_b, acquisition_directions, tensor):
        super(Anova, self).__init__()
        self.__model_a = model_a
        self.__model_b = model_b
        self.__acquisition_directions = acquisition_directions
        self.__tensor = tensor

    def equivalent(self, significance_level):
        f = (
             ((len(self.__acquisition_directions) - self.__free_parameters(self.__model_b))*(self.__variance(self.__model_b) - self.__variance(self.__model_a)))/
             ((self.__free_parameters(self.__model_b) - self.__free_parameters(self.__model_a))*self.__mean_squared_error(self.__model_b))
            )

        # Freedom degrees
        d1 = len(self.__acquisition_directions) - self.__free_parameters(self.__model_b) - 1
        d2 = self.__free_parameters(self.__model_b) - self.__free_parameters(self.__model_a)

        distribution = f_dist(d1, d2)

        return f <= distribution.ppf(1.0 - significance_level)

    def __mean(self, model):
        accum = complex(0,0)

        for acquisition_direction in self.__acquisition_directions:
            accum += model.value(acquisition_direction)

        return accum/len(self.__acquisition_directions)

    def __variance(self, model):
        accum = complex(0,0)
        mean = self.__mean(model)

        for acquisition_direction in self.__acquisition_directions:
            accum += (model.value(acquisition_direction) - mean)**2

        return accum/len(self.__acquisition_directions)

    def __mean_squared_error(self, model):
        accum = complex(0,0)

        for acquisition_direction in self.__acquisition_directions:
            accum += (model.value(acquisition_direction) - adc(self.__tensor, acquisition_direction))**2

        return accum/len(self.__acquisition_directions)

    def __free_parameters(self, model):
        accum = 0

        for n in range(model.order + 1):
            accum += (2*n + 1)

        return accum
