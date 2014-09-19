import numpy as np

class Tensor(object):
    """Tensor (3x3 symetric matrix)"""
    def __init__(self, compact_tensor):
        super(Tensor, self).__init__()
        self.matrix = np.matrix([[compact_tensor[0], compact_tensor[1], compact_tensor[2]],
                                 [compact_tensor[1], compact_tensor[3], compact_tensor[4]],
                                 [compact_tensor[2], compact_tensor[4], compact_tensor[5]]])