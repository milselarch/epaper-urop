from PIL import Image, ImageOps, ImageChops
from numpy.ctypeslib import ndpointer

import faulthandler
import numpy as np
import ctypes as ct
import pyautogui 
import os

faulthandler.enable()
bits_per_pixel = 8

bcmtest = ct.CDLL('./bcmtest.so')
bcmtest.reset.restype = ct.c_int
bcmtest.reset.argtypes = []

bcmtest.clear_screen.restype = ct.c_void_p
bcmtest.clear_screen.argtypes = [ct.c_ushort]

bcmtest.change_bits_per_pixel.restype = ct.c_void_p
bcmtest.change_bits_per_pixel.argtypes = [ct.c_ushort]

bcmtest.draw_grayscale_array.restype = ct.c_int
bcmtest.draw_grayscale_array.argtypes = [
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

    # image = Image.open('screenshot.png')
    # width, height = 1872, 1404
    width, height = 1872, 1404
    image = image.resize((width, height))
    gray_image = ImageOps.grayscale(image)
    # gray_image.show()

    arr = np.array(gray_image, dtype=np.uint8)
    # arr2 = arr.flatten()
    # arr = 255 - arr

    height, width = arr.shape[0], arr.shape[1]
    # print(arr, arr.shape)

    bcmtest.draw_grayscale_array(
        width, height, bpp, arr
    )

open_image('/home/pi/Downloads/alena-aenami-quiet-1px.jpg')
open_image('screenshot.png', bpp=2)

class BoundingBox:
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.pixels = [] # empty initially
	
	def fill(self, sourceImage):
		for currY in range(self.y, self.y + self.height):
			self.pixels.append([])
			for currX in range(self.x, self.x + self.width):
				self.pixels[currY - self.y].append(sourceImage.getpixel((currX,currY)))

def openBoundingBoxes(boundingBoxArray, bpp=None):
	global bits_per_pixel

	if bpp is None:
		bpp = bits_per_pixel
	elif bpp != bits_per_pixel:
		bcmtest.change_bits_per_pixel(bpp)
		bits_per_pixel = bpp
	
	for boundingBox in boundingBoxArray:
		arr = np.array(boundingBox.pixels, dtype=np.uint8)
		bcmtest.draw_grayscale_array(
			boundingBox.width, boundingBox.height, bpp, arr
		)

newScreenshot = pyautogui.screenshot().convert("L")
while True:
	oldScreenshot = newScreenshot
	newScreenshot = pyautogui.screenshot().convert("L")
	diff = ImageChops.difference(oldScreenshot, newScreenshot)

	newScreenshotSlice = Image.new(mode="RGB", size=(diff.width, diff.height))

	for x in range(diff.width):
		for y in range(diff.height):
			if diff.getpixel((x,y)) != 0:
				newScreenshotSlice.putpixel((x,y), newScreenshot.getpixel((x,y)))
	
	rowHasSomething = False
	xMin = newScreenshotSlice.width
	yMin = newScreenshotSlice.height
	xMax = yMax = 0
	boundingBoxArray = []
	for y in range(newScreenshotSlice.height):
		oldXMin = xMin
		oldYMin = yMin
		rowHasSomething = False
		for x in range(newScreenshotSlice.width):
			currPixel = newScreenshotSlice.getpixel((x,y))
			if currPixel != (0,0,0):
				rowHasSomething = True
			if rowHasSomething:
				if currPixel != (0,0,0):
					if xMin > x:
						xMin = x
					if xMax < x:
						xMax = x
		if rowHasSomething:
			if currPixel != (0,0,0):
				if yMin > y:
					yMin = y
				if yMax < y:
					yMax = y
		else:
			if oldXMin == xMin or oldYMin == yMin:
				pass
			else:
				boundingBoxArray.append(BoundingBox(xMin, yMin, xMax-xMin, yMax-yMin))

	for boundingBox in boundingBoxArray:
		boundingBox.fill()
	
	openBoundingBoxes(boundingBoxArray)

