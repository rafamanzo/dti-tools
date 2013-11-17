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

from threading import Thread  # Makes possible to create threads
import multiprocessing        # Useful on getting the processor count

from src.classes.base.step import Step

class CPUParallelStep(Step):
    def __init__(self):
        self.workers = []

    def __start_worker(self, workers_count, partition_size, extra_size):
        i = len(self.workers) + 1

        if i == workers_count:
            self.workers.append(
                Thread(target=self.process_partition,
                       args=(((i - 1)*partition_size,
                               i*partition_size + extra_size),
                             (0, self.shape[1]),
                             (0, self.shape[2]))
                )
            )
        else:
            self.workers.append(
                Thread(target=self.process_partition,
                       args=(((i - 1)*partition_size, i*partition_size),
                             (0, self.shape[1]),
                             (0, self.shape[2]))
                )
            )

        self.workers[i-1].start()

    def __join_workers(self):
        for i in range(0, len(self.workers)):
            self.workers[i].join()

    def process_partition(self, x_range, y_range, z_range):
        raise NotImplementedError("Please implement this method")

    def process(self):
        workers_count = multiprocessing.cpu_count()
        partition_size = int(self.shape[0]/workers_count)
        extra_size = self.shape[0]%workers_count

        for i in range(1, workers_count+1):
            self.__start_worker(workers_count, partition_size,extra_size)

        self.__join_workers()
