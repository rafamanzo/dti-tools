"""Apparent Diffusion Coefficient"""
def adc(tensor, acquisition_direction):
    return acquisition_direction.cartesian().T*tensor.matrix*acquisition_direction.cartesian()
