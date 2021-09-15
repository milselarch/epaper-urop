from PIL import Image, ImageOps

import numpy as np
import numpy.ctypeslib as npct
from numpy.ctypeslib import ndpointer
import ctypes as ct
import os

image = Image.open('screenshot.png')
gray_image = ImageOps.grayscale(image)
gray_image.show()

arr = np.array(gray_image, dtype=np.uint8)
height, width = arr.shape[0], arr.shape[1]
print(arr, arr.shape)