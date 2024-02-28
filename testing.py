#!/usr/bin/env python3

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from inky.auto import auto

# Check that the libary is up to date enough
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

# Set the fonts and sizes
bigFont = ImageFont.truetype(HankenGroteskBold, int(44))
smallFont = ImageFont.truetype(HankenGroteskBold, int(24))

# Create a varible that holds what will be drawn onto the screen
img  = Image.new( mode = "P", size = inky_display.resolution )

# Create a varible that allows access to the drawing functions
draw = ImageDraw.Draw(img)

# Draw a white background on the display
draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)

# Draw text on the display
draw.text((inky_display.width / 2, 32), "Test namey", inky_display.BLACK, font=bigFont, anchor="mm")
draw.text((8, 86), "she/it", inky_display.BLACK, font=smallFont, anchor="lm")
draw.text((inky_display.width-8, 86), "tiny", inky_display.RED, font=smallFont, anchor="rm")

inky_display.set_image(img)
inky_display.show()
