from papirus import Papirus
import PIL

# The epaper screen object.
# Optional rotation argument: rot = 0, 90, 180 or 270 degrees
screen = Papirus()

image = PIL.Image.open('screenshot.png')
resized_image = image.resize(screen.size)

# Write a bitmap to the epaper screen
screen.display(resized_image)

# Perform a full update to the screen (slower)
screen.update()

# Update only the changed pixels (faster)
screen.partial_update()

# Update only the changed pixels with user defined update duration
screen.fast_update()

# Disable automatic use of LM75B temperature sensor
screen.use_lm75b = False
