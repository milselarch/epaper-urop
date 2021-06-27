
from papirus import PapirusText
from papirus import PapirusTextPos
import time

text = PapirusTextPos()
text.Clear()

text.AddText("Test", 10, 10, Id="Start")
text.partialUpdates = True

# Write text to the screen
# text.write(text)
message = "hello world this is a test to see how fast the screen is"
for k in range(len(message)):
    text.UpdateText("Start", message[:k])
    # text.partial_update()
    time.sleep(0.5)

