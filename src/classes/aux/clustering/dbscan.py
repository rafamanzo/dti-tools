# This file is part of Improving Tractogrophy
# Copyright (C) 2013 it's respectives authors (please see the AUTHORS file)
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

import numpy as np
from multiprocessing import cpu_count, Process, Queue, Value, Array
from multiprocessing.queues import Empty
from threading import Thread
import time

# pylint: disable-msg=R0903,R0922

class DBSCAN(object):
    """Implementation of the DBSCAN clustering algorithm"""

    def __init__(self, eps, min_pts, mask, shape):
        super(DBSCAN, self).__init__()
        self.__eps = eps
        self.__min_pts = min_pts
        self.__mask = mask
        self.__shape = shape
        self.__result = np.zeros(self.__shape,  # pylint: disable-msg=E1101
                                 dtype=np.int8) # pylint: disable-msg=E1101
        self.expandable_neighbours = Queue()
        self.to_be_inserted = Queue()
        self.__workers = []
        self.idle_workers = Queue()
        self.processing = Queue()
        self.__current_cluster = set()

    def neighbourhood_criteria(self, centroid, point):
        """  Checks for wheter a givens point should be part of a beighbourhood

             Notice that the implementation must get done in a way that when
           centroid and point args are equal this must return true
        """
        raise NotImplementedError("Please implement this method")

    def __neighbourhood(self, point):
        """Receive a point and returns a set with it's neighbourhood"""
        neighbourhood = {point}

        for x in range(max((point[0] - self.__eps, 0)),                       # pylint: disable-msg=C0103,C0301
                       min(self.__shape[0], point[0] + self.__eps + 1)):
            for y in range(max((point[1] - self.__eps, 0)),                   # pylint: disable-msg=C0103,C0301
                           min(self.__shape[1], point[1] + self.__eps + 1)):
                for z in range(max((point[2] - self.__eps, 0)),               # pylint: disable-msg=C0103,C0301
                               min(self.__shape[2], point[2] + self.__eps + 1)):
                    if (self.__mask[x][y][z] and
                            self.neighbourhood_criteria(point, (x, y, z))):
                        neighbourhood.add((x, y, z))

        return neighbourhood

    def __expand_neighbourhood(self, point, neighbourhood):
        neighbour = point

        for neighbour in neighbourhood:
            if(self.__result[neighbour[0]][neighbour[1]][neighbour[2]] == 0 and
               self.__mask[neighbour[0]][neighbour[1]][neighbour[2]] == 1 and
               self.neighbourhood_criteria(point,
                                           (neighbour[0], neighbour[1], neighbour[2]))): # pylint: disable-msg=C0301
                self.to_be_inserted.put(neighbour)
                self.__result[neighbour] = 1
                neighbour_neighbourhood = self.__neighbourhood(neighbour)
                if len(neighbour_neighbourhood) >= self.__min_pts:
                    self.expandable_neighbours.put((neighbour, neighbour_neighbourhood))
        

    def __expansor(self, id):
        """Expands a neighbourhood until it is not possible"""

        active = True

        while self.processing.empty() or not self.expandable_neighbours.empty():
            try:
                resource = self.expandable_neighbours.get(True, 1)
                if not active:
                    active = True
                    self.idle_workers.get()
                self.__expand_neighbourhood(resource[0], resource[1])
            except Empty:
                if active:
                    active = False
                    self.idle_workers.put(id)


    def __join_workers(self, worker_count):
        active = True
        while active:
            if self.idle_workers.qsize() >= worker_count and self.expandable_neighbours.empty():
                active = False
                self.processing.put(0)
            else:
                time.sleep(1)

        for worker in range(0, worker_count):
            self.__workers[worker].join()

    def __add_points_to_cluster(self):
        while self.processing.empty() or not self.to_be_inserted.empty():
            try:
                point = self.to_be_inserted.get(True, 1)
                self.__current_cluster.add(point)
                self.__result[point] = 1
            except Empty:
                time.sleep(1)

    def __expand_cluster(self, point, neighbourhood):
        """Creates a cluster based on a given point and it's neighbourhood"""
        worker_count = cpu_count()
        self.__workers = []
        self.active_workers = Array('i', np.ones(worker_count, np.int_))
        self.expandable_neighbours.put((point, neighbourhood))
        self.processing = Queue()
        self.idle_workers = Queue()
        self.__current_cluster = set()

        for worker in range(0, worker_count):
            self.__workers.append(Process(target=self.__expansor, args=(worker,)))
            self.__workers[worker].start()

        manager = Thread(target=self.__join_workers, args=(worker_count,))
        consumer = Thread(target=self.__add_points_to_cluster)
        manager.start()
        consumer.start()

        manager.join()
        consumer.join()


    def __discard_cluster(self, centroid, cluster):
        """Disconsider a given cluster and mark it's centroid as noise"""
        for point in cluster:
            self.__result[point] = 0
        self.__result[centroid] = -1


    def fit(self):
        """For the given data, returns the clusters and result matrix"""
        clusters = []
        for x in range(0, self.__shape[0]):         # pylint: disable-msg=C0103,C0301
            for y in range(0, self.__shape[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(0, self.__shape[2]): # pylint: disable-msg=C0103,C0301
                    if self.__result[x][y][z] == 0:
                        neighbourhood = self.__neighbourhood((x, y, z))
                        if (len(neighbourhood) < self.__min_pts or
                           self.__mask[x][y][z] == 0 or
                           not self.neighbourhood_criteria((x, y, z), (x, y, z))): # pylint: disable-msg=C0301
                            self.__result[x][y][z] = -1
                        else:
                            self.__expand_cluster((x, y, z),
                                                  neighbourhood)
                            if len(self.__current_cluster) >= self.__min_pts:
                                clusters.append(self.__current_cluster)
                            else:
                                self.__discard_cluster((x, y, z), self.__current_cluster)

        return clusters, self.__result
