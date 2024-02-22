#!/usr/bin/env python3

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from inky.auto import auto

# vertical layout: 64 + 4 + 36

try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

bigFont = ImageFont.truetype(HankenGroteskBold, int(44))
smallFont = ImageFont.truetype(HankenGroteskBold, int(24))

img  = Image.new( mode = "P", size = inky_display.resolution )

draw = ImageDraw.Draw(img)

draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)

draw.text((inky_display.width / 2, 32), "Test namey", inky_display.BLACK, font=bigFont, anchor="mm")
draw.text((8, 86), "she/it", inky_display.BLACK, font=smallFont, anchor="lm")
draw.text((inky_display.width-8, 86), "tiny", inky_display.RED, font=smallFont, anchor="rm")

inky_display.set_image(img)
inky_display.show()
