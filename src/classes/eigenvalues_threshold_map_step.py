# This file is part of Improving Tractogrophy
# Copyright (C) 2013-2014 it's respectives authors (please see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Container for EigenvaluesThresholdMapStep class"""

import sys                    # Makes possible to get the arguments
import math as m   # Basic calculations

from src.classes.base.threshold_map_step import ThresholdMapStep
from src.classes.aux.input_validators import validate_tensor_and_mask

class EigenvaluesThresholdMapStep(ThresholdMapStep):
    """Maps voxels with fractional anisotropy higher then a given threshold"""

    def __init__(self):
        super(EigenvaluesThresholdMapStep, self).__init__("eigenvalues_%s_%s_%s_%s" % (sys.argv[3].replace(".", ""), sys.argv[4].replace(".", ""), sys.argv[5].replace(".", ""), sys.argv[6].replace(".", "")) )

    def validate_args(self):
        if len(sys.argv) != 7:
            print('This program expects five arguments: normalized eigenvalues file;'+
                  ' mask file; e1 - e2 threshold; e1 - e3 threshold; and e2 - e3 threshold; and epsilon.',
                  file=sys.stderr)
            exit(1)
        return validate_tensor_and_mask(1, 2)

    def load_data(self):
        super().load_data()
        self.e1_threshold = float(sys.argv[3])
        self.e2_threshold = float(sys.argv[4])
        self.e3_threshold = float(sys.argv[5])
        self.epsilon = float(sys.argv[6])

    # tensor is actually the eigenvalues array
    def check_for_threshold(self, tensor):
        return (((m.fabs(tensor[0] - tensor[1]) <= (self.e1_threshold + self.epsilon)) and m.fabs(tensor[0] - tensor[1]) >= (self.e1_threshold - self.epsilon)) and
                ((m.fabs(tensor[0] - tensor[2]) <= (self.e2_threshold + self.epsilon)) and m.fabs(tensor[0] - tensor[2]) >= (self.e2_threshold - self.epsilon)) and
                ((m.fabs(tensor[1] - tensor[2]) <= (self.e3_threshold + self.epsilon)) and m.fabs(tensor[1] - tensor[2]) >= (self.e3_threshold - self.epsilon))
               )
