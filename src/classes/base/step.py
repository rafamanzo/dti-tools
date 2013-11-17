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

"""Container for the Step class"""

class Step(object):
    """Abstract class that defines how a pipeline step should look like"""

    def validate_args(self): # pylint: disable-msg=R0201
        """Checks wether the given arguments are valid"""
        return True

    def load_data(self): # pylint: disable-msg=R0201
        """Loads any data necessary during the step processing"""
        return True

    def save(self): # pylint: disable-msg=R0201
        """Saves the results of the processing"""
        return True

    def process(self): # pylint: disable-msg=R0201
        """Do the processing"""
        raise NotImplementedError("Please implement this method")

    def run(self):
        """Calls all the other method on the proper order"""
        if self.validate_args():
            self.load_data()
            self.process()
            self.save()
