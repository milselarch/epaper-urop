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

print('pre-test')
result = bcmtest.reset()
bcmtest.clear_screen(bits_per_pixel)

def open_image(
    image, bpp=None, x=0, y=0,
    width=None, height=None
):
    global bits_per_pixel
    global prev_arr
    global prev_res

    if bpp is None:
        bpp = bits_per_pixel
    elif bpp != bits_per_pixel:
        bcmtest.change_bits_per_pixel(bpp)
        bits_per_pixel = bpp

    print(f'test status', result)

    print(bcmtest)
    if type(image) == str:
        image = Image.open(image)

    if width is None:
        width = image.width
    if height is None:
        height = image.height

    width -= width % 16
    height -= height % 16

    image = image.resize((width, height))
    gray_image = ImageOps.grayscale(image)
    arr = np.array(gray_image, dtype=np.uint8)
    height, width = arr.shape[0], arr.shape[1]
    res = (width, height)

    x -= x % 16
    y -= y % 16

    prev_arr = arr
    prev_res = res
    print('WH', width, height)
    # print('START-COORDS', coords)
    bcmtest.fast_draw_grayscale_array(
        x, y, width, height, arr
    )

frame_no = 0

while True:
    print(f'frame no: {frame_no}')
    screenshot = pyautogui.screenshot()
    open_image(screenshot, width=SW, height=SH)
    # open_image(screenshot, width=SW//2, height=SH//2, x=200, y=200)
    # WH 936 696
    # open_image(screenshot, width=1600, height=600, x=0, y=0)
    frame_no += 1                            
