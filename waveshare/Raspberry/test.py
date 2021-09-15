from PIL import Image, ImageOps

import numpy as np
import numpy.ctypeslib as npct
from numpy.ctypeslib import ndpointer
import ctypes as ct
import os

UBYTE = ct.c_ubyte
PUBYTE = ct.POINTER(UBYTE)
pointer_type = ndpointer(dtype=np.uint8, ndim=1, flags='C')

x = np.arange(9.).reshape((3, 3))
print('X', x, x.__array_interface__['data'])
xpp = (x.__array_interface__['data'][0] 
      + np.arange(x.shape[0])*x.strides[0]).astype(np.uintp) 

print('XPP', xpp)
# raise ValueError

def ubyte_array_to_pointer(arr):
    """
    Converts a 2D numpy to ctypes 2D array. 
    Arguments:
        arr: [ndarray] 2D numpy float64 array
    Return:
        arr_ptr: [ctypes double pointer]
    """

    # Init needed data types
    ARR_DIMX = UBYTE * arr.shape[1]
    ARR_DIMY = PUBYTE * arr.shape[0]

    # Init pointer
    arr_ptr = ARR_DIMY()

    # Fill the 2D ctypes array with values
    for i, row in enumerate(arr):
        arr_ptr[i] = ARR_DIMX()

        for j, val in enumerate(row):
            arr_ptr[i][j] = val

    return arr_ptr

print('preload')
libdraw = npct.load_library('libdraw.so', os.path.dirname(__file__))

libdraw.test.restype = ct.c_int
libdraw.test.argtypes = [ct.c_int]
status_code = libdraw.test(1520)
print(f'test status', status_code)

libdraw.init_screen.restype = ct.c_int
libdraw.init_screen.argtypes = [ct.c_int]
status_code = libdraw.init_screen(1520)
print(f'init status', status_code)

raise ValueError
libdraw.draw_grayscale_array.restype = ct.c_void_p
libdraw.draw_grayscale_array.argtypes = [
    ct.c_ushort, ct.c_ushort,
    np.ctypeslib.ndpointer(
        dtype=np.uint8, ndim=2,
        flags='C_CONTIGUOUS'
    )
]

print(libdraw)
image = Image.open('screenshot.png')
gray_image = ImageOps.grayscale(image)
# gray_image.show()

arr = np.array(gray_image, dtype=np.uint8)
height, width = arr.shape[0], arr.shape[1]
print(arr, arr.shape)

libdraw.draw_grayscale_array(width, height, arr)

print('done')