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

"""Container for the CPUParallelStep class"""

import multiprocessing        # Useful on getting the processor count
from multiprocessing import Process, Queue
import multiprocessing.queues as mq
from threading import Thread

from src.classes.base.step import Step

class CPUParallelStep(Step): # pylint: disable-msg=R0903
    """Abstract class to represent pipeline steps that can be
       parallelized on CPU

    """
    def __init__(self):
        self.workers = []
        self.shape = (0, 0, 0, 0)
        self.queue = Queue()
        self.__processing = True

    def __start_worker(self, workers_count, partition_size, extra_size):
        """Given a partition of the dataset, starts the thread to process it"""
        i = len(self.workers) + 1

        if i == workers_count:
            self.workers.append(
                Process(target=self.process_partition,
                       args=(((i - 1)*partition_size,
                               i*partition_size + extra_size),
                             (0, self.shape[1]),
                             (0, self.shape[2]))
                )
            )
        else:
            self.workers.append(
                Process(target=self.process_partition,
                       args=(((i - 1)*partition_size, i*partition_size),
                             (0, self.shape[1]),
                             (0, self.shape[2]))
                )
            )

        self.workers[i-1].start()

    def __join_workers(self):
        """Barrier to make sure that all the threads have finished"""
        for i in range(0, len(self.workers)):
            self.workers[i].join()

    def process_partition(self, x_range, y_range, z_range):
        """Unimplemented method that should contain
           the logic for partition processing

        """
        raise NotImplementedError("Please implement this method")

    def consume_product(self, product):
        """Unimplemented method that should contain
           the logic for consuming a given data from the queue

        """
        raise NotImplementedError("Please implement this method")

    def __consumer(self):
        """Thread that consumes elements from the queue"""

        while (not self.queue.empty()) or self.__processing:
            try:
                self.consume_product(self.queue.get(True, 1))
            except mq.Empty:
                pass

    def __sequential_fallback(self):
        """When there is just one processor"""

        self.process_partition((0, self.shape[0]),
                               (0, self.shape[1]),
                               (0, self.shape[2]))
        self.__processing = False
        while not self.queue.empty():
            self.consume_product(self.queue.get())

    def workers_count(self): # pylint: disable-msg=R0201
        """Returns the cpu count"""

        return multiprocessing.cpu_count()

    def process(self):
        workers_count = self.workers_count()
        if workers_count > 1:
            partition_size = int(self.shape[0]/workers_count)
            extra_size = self.shape[0] % workers_count

            for _ in range(1, workers_count+1):
                self.__start_worker(workers_count, partition_size, extra_size)
            manager = Thread(target=self.__join_workers)
            consumer = Thread(target=self.__consumer)
            manager.start()
            consumer.start()

            manager.join()
            self.__processing = False
            consumer.join()
        else:
            self.__sequential_fallback()
