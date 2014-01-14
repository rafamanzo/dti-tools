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

import sys
sys.path.append(sys.path[0][:-9])

import unittest

from src.tests.classes.base.step_test import StepTestCase
from src.tests.classes.base.cpu_parallel_step_test import CPUParallelStepTestCase
from src.tests.classes.base.threshold_map_step_test import ThresholdMapStepTestCase
from src.tests.classes.aux.clustering.base.dbscan_test import DBSCANTestCase
from src.tests.classes.aux.clustering.mask_dbscan_test import MaskDBSCANTestCase
from src.tests.classes.aux.clustering.tensor_statistics_dbscan_test import TensorStatisticsDBSCANTestCase
from src.tests.classes.aux.clustering.fa_dbscan_test import FADBSCANTestCase
from src.tests.classes.aux.clustering.rd_dbscan_test import RDDBSCANTestCase
from src.tests.classes.aux.clustering.tv_dbscan_test import TVDBSCANTestCase
from src.tests.classes.aux.clustering.tc_dbscan_test import TCDBSCANTestCase
from src.tests.classes.aux.tensor_statistics_test import TensorStatisticsTestCase
from src.tests.classes.aux.input_validators_test import InputValidatorsTestCase
from src.tests.classes.md_threshold_map_step_test import MDThresholdMapStepTestCase
from src.tests.classes.fa_threshold_map_step_test import FAThresholdMapStepTestCase
from src.tests.classes.filter_mask_noise_step_test import FilterMaskNoiseStepTestCase
from src.tests.classes.tensor_statistics_clustering_step_test import TensorStatisticsClusteringStepTestCase
from src.tests.classes.fa_clustering_step_test import FAClusteringStepTestCase
from src.tests.classes.rd_clustering_step_test import RDClusteringStepTestCase
from src.tests.classes.tv_clustering_step_test import TVClusteringStepTestCase
from src.tests.classes.tc_clustering_step_test import TCClusteringStepTestCase
from src.tests.classes.region_statistics_step_test import RegionStatisticsStepTestCase

class UnitTestsSuite(unittest.TestSuite):
    def __init__(self):
        self.addTest(StepTestCase())
        self.addTest(CPUParallelStepTestCase())
        self.addTest(DBSCANTestCase())
        self.addTest(TensorStatisticsDBSCANTestCase())
        self.addTest(FADBSCANTestCase())
        self.addTest(RDDBSCANTestCase())
        self.addTest(TVDBSCANTestCase())
        self.addTest(TCDBSCANTestCase())
        self.addTest(TensorStatisticsTestCase())
        self.addTest(InputValidatorsTestCase())
        self.addTest(MaskDBSCANTestCase())
        self.addTest(MDThresholdMapStepTestCase())
        self.addTest(FAThresholdMapStepTestCase())
        self.addTest(FilterMaskNoiseStepTestCase())
        self.addTest(TensorStatisticsClusteringStepTestCase())
        self.addTest(FAClusteringStepTestCase())
        self.addTest(RDClusteringStepTestCase())
        self.addTest(TVClusteringStepTestCase())
        self.addTest(TCClusteringStepTestCase())
        self.addTest(RegionStatisticsStepTestCase())

if __name__ == '__main__':
    unittest.main()