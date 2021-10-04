from PIL import Image, ImageOps
from numpy.ctypeslib import ndpointer

import faulthandler
import numpy as np
import ctypes as ct
import pyautogui 
import time
import os

SCREEN_WIDTH, SCREEN_HEIGHT = 1872, 1404
SW, SH = SCREEN_WIDTH, SCREEN_HEIGHT

faulthandler.enable()
bits_per_pixel = 1

bcmtest = ct.CDLL('./bcmtest.so')
bcmtest.reset.restype = ct.c_int
bcmtest.reset.argtypes = []

bcmtest.clear_screen.restype = ct.c_void_p
bcmtest.clear_screen.argtypes = [ct.c_ushort]

bcmtest.change_bits_per_pixel.restype = ct.c_void_p
bcmtest.change_bits_per_pixel.argtypes = [ct.c_ushort]

bcmtest.draw_grayscale_array.restype = ct.c_int
bcmtest.draw_grayscale_array.argtypes = [
    ct.c_int, ct.c_int,
    ct.c_ushort, ct.c_ushort, ct.c_ushort,
    np.ctypeslib.ndpointer(
        dtype=np.uint8, ndim=2,
        flags='C_CONTIGUOUS'
    )
]

bcmtest.fast_draw_grayscale_array.restype = ct.c_int
bcmtest.fast_draw_grayscale_array.argtypes = [
    ct.c_int, ct.c_int, ct.c_int, ct.c_int,
    np.ctypeslib.ndpointer(
        dtype=np.uint8, ndim=2,
        flags='C_CONTIGUOUS'
    )
]

bcmtest.Dynamic_GIF_Example.restype = ct.c_int
bcmtest.Dynamic_GIF_Example.argtypes = []

print('pre-test')
result = bcmtest.reset()
bcmtest.Dynamic_GIF_Example()

