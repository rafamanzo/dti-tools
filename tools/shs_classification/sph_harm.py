from scipy.special import sph_harm as sp_sph_harm

def sph_harm(l, m, acquisition_direction):
  _, theta, phi = acquisition_direction.spherical()

  return sp_sph_harm(m,l,phi,theta) # SciPy inverts phi and theta