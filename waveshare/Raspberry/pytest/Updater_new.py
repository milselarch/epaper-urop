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
import SharedArray as sa

import threading
import asyncio
import multiprocessing as mp

shared_last_screenshot = sa.create("shm://test", (1600,2144))
shared_curr_screenshot = sa.create("shm://test", (1600,2144))

class Updater(object):
    def __init__(self):
        self.screen_width = 1856 # 1872
        self.screen_height = 1392 # 1404

        self.bits_per_pixel = 1
        self.bcmtest = self.load_dll()
        self.bcmtest.reset()
        self.bcmtest.clear_screen(self.bits_per_pixel)

        self.chunks = 25
        self.area = (self.screen_width * self.screen_height)
        self.chunk_length = int((self.area / self.chunks) ** 0.5)
        self.chunk_length -= self.chunk_length % 16

        self.shared_width = mp.Value(ct.c_uint8, 0)
        self.shared_height = mp.Value(ct.c_uint8, 0)

        temp = self.screenshot()
        print(self.shared_height, self.shared_width)

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

    def screenshot(self):
        screenshot = pyautogui.screenshot()
        scale = max(
            screenshot.width / self.screen_width,
            screenshot.height / self.screen_height
        )

        width = int(self.screen_width / scale)
        height = int(self.screen_height / scale)
        width -= width % 16
        height -= height % 16

        self.shared_width = width
        self.shared_height = height

        screenshot = screenshot.resize((width, height))
        gray_image = ImageOps.grayscale(screenshot)
        arr = np.array(gray_image, dtype=np.uint8)
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

    def get_sub_chunk(self, x_chunk, y_chunk):
        global shared_curr_screenshot
        global shared_last_screenshot
        #print(self.chunk_length, self.chunk_length * (y_chunk))
        chunk = shared_curr_screenshot[
            self.chunk_length * (y_chunk):
            self.chunk_length * (y_chunk + 1),
            self.chunk_length * (x_chunk):
            self.chunk_length * (x_chunk + 1)
        ]
        prev_chunk = shared_last_screenshot[
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

    def take_screenshot(self):
        global shared_curr_screenshot
        global shared_last_screenshot
        temp = self.screenshot()
        print(temp.shape)
        np.copyto(shared_curr_screenshot, temp)
        while True:
            np.copyto(shared_last_screenshot, shared_curr_screenshot)
            np.copyto(shared_curr_screenshot, self.screenshot())
            print("TS", shared_curr_screenshot)
            print("OTHER", shared_last_screenshot)

    def constant_update(self):
        print("constant_update", self.shared_height, self.shared_width)
        while True:
            """
            curr = np.frombuffer(
            shared_curr_screenshot,
            dtype=np.uint8
            ).reshape(
                self.shared_height,
                self.shared_width
            )
            last = np.frombuffer(
            shared_last_screenshot,
            dtype=np.uint8
            ).reshape(
                self.shared_height,
                self.shared_width
            )
            """
            global shared_curr_screenshot
            global shared_last_screenshot
            print("CURR", shared_curr_screenshot)
            print("PREV", shared_last_screenshot)
            if shared_curr_screenshot is None:
                height, width = shared_curr_screenshot.shape[0], shared_curr_screenshot.shape[1]
                self.draw(
                    0, 0, width, height, shared_curr_screenshot
                )

                # input('INIT: ')
                return

            height, width = shared_curr_screenshot.shape[0], shared_curr_screenshot.shape[1]
            #print("X", height, width)
            x_chunks = math.ceil(width / self.chunk_length)
            y_chunks = math.ceil(height / self.chunk_length)
            pairs = itertools.product(
                range(x_chunks), range(y_chunks)
            )

            for x_chunk, y_chunk in pairs:
                #print('CHUNK', x_chunk, y_chunk)
                result = self.get_sub_chunk(
                    x_chunk, y_chunk
                )

                if result is None:
                    #print("hi")
                    continue
                else:
                    print("hoyo")
                chunk, sub_chunk = result
                print(result)
                diff = self.chunk_length - chunk.shape[1]

                self.draw(
                    self.screen_width - self.chunk_length * (x_chunk + 1) + diff,
                    self.chunk_length * (y_chunk),
                    chunk.shape[1],
                    chunk.shape[0],
                    np.array(sub_chunk)
                )
            # input('PAUSE: ')

    def run(self, images=None):
        print("run")
        index = 0
        height, width = 0, 0

        # shared_mod_screenshot = mp.Array(np.uint8, self.screen_width*self.screen_height)
        screenshot_process = mp.Process(target=self.take_screenshot)
        screenshot_process.start()
        update_process = mp.Process(target=self.constant_update)
        update_process.start()
        while True:
            pass
        
        


"""
    def zyFunc():
        rowHasSomething = False
        xMin = diff.width
        yMin = diff.height
        xMax = yMax = 0
        boundingBoxArray = []
        countSince = 0
        for y in range(diff.height):
            rowHasSomething = False
            for x in range(diff.width):
                currPixel = diff.getpixel((x,y))
                if currPixel != (0,0,0):
                    rowHasSomething = True
                    countSince = 0
                if rowHasSomething:
                    if currPixel != (0,0,0):
                        if xMin > x:
                            xMin = x
                        if xMax < x:
                            xMax = x
                        if yMin > y:
                            yMin = y
                        if yMax < y:
                            yMax = y
            if rowHasSomething:
                if currPixel != (0,0,0):
                    if yMin > y:
                        yMin = y
                    if yMax < y:
                        yMax = y
            else:
                countSince += 1
                if countSince == 1:
                    boundingBoxArray.append(BoundingBox(xMin, yMin, xMax-xMin, yMax-yMin))
                    yMin = diff.height
                    xMin = diff.width
                    yMax = xMax = 0
                else:
                    pass
"""
            

if __name__ == '__main__':
    updater = Updater()
    updater.run()
    