import numpy as np

from tools.base import Base
from tools.shs_classification.classifier import Classifier
from tools.shs_classification.acquisition_direction import AcquisitionDirection

class SHSMapper(Base):
    """Maps the whole dataset using the classifier"""
    def __init__(self, tensor_path, mask_path, acquisition_directions_path, significance_level, output_path):
        super(SHSMapper, self).__init__(tensor_path, mask_path, output_path)
        self.__classifier = Classifier(float(significance_level), self.__load_acquisition_directions(acquisition_directions_path))
        self.__classification = np.zeros(self.mask.shape(), dtype=np.uint8)

    def classify(self):
        for i in range(self.mask.shape()[0]):
            for j in range(self.mask.shape()[1]):
                for k in range(self.mask.shape()[2]):
                    if self.mask.inside((i,j,k)):
                        self.__classification[(i,j,k)] = self.__classifier.classify(self.tensor_data.get((i,j,k))) + 1

    def save(self):
        nib.Nifti1Image(self.__classification, self.mask.affine()).to_filename("%s.nii.gz" % self.output_path)

    def __load_acquisition_directions(self, acquisition_directions_path):
        acquisition_directions_file = open(acquisition_directions_path, 'r')
        acquisition_directions = []

        for line in acquisition_directions_file.readlines():
            directions = line.split()
            if len(directions) == 3:
                acquisition_directions.append(AcquisitionDirection(float(directions[0]), float(directions[1]), float(directions[2])))

        return acquisition_directions

