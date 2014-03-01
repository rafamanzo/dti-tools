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

"""Container for DBSCANExpansor class"""

from threading import Thread
import time
from multiprocessing.queues import Empty

class DBSCANExpansor(object):
    """docstring for DBSCANExpansor"""
    def __init__(self, expansor_id, results_manager, base, processing_finished, expandables_queue, idling): # pylint: disable=C0301
        self.__id = expansor_id
        self.__processing_finished = processing_finished
        self.__expandables_queue = expandables_queue
        self.__results_manager = results_manager
        self.__base = base
        self.__idling = idling

    def __expand_neighbourhood(self, point, neighbourhood):
        """Expands a given neighbourhood"""

        neighbour = point

        for neighbour in neighbourhood:
            if(self.__base.get_result(neighbour) == 0): # pylint: disable=C0301
                self.__base.set_result(neighbour, 1)
                self.__results_manager.add_result(self.__id, neighbour, 1)
                neighbour_neighbourhood = self.__base.get_neighbourhood(neighbour) # pylint: disable=C0301
                if len(neighbour_neighbourhood) >= self.__base.get_min_pts():
                    self.__expandables_queue.put((neighbour, neighbour_neighbourhood)) # pylint: disable=C0301

    def __expansor(self):
        """Expands a neighbourhood until it is not possible"""

        while (not self.__processing_finished.is_set() or
               not self.__expandables_queue.empty()):
            try:
                resource = self.__expandables_queue.get(True, 0.1)
                self.__idling.clear()
                self.__expand_neighbourhood(resource[0], resource[1])
                self.__expandables_queue.task_done()
            except Empty:
                self.__idling.set()

    def __results_updater(self):
        """Updates the results map"""

        while not self.__processing_finished.is_set():
            presence, resource = self.__results_manager.get_result_update_for(self.__id) # pylint: disable=C0301

            if presence:
                self.__base.set_result(resource[0], resource[1])
                self.__results_manager.signal_result_updated_for(self.__id)
            else:
                time.sleep(0.1)

    def start(self):
        """Starts to accept points to get expanded and process them"""

        updater = Thread(target=self.__results_updater)
        expansor = Thread(target=self.__expansor)

        updater.start()
        expansor.start()

        updater.join()
        expansor.join()
