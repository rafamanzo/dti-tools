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

"""Container for DBSCAN class"""

from multiprocessing import cpu_count
from threading import Thread
import time

from src.classes.aux.clustering.base.dbscan_expansor_manager import DBSCANExpansorManager # pylint: disable=C0301
from src.classes.aux.clustering.base.dbscan_results_manager import DBSCANResultsManager # pylint: disable=C0301
from src.classes.aux.clustering.base.dbscan_base import DBSCANBase

# pylint: disable=R0903,R0922

class DBSCAN(object):
    """Implementation of the DBSCAN clustering algorithm"""

    def __init__(self, eps, min_pts, mask, shape):
        self.__base = DBSCANBase(eps, min_pts, mask, shape,
                                 self.neighbourhood_criteria)
        self.__results_manager = DBSCANResultsManager(cpu_count())
        self.__expansor_manager = DBSCANExpansorManager(cpu_count(),
                                        self.__results_manager, self.__base)

        self.__current_cluster = set()

    def __cluster_finished(self):
        """Checks wether all the workers are idle"""
        return (self.__expansor_manager.all_idling() and
                self.__expansor_manager.nothing_to_expand())

    def __add_points_to_cluster(self):
        """Consumes results"""
        while True:
            presence, point = self.__results_manager.get_result_to_be_inserted()

            if presence:
                if point == None:
                    self.__results_manager.signal_result_to_be_inserted()
                    break
                self.__current_cluster.add(point)
                self.__base.set_result(point, 1)
                self.__results_manager.signal_result_to_be_inserted()

    def __expand_cluster(self, point, neighbourhood):
        """Creates a cluster based on a given point and it's neighbourhood"""

        self.__current_cluster = set()
        self.__expansor_manager.add_point(point, neighbourhood)

        consumer = Thread(target=self.__add_points_to_cluster)
        consumer.start()

        self.__expansor_manager.wait_for_expansion()

        while not self.__cluster_finished():
            time.sleep(1)

        self.__expansor_manager.wait_for_expansion()
        self.__results_manager.wait_for_insertion_end()
        self.__results_manager.poison_cluster_inserter()

        consumer.join()

    def __discard_cluster(self, centroid, cluster):
        """Disconsider a given cluster and mark it's centroid as noise"""
        for point in cluster:
            self.__base.set_result(point, 0)
            self.__results_manager.add_result(-1, point, 0)
        self.__base.set_result(centroid, -1)
        self.__results_manager.add_result(-1, centroid, -1)
        self.__results_manager.wait_results_update()

    def set_base_negighbourhood_criteria(self, criteria_function):
        self.__base.set_negighbourhood_criteria(criteria_function)
        self.neighbourhood_criteria = criteria_function

    def neighbourhood_criteria(self, centroid, point):
        """  Checks for wheter a given point should be part of a neighbourhood

             Notice that the implementation must get done in a way that when
           centroid and point args are equal this must return true
        """
        raise NotImplementedError("Please implement this method")


    def fit(self):
        """For the given data, returns the clusters and result matrix"""
        clusters = []

        self.__expansor_manager.start_expansors()

        for x in range(0, self.__base.get_shape()[0]):         # pylint: disable=C0103,C0301
            for y in range(0, self.__base.get_shape()[1]):     # pylint: disable=C0103,C0301
                for z in range(0, self.__base.get_shape()[2]): # pylint: disable=C0103,C0301
                    if self.__base.get_result((x, y, z)) == 0:
                        neighbourhood = self.__base.get_neighbourhood((x, y, z))
                        if (len(neighbourhood) < self.__base.get_min_pts() or
                           self.__base.get_mask_val((x, y, z)) == 0 or
                           not self.neighbourhood_criteria((x, y, z), (x, y, z))): # pylint: disable=C0301
                            self.__base.set_result((x, y, z), -1)
                            self.__results_manager.add_result(-1, (x, y, z), -1)
                        else:
                            self.__results_manager.wait_results_update()
                            self.__expand_cluster((x, y, z),
                                                  neighbourhood)
                            if len(self.__current_cluster) >= self.__base.get_min_pts(): # pylint: disable=C0301
                                clusters.append(self.__current_cluster)
                            else:
                                self.__discard_cluster((x, y, z),
                                                       self.__current_cluster)

        self.__expansor_manager.end_expansors()

        return clusters, self.__base.get_results()
