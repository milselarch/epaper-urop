from PIL import Image, ImageOps
from numpy.ctypeslib import ndpointer
from itertools import permutations 

import matplotlib.pyplot as plt
import numpy as np
import ctypes as ct
import pyautogui 
import itertools
import time
import math
import os

class Updater(object):
    def __init__(self):
        self.screen_width = 1856 # 1872
        self.screen_height = 1392 # 1404
        self.last_img = None

        self.bits_per_pixel = 1
        self.bcmtest = self.load_dll()
        self.bcmtest.reset()
        self.bcmtest.clear_screen(self.bits_per_pixel)

        self.chunks = 25
        self.area = (self.screen_width * self.screen_height)
        self.chunk_length = int((self.area / self.chunks) ** 0.5)
        self.chunk_length -= self.chunk_length % 16

    def load_dll(self):
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

        return bcmtest

    def load_image(
        self, image, x=0, y=0,
        width=None, height=None
    ):
        if type(image) == str:
            image = Image.open(image)

        if width is None:
            width = image.width
        if height is None:
            height = image.height

        image = image.resize((width, height))
        gray_image = ImageOps.grayscale(image)
        arr = np.array(gray_image, dtype=np.uint8)
        height, width = arr.shape[0], arr.shape[1]
        res = (width, height)

        prev_arr = arr
        prev_res = res
        print('WH', width, height)
        # print('START-COORDS', coords)
        self.bcmtest.fast_draw_grayscale_array(
            x, y, width, height, arr
        )

        return gray_image

    def rescale(self, image, grayscale=True):        
        scale = max(
            image.width / self.screen_width,
            image.height / self.screen_height
        )

        print('SCALE', scale)
        width = int(image.width / scale)
        height = int(image.height / scale)
        width -= width % 16
        height -= height % 16

        image = image.resize((width, height))
        
        if grayscale:
            image = ImageOps.grayscale(image)
            image = np.array(image, dtype=np.uint8)

        return image

    def screenshot(self):
        screenshot = pyautogui.screenshot()
        arr = self.rescale(screenshot)
        return arr

    def draw_test(self, test, chunk, start_x, start_y, width, height):
        chunk = chunk.flatten()
        
        for y in range(height):
            for x in range(width):
                test[start_y+y, start_x+x] = chunk[
                    y * width + x
                ]

    def chunk_load_image(self, arr):
        if type(arr) == str:
            arr = Image.open(arr)

        scale = max(
            arr.height / self.screen_height,
            arr.width / self.screen_width
        )

        height = int(arr.height / scale)
        width = int(arr.width / scale)
        width -= width % 16
        height -= height % 16
        arr = arr.resize((width, height))

        arr = np.array(arr)
        test = np.zeros_like(arr)
        height, width = arr.shape[0], arr.shape[1]
        x_chunks = math.ceil(width / self.chunk_length)
        y_chunks = math.ceil(height / self.chunk_length)
        pairs = itertools.product(
            range(x_chunks), range(y_chunks)
        )

        for x_chunk, y_chunk in pairs:
            chunk = arr[
                self.chunk_length * (y_chunk):
                self.chunk_length * (y_chunk + 1),
                self.chunk_length * (x_chunk):
                self.chunk_length * (x_chunk + 1)
            ]

            assert len(chunk.shape) == 2
            print('CHUNK', x_chunk, y_chunk)
            
            self.draw_test(
                test, chunk, 
                self.chunk_length * (x_chunk),
                self.chunk_length * (y_chunk),
                chunk.shape[1], chunk.shape[0]
            )

            diff = self.chunk_length - chunk.shape[1]
        
            """
            self.bcmtest.fast_draw_grayscale_array(
                self.chunk_length * (x_chunks - x_chunk - 2) + diff,
                self.chunk_length * (y_chunk),
                chunk.shape[1], chunk.shape[0],
                np.array(chunk)
            )
            """
            self.bcmtest.fast_draw_grayscale_array(
                width - self.chunk_length * (x_chunk + 1) + diff,
                self.chunk_length * (y_chunk),
                chunk.shape[1], chunk.shape[0],
                np.array(chunk)
            )

            # plt.imshow(test)
            # plt.show()

    def draw(self, *args, **kwargs):
        self.bcmtest.fast_draw_grayscale_array(
            *args, **kwargs
        )

    def get_sub_chunk(self, arr, x_chunk, y_chunk):
        chunk = arr[
            self.chunk_length * (y_chunk):
            self.chunk_length * (y_chunk + 1),
            self.chunk_length * (x_chunk):
            self.chunk_length * (x_chunk + 1)
        ]
        prev_chunk = self.last_img[
            self.chunk_length * (y_chunk):
            self.chunk_length * (y_chunk + 1),
            self.chunk_length * (x_chunk):
            self.chunk_length * (x_chunk + 1)
        ]

        mismatches = chunk != prev_chunk
        if not mismatches.any():
            return None

        assert chunk.shape == prev_chunk.shape
        assert len(chunk.shape) == 2
        
        positions = np.where(mismatches)
        y_positions, x_positions = positions[0], positions[1]
        x_start, x_end = min(x_positions), max(x_positions)
        y_start, y_end = min(y_positions), max(y_positions)
        
        x_start -= x_start % 16
        x_end += (16 - x_end % 16) % 16
        x_end = min(x_end, chunk.shape[1])
        y_start -= y_start % 16
        y_end += (16 - y_end % 16) % 16
        y_end = min(y_end, chunk.shape[0])

        sub_chunk = chunk[y_start:y_end, x_start:x_end]
        sub_chunk = np.array(sub_chunk, dtype=np.uint8)
        print('CHUNK', x_chunk, y_chunk)
        return chunk, sub_chunk

    def show_image(self, arr):
        if type(arr) == str:
            arr = Image.open(arr)
            print('WH', arr.width, arr.height)
            arr = self.rescale(arr)
        
        height, width = arr.shape[0], arr.shape[1]
        self.draw(0, 0, width, height, arr)

    def show_depth_image(self, arr, bpp=8):
        if bpp != self.bits_per_pixel:
            self.bcmtest.clear_screen(bpp)
            self.bits_per_pixel = bpp

        height, width = arr.shape[0], arr.shape[1]
        self.bcmtest.draw_grayscale_array(
            0, 0, width, height, bpp, arr
        )

    def run(self, images=None):
        index = 0
        height, width = 0, 0

        while True:
            if images is None:
                arr = self.screenshot()
            else:
                try:
                    arr = images[index]
                except IndexError:
                    return

                if type(arr) == str:
                    arr = Image.open(arr)
                    arr = np.array(arr)

            if self.last_img is None:
                height, width = arr.shape[0], arr.shape[1]
                self.draw(
                    0, 0, width, height, arr
                )

                # input('INIT: ')
                self.last_img = arr
                continue

            height, width = arr.shape[0], arr.shape[1]
            x_chunks = math.ceil(width / self.chunk_length)
            y_chunks = math.ceil(height / self.chunk_length)
            pairs = itertools.product(
                range(x_chunks), range(y_chunks)
            )

            for x_chunk, y_chunk in pairs:
                print('CHUNK', x_chunk, y_chunk)
                result = self.get_sub_chunk(
                    arr, x_chunk, y_chunk
                )

                if result is None:
                    continue

                chunk, sub_chunk = result
                diff = self.chunk_length - chunk.shape[1]
                self.draw(
                    self.screen_width - 
                    self.chunk_length * (x_chunk + 1) + diff,
                    self.chunk_length * (y_chunk),
                    chunk.shape[1], chunk.shape[0],
                    np.array(chunk)
                )

                """
                self.draw(
                    self.screen_width - 
                    self.chunk_length * (x_chunk + 1) + diff,
                    self.chunk_length * (y_chunk),
                    chunk.shape[1], chunk.shape[0],
                    np.array(chunk)
                )
                """

            index += 1
            self.last_img = arr
            # input('PAUSE: ')

            

if __name__ == '__main__':
    updater = Updater()
    updater.run()
    