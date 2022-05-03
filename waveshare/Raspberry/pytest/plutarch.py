import os
import matplotlib.pyplot as plt

from Updater import Updater
from datetime import datetime
from PIL import Image, ImageOps

updater = Updater()
updater.screen_width = 1872
updater.screen_height = 1404

basedir = 'readings/plutarch_lives'
filenames = [
    f for f in os.listdir(basedir) 
    if os.path.isfile(os.path.join(basedir, f))
]

length = len(filenames)
filenames = sorted(filenames)
index = 0

while index < length:
    filename = filenames[index]
    path = os.path.join(basedir, filename)

    image = Image.open(path)
    image = image.transpose(Image.ROTATE_90)
    print('WH', image.width, image.height)
    # plt.imshow(image)
    # plt.show()

    arr = updater.rescale(image)
    updater.show_depth_image(arr)

    entry = None
    while entry not in ('p', ''):
        entry = input(f'{index}/{length}: ')
        entry = entry.strip()

    if entry == '':
        index += 1
    elif index > 0:
        index -= 1
