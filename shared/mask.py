# Lib for reading and writing Nifit1
import nibabel as nib

class Mask(object):
    """docstring for Mask"""
    def __init__(self, mask_path):
        super(Mask, self).__init__()
        self.__image = nib.load(mask_path)

    def shape(self):
        return (self.__image.shape[0], self.__image.shape[1], self.__image.shape[2])

    def affine(self):
        self.__image.get_affine()

    def get(self, index):
        return self.__image.get_data()[index]

    def out(self, index):
        return self.get(index) == 0

    def inside(self, index):
        return not self.out(index)