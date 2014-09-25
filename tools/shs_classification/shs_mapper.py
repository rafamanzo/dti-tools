import numpy as np
import nibabel as nib

from multiprocessing import Process, Queue, cpu_count
from threading import Thread

from tools.base import Base
from tools.shs_classification.classifier import Classifier
from tools.shs_classification.acquisition_direction import AcquisitionDirection

class PoisonPill(object):
    """PoisonPill stops a running parallel process"""
    def __init__(self):
        super(PoisonPill, self).__init__()

class CoordinateClassification(object):
    """CoordinateClassification pair"""
    def __init__(self, coordinate, classification):
        super(CoordinateClassification, self).__init__()
        self.coordinate = coordinate
        self.classification = classification


class SHSMapper(Base):
    """Maps the whole dataset using the classifier"""
    def __init__(self, tensor_path, mask_path, acquisition_directions_path, output_path):
        super(SHSMapper, self).__init__(tensor_path, mask_path, output_path)
        self.__classifier = Classifier(self.__load_acquisition_directions(acquisition_directions_path))
        self.__classification = np.zeros(self.mask.shape(), dtype=np.uint8)

        self.__to_be_classified = Queue()
        self.__classified = Queue()
        self.__worker_count = cpu_count()


    def save(self):
        nib.Nifti1Image(self.__classification, self.mask.affine()).to_filename("%s" % self.output_path)

    def run(self):
        if self.__worker_count > 1:
            self.__parallel_run()
        else:
            self.__sequential_run()

    def __load_acquisition_directions(self, acquisition_directions_path):
        acquisition_directions_file = open(acquisition_directions_path, 'r')
        acquisition_directions = []

        for line in acquisition_directions_file.readlines():
            directions = line.split()
            if len(directions) == 3:
                acquisition_directions.append(AcquisitionDirection(float(directions[0]), float(directions[1]), float(directions[2])))

        return acquisition_directions

    def __parallel_run(self):
        classifiers = []

        producer = Thread(target=self.__produce)
        producer.start()

        for _ in range(self.__worker_count):
            classifiers.append(Process(target=self.__classify))
            classifiers[-1].start()

        consumer = Thread(target=self.__consume)
        consumer.start()

        producer.join()

        for classifier in classifiers:
            classifier.join()

        self.__classified.put(PoisonPill())

        consumer.join()

    def __sequential_run(self):
        for i in range(self.mask.shape()[0]):
            for j in range(self.mask.shape()[1]):
                for k in range(self.mask.shape()[2]):
                    if self.mask.inside((i,j,k)):
                        self.__classification[(i,j,k)] = self.__classifier.classify(self.tensor_data.get((i,j,k))) + 1

    def __produce(self):
        for i in range(self.mask.shape()[0]):
            for j in range(self.mask.shape()[1]):
                for k in range(self.mask.shape()[2]):
                    if self.mask.inside((i,j,k)):
                        self.__to_be_classified.put((i,j,k))

        for _ in range(self.__worker_count):
            self.__to_be_classified.put(PoisonPill())

        return True

    def __classify(self):
        coordinate = self.__to_be_classified.get()

        while not type(coordinate) is PoisonPill:
            self.__classified.put(CoordinateClassification(coordinate, self.__classifier.classify(self.tensor_data.get(coordinate)) + 1))
            coordinate = self.__to_be_classified.get()

        return True

    def __consume(self):
        coordinate_classification = self.__classified.get()

        while not type(coordinate_classification) is PoisonPill:
            self.__classification[coordinate_classification.coordinate] = coordinate_classification.classification
            coordinate_classification = self.__classified.get()

        return True