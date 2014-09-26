from tools.shs_classification.adc import adc
from tools.shs_classification.model import Model
from tools.shs_classification.shs_coefficients import SHSCoefficients
from tools.shs_classification.anova import Anova

class Classifier(object):
    """Classify each voxel accordingly to its fit to the spherical harmonics model order"""
    def __init__(self, acquisition_directions):
        super(Classifier, self).__init__()
        self.__acquisition_directions = acquisition_directions
        self.__lmax = self.__lmax()
        self.__significance_levels = self.__prompt_significance_levels()
        self.__coefficients = self.__coefficients()

    def classify(self, tensor):
        adcs = self.__adcs(tensor)

        selected_model = Model(0, self.__coefficients[0].coefficients(adcs))

        if self.__lmax > 0:
            for order in range(2, self.__lmax + 1, 2):
                new_model = Model(order, self.__coefficients[order].coefficients(adcs))

                if Anova(selected_model, new_model, self.__acquisition_directions, tensor).equivalent(self.__significance_levels[new_model.order]):
                    selected_model = new_model
                else:
                    return selected_model.order

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

    def __coefficients(self):
        coefficients = []

        for l in range(0, self.__lmax + 1, 2):
            coefficients.append(SHSCoefficients(self.__acquisition_directions, l))
            coefficients.append(None)

        return coefficients

    def __prompt_significance_levels(self):
        significance_levels = [None, None]

        for order in range(2, self.__lmax + 1, 2):
            significance_levels.append(float(input("\nSignificance level for %d order models: " % order)))
            significance_levels.append(None)

        return significance_levels
