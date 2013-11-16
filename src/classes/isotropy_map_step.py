import sys                    # Makes possible to get the arguments
import os                     # File existence checking
import nibabel as nib         # Lib for reading and writing Nifit1
import numpy as np            # Nibabel is based on Numpy

from src.classes.base.cpu_parallel_step import CPUParallelStep

class IsotropyMapStep(CPUParallelStep):
  def validate_args(self):
    if len(sys.argv) != 4:
      print('This program expects three arguments: tensor file; mask file; and mean diffusivity threshold.', file=sys.stderr)
      exit(1)
    elif not os.path.isfile(str(sys.argv[1])):
      print('The given tensor file does not exists:\n%s'%str(sys.argv[1]), file=sys.stderr)
      exit(1)
    elif not os.path.isfile(str(sys.argv[2])):
      print('The given mask file does not exists:\n%s'%str(sys.argv[2]), file=sys.stderr)
      exit(1)
    return True

  def load_data(self):
    self.tensor_data = nib.load(str(sys.argv[1])).get_data()
    mask = nib.load(str(sys.argv[2]))
    self.threshold = float(sys.argv[3])
    self.shape = mask.shape
    self.mask_data = mask.get_data()
    self.isotropy_mask = np.zeros(self.shape, dtype=np.int16)

  def __mean_diffusivity(self,tensor):
    return (tensor[0] + tensor[3] + tensor[5])/3 # The sum of the three eigenvalues is equal to the trace of the tensor

  def process_partition(self, x_range, y_range, z_range):
    for x in range(x_range[0],x_range[1]):
      for y in range(y_range[0],y_range[1]):
        for z in range(z_range[0],z_range[1]):
          if self.mask_data[x][y][z]:
            if self.__mean_diffusivity(self.tensor_data[x][y][z]) <= self.threshold:
              self.isotropy_mask[x][y][z] = 1

  def save(self):
    isotropy_img = nib.Nifti1Image(self.isotropy_mask, np.eye(4))
    isotropy_img.to_filename('isotropy_mask.nii.gz')