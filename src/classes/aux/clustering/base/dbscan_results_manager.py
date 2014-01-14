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

"""Container for DBSCANResultsManager class"""

from multiprocessing import JoinableQueue
from multiprocessing.queues import Empty

class DBSCANResultsManager(object):
    """docstring for DBSCANResultsManager"""
    def __init__(self, expansor_count):
        self.__expansor_count = expansor_count
        self.__result_update_queues = []
        self.__to_be_inserted = JoinableQueue()

        for _ in range(0, expansor_count):
            self.__result_update_queues.append(JoinableQueue())

    def add_result(self, expansor_id, point, result):
        """Spreads the results between all the expansors"""
        if expansor_id >= 0:
            self.__to_be_inserted.put(point)

        for expansor in range(0, self.__expansor_count):
            if expansor != expansor_id:
                self.__result_update_queues[expansor].put((point, result))

    def wait_results_update(self):
        """Wait until all the expansors get the updates"""
        for result_queue in self.__result_update_queues:
            result_queue.join()

    def poison_cluster_inserter(self):
        """Finishes the loop for cluster points insertion"""
        self.__to_be_inserted.put(None)

    def get_result_to_be_inserted(self):
        """Get a point from insertion queues

            If there is something to insert, returns True and the point
            Otherwise, return False and None
        """
        try:
            result = self.__to_be_inserted.get(True, 0.1)
            return (True, result)
        except Empty:
            return (False, None)

    def signal_result_to_be_inserted(self):
        """Signal that the previous acquired result has been inserted"""
        self.__to_be_inserted.task_done()

    def wait_for_insertion_end(self):
        """Wait until all the points get inserted"""
        self.__to_be_inserted.join()

    def get_result_update_for(self, expansor_id):
        """Get a result from given expansor_id queue

            If there is something to update, returns True and the result
            Otherwise, return False and None
        """
        try:
            result = self.__result_update_queues[expansor_id].get(True, 0.1)
            return (True, result)
        except Empty:
            return (False, None)

    def signal_result_updated_for(self, expansor_id):
        """   Signal that the previous result on the given expansor_id
            queue has been updated
        """
        self.__result_update_queues[expansor_id].task_done()
