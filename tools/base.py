from shared.tensor_data import TensorData
from shared.mask import Mask

class Base(object):
  """Wrapper for tool parameters"""
  def __init__(self, tensor_path, mask_path, output_path):
    super(Base, self).__init__()
    self.tensor_path = tensor_path
    self.mask_path = mask_path
    self.output_path = output_path
    self.tensor_data = TensorData(tensor_path)
    self.mask = Mask(mask_path)
    self.output_path = output_path
