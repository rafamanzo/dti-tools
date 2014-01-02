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
from threading import Thread
from multiprocessing import cpu_count, Process, JoinableQueue, Event
from multiprocessing.queues import Empty
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
        self.expandable_neighbours = JoinableQueue()
        self.to_be_inserted = JoinableQueue()
        self.worker_result_updates = []
        self.__workers = []
        self.idle_workers = []
        self.processing = Event()
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

    def __expand_neighbourhood(self, worker_id, point, neighbourhood):
        """Expands a given neighbourhood"""

        neighbour = point

        for neighbour in neighbourhood:
            if(self.__result[neighbour[0]][neighbour[1]][neighbour[2]] == 0): # pylint: disable-msg=C0301
                self.to_be_inserted.put(neighbour)
                self.__result[neighbour] = 1
                self.__add_result(worker_id, neighbour, 1)
                neighbour_neighbourhood = self.__neighbourhood(neighbour)
                if len(neighbour_neighbourhood) >= self.__min_pts:
                    self.expandable_neighbours.put((neighbour, neighbour_neighbourhood)) # pylint: disable-msg=C0301


    def __expansor(self, worker_id):
        """Expands a neighbourhood until it is not possible"""

        while (not self.processing.is_set() or
               not self.expandable_neighbours.empty()):
            try:
                resource = self.expandable_neighbours.get(True, 0.1)
                self.idle_workers[worker_id].clear()
                self.__expand_neighbourhood(worker_id, resource[0], resource[1])
                self.expandable_neighbours.task_done()
            except Empty:
                self.idle_workers[worker_id].set()

    def __results_updater(self, worker_id):
        """Updates the results map"""

        while not self.processing.is_set():
            try:
                resource = self.worker_result_updates[worker_id].get(True, 1)
                self.__result[resource[0]] = resource[1]
                self.worker_result_updates[worker_id].task_done()
            except Empty:
                time.sleep(1)

    def __add_result(self, worker_id, point, result):
        """Enqueue a new result for propagation"""
        for worker in range(0, cpu_count()):
            if worker != worker_id:
                self.worker_result_updates[worker].put((point, result))

    def __cluster_finished(self):
        """Checks wheter all the workers are idle"""
        finished = True

        for worker in range(0, cpu_count()):
            finished = finished and self.idle_workers[worker].is_set()

        return finished and self.expandable_neighbours.empty()

    def __add_points_to_cluster(self):
        """Consumes results"""
        while True:
            try:
                point = self.to_be_inserted.get(True, 0.1)
                if point == None:
                    self.to_be_inserted.task_done()
                    break
                self.__current_cluster.add(point)
                self.__result[point] = 1
                self.to_be_inserted.task_done()
            except Empty:
                pass

    def __expand_cluster(self, point, neighbourhood):
        """Creates a cluster based on a given point and it's neighbourhood"""

        self.__current_cluster = set()
        self.expandable_neighbours.put((point, neighbourhood))

        consumer = Thread(target=self.__add_points_to_cluster)
        consumer.start()

        self.expandable_neighbours.join()

        while not self.__cluster_finished():
            time.sleep(1)

        self.expandable_neighbours.join()
        self.to_be_inserted.join()
        self.to_be_inserted.put(None)

        consumer.join()

    def __worker(self, worker_id):
        """Worker process"""

        updater = Thread(target=self.__results_updater, args=(worker_id,))
        expansor = Thread(target=self.__expansor, args=(worker_id,))

        updater.start()
        expansor.start()

        updater.join()
        expansor.join()

    def __discard_cluster(self, centroid, cluster):
        """Disconsider a given cluster and mark it's centroid as noise"""
        for point in cluster:
            self.__result[point] = 0
        self.__result[centroid] = -1

    def __wait_results_update(self):
        """Barrier for result propagation"""
        for result_queue in self.worker_result_updates:
            result_queue.join()

    def fit(self):
        """For the given data, returns the clusters and result matrix"""
        clusters = []

        for worker in range(0, cpu_count()):
            self.idle_workers.append(Event())
            self.worker_result_updates.append(JoinableQueue())

        for worker in range(0, cpu_count()):
            self.__workers.append(Process(target=self.__worker, args=(worker,)))
            self.__workers[worker].start()

        for x in range(0, self.__shape[0]):         # pylint: disable-msg=C0103,C0301
            for y in range(0, self.__shape[1]):     # pylint: disable-msg=C0103,C0301
                for z in range(0, self.__shape[2]): # pylint: disable-msg=C0103,C0301
                    if self.__result[x][y][z] == 0:
                        neighbourhood = self.__neighbourhood((x, y, z))
                        if (len(neighbourhood) < self.__min_pts or
                           self.__mask[x][y][z] == 0 or
                           not self.neighbourhood_criteria((x, y, z), (x, y, z))): # pylint: disable-msg=C0301
                            self.__result[x][y][z] = -1
                            self.__add_result(-1, (x, y, z), -1)
                        else:
                            self.__wait_results_update()
                            self.__expand_cluster((x, y, z),
                                                  neighbourhood)
                            if len(self.__current_cluster) >= self.__min_pts:
                                clusters.append(self.__current_cluster)
                            else:
                                self.__discard_cluster((x, y, z),
                                                       self.__current_cluster)

        self.processing.set()

        for worker in range(0, cpu_count()):
            self.__workers[worker].join()

        return clusters, self.__result
