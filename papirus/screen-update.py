import os

os.environ['DISPLAY'] = ':0'

import time
import PIL
import pyautogui 

from papirus import Papirus


# The epaper screen object.
# Optional rotation argument: rot = 0, 90, 180 or 270 degrees
screen = Papirus()
screen.clear()

# image = PIL.Image.open('screenshot.png')
# resized_image = image.resize(screen.size)

# Disable automatic use of LM75B temperature sensor
screen.use_lm75b = False

while True:
    # image = PIL.Image.open('screenshot.png')
    image = pyautogui.screenshot()
    resized_image = image.resize(screen.size)
    screen.display(resized_image)
    screen.partial_update()
    # time.sleep(0.1)


