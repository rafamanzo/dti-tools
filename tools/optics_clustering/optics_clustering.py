#!/usr/bin/python3

###########
# Imports #
###########

import sys
import math as m
from heapq import heappush, heappop

import numpy as np
import nibabel as nib
from sortedcontainers import SortedList # Used for core-dist calculation

#####################
# Auxiliary Classes #
#####################

class Point(object):
  def __init__(self, coordinates):
    super(Point, self).__init__()
    self.coordinates = coordinates
    self.reachability_distance = -1
    self.core_distance = self.__core_distance()

  def neighbour_coordinates(self):
    n = []

    x_range = range(max(0, self.coordinates[0] - eps), min(mask.shape[0], self.coordinates[0] + eps))
    y_range = range(max(0, self.coordinates[1] - eps), min(mask.shape[1], self.coordinates[1] + eps))
    z_range = range(max(0, self.coordinates[2] - eps), min(mask.shape[2], self.coordinates[2] + eps))

    for x in x_range:
      for y in y_range:
        for z in z_range:
          neighbour = (x,y,z)

          if mask_data[neighbour] > 0:
            if m.fabs(data[self.coordinates] - data[neighbour]) <= max_difference:
              n.append(neighbour)

    return n

  def __core_distance(self):
    if len(self.neighbour_coordinates()) < min_pts:
      return -1
    else:
      stop_on_next_it = False

      for search_radius in range(1, eps + 2):
        visited = SortedList([])
        x_range = range(max(0, self.coordinates[0] - search_radius), min(mask.shape[0], self.coordinates[0] + search_radius))
        y_range = range(max(0, self.coordinates[1] - search_radius), min(mask.shape[1], self.coordinates[1] + search_radius))
        z_range = range(max(0, self.coordinates[2] - search_radius), min(mask.shape[2], self.coordinates[2] + search_radius))

        for x in x_range:
          for y in y_range:
            for z in z_range:
              if mask_data[(x,y,z)] > 0:
                if m.fabs(data[self.coordinates] - data[(x,y,z)]) <= max_difference:
                  visited.add(distance(self.coordinates, (x,y,z)))

        if stop_on_next_it:
          return visited[min_pts - 1]

        if len(visited) >= min_pts:
          stop_on_next_it = True

  def __lt__(self, other):
    if self.reachability_distance == -1:
      return False
    else:
      return self.reachability_distance < other.reachability_distance

#######################
# Auxiliary Functions #
#######################

# FIXME: it will be wrong for non isotropic voxel distances
def distance(a_coordinates, b_coordinates):
  return m.sqrt((a_coordinates[0] - b_coordinates[0])**2 + (a_coordinates[1] - b_coordinates[1])**2 + (a_coordinates[2] - b_coordinates[2])**2)

def update(point, seeds):
  for neighbour_coordinate in point.neighbour_coordinates():
    neighbour = get_point(neighbour_coordinate)
    if clusters[neighbour.coordinates] == -1:
      new_reach_dist = max(point.core_distance, distance(point.coordinates, neighbour.coordinates))
      if neighbour.reachability_distance == -1:
        neighbour.reachability_distance = new_reach_dist
        heappush(seeds, neighbour)
      elif new_reach_dist < neighbour.reachability_distance:
        seeds.remove(neighbour)
        neighbour.reachability_distance = new_reach_dist
        heappush(seeds, neighbour)

def get_point(coordinates):
  if points[coordinates] == None:
    points[coordinates] = Point(coordinates)

  return points[coordinates]

##################
# Initialization #
##################

data = nib.load(sys.argv[1]).get_data()
mask = nib.load(sys.argv[2])
eps = int(sys.argv[3])
min_pts = int(sys.argv[4])
max_difference = float(sys.argv[5])
mask_data = mask.get_data()
clusters = -1*np.ones(mask.shape, dtype=np.int16)
cluster_index = 1
ordered_points = []
points = np.array([[[None for i in range(mask.shape[2])] for i in range(mask.shape[1])] for i in range(mask.shape[0])])

##################
# Implementation #
##################

# Ordering
for i in range(mask.shape[0]):
  for j in range(mask.shape[1]):
    for k in range(mask.shape[2]):
      point = get_point((i,j,k))
      if clusters[point.coordinates] == -1:
        if mask_data[point.coordinates] > 0:
          clusters[point.coordinates] = 0
          ordered_points.append(point)
          if point.core_distance != -1:
            seeds = []
            update(point, seeds)
            while len(seeds) > 0:
              seed = heappop(seeds)
              clusters[seed.coordinates] = 0
              ordered_points.append(seed)
              if seed.core_distance != -1:
                update(seed, seeds)
        else:
          clusters[point.coordinates] = 0

# Extract clusters following DBSCAN with eps 1
for point in ordered_points:
  if point.reachability_distance > 1.0 or point.reachability_distance == -1:
    if point.core_distance <= 1.0:
      clusters[point.coordinates] = cluster_index
      cluster_index += 1
  else:
    clusters[point.coordinates] = cluster_index

##########
# Output #
##########

nib.Nifti1Image(clusters, mask.get_affine()).to_filename("%s" % sys.argv[6])