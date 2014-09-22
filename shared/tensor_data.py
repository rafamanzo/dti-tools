# Lib for reading and writing Nifit1
import nibabel as nib

from shared.tensor import Tensor

class TensorData(object):
    """TensorData groups all the data access"""
    def __init__(self, tensor_path):
        super(TensorData, self).__init__()
        self.__data = nib.load(tensor_path).get_data()

    def get(self, index):
        return Tensor(self.__data[index][slice(0,6)])
