from PIL import Image, ImageOps
from numpy.ctypeslib import ndpointer

import faulthandler
import numpy as np
import ctypes as ct
import pyautogui 
import os

SCREEN_WIDTH, SCREEN_HEIGHT = 1872, 1404
faulthandler.enable()
bits_per_pixel = 2

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

print('pre-test')
result = bcmtest.reset()
bcmtest.clear_screen(bits_per_pixel)

def open_image(image, bpp=None):
    global bits_per_pixel

    if bpp is None:
        bpp = bits_per_pixel
    elif bpp != bits_per_pixel:
        bcmtest.change_bits_per_pixel(bpp)
        bits_per_pixel = bpp

    print(f'test status', result)

    print(bcmtest)
    if type(image) == str:
        image = Image.open(image)

    scale = min(
        SCREEN_WIDTH / image.width,
        SCREEN_HEIGHT / image.height
    )

    width = int(image.width * scale)
    height = int(image.height * scale)

    image = image.resize((width, height))
    gray_image = ImageOps.grayscale(image)
    # gray_image.show()

    arr = np.array(gray_image, dtype=np.uint8)
    # arr2 = arr.flatten()
    # arr = 255 - arr

    height, width = arr.shape[0], arr.shape[1]
    print(arr, arr.shape)

    bcmtest.draw_grayscale_array(
        0, 0, width, height, bpp, arr
    )
    input('>>> ')

# open_image('/home/pi/Downloads/alena-aenami-quiet-1px.jpg')
# open_image('screenshot.png', bpp=2)

while True:
	screenshot = pyautogui.screenshot()
	open_image(screenshot)
                                              
