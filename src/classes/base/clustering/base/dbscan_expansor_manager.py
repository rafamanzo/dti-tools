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

"""Container for DBSCANExpansorManager class"""

from multiprocessing import cpu_count, Process, JoinableQueue, Event

from src.classes.base.clustering.base.dbscan_expansor import DBSCANExpansor

class DBSCANExpansorManager(object):
    """docstring for DBSCANExpansorManager"""
    def __init__(self, expansor_count, results_manager, base):
        self.__expansor_count = expansor_count
        self.__expansors = []
        self.__processing_finished = Event()
        self.__idle_expansors = []
        self.__expandable_neighbours = JoinableQueue()
        self.__results_manager = results_manager
        self.__base = base

    def start_expansors(self):
        """Instantiates processes with expansors and starts them"""
        for expansor_id in range(0, self.__expansor_count):
            self.__idle_expansors.append(Event())
            base_expansor = DBSCANExpansor(expansor_id, self.__results_manager,
                                self.__base, self.__processing_finished,
                                self.__expandable_neighbours,
                                self.__idle_expansors[expansor_id])
            self.__expansors.append(Process(target=base_expansor.start))
            self.__expansors[expansor_id].start()


    def all_idling(self):
        """Returns True if all the expansors are idling"""
        for expansor in range(0, self.__expansor_count):
            if not self.__idle_expansors[expansor].is_set():
                return False

        return True

    def nothing_to_expand(self):
        """Returns True if the expandable neighbours queue is empty"""
        return self.__expandable_neighbours.empty()

    def end_expansors(self):
        """Signal the expansors process to exit the loop and joins them"""
        self.__processing_finished.set()

        for expansor in range(0, cpu_count()):
            self.__expansors[expansor].join()

    def add_point(self, point, neighbourhood):
        """Adds a point to the expandable neighbours queue"""
        self.__expandable_neighbours.put((point, neighbourhood))

    def wait_for_expansion(self):
        """Wait until all the expandable points get expanded"""
        self.__expandable_neighbours.join()
