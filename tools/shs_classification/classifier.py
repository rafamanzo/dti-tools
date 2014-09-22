from tools.shs_classification.adc import adc
from tools.shs_classification.model import Model
from tools.shs_classification.shs_coefficients import SHSCoefficients
from tools.shs_classification.anova import Anova

class Classifier(object):
    """Classify each voxel accordingly to its fit to the spherical harmonics model order"""
    def __init__(self, significance_level, acquisition_directions):
        super(Classifier, self).__init__()
        self.__significance_level = significance_level
        self.__acquisition_directions = acquisition_directions

    def classify(self, tensor):
        lmax = self.__lmax()
        adcs = self.__adcs(tensor)

        selected_model = Model(0, SHSCoefficients(self.__acquisition_directions, 0).coefficients(adcs))

        if lmax > 0:
            for order in range(2, lmax + 1, 2):
                new_model = Model(order, SHSCoefficients(self.__acquisition_directions, order).coefficients(adcs))

                if Anova(selected_model, new_model, self.__acquisition_directions, tensor).equivalent(self.__significance_level):
                    selected_model = new_model

        return selected_model.order

    def __lmax(self):
        lmax = 0
        accum = 1

        while accum < len(self.__acquisition_directions):
            accum += 2*(lmax + 1) + 1
            accum += 2*(lmax + 2) + 1

            if accum < len(self.__acquisition_directions):
                lmax += 2


            return lmax

    def __adcs(self, tensor):
        adcs = []

        for acquisition_direction in self.__acquisition_directions:
            adcs.append(adc(tensor, acquisition_direction))

        return adcs
