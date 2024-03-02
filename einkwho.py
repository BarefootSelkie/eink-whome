#!/usr/bin/env python3
# This is for testing without a raspberry pi or eink display, it will create and image and open it in preview

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from pktools import pktools
from inky.auto import auto

# Check that the libary is up to date enough
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

# GroupID of the group that displays a flag in the bottom right of the screen
flagGroupId = "syuzl"
flagGroup = [i for i in pktools.pkGroups if i["id"] == flagGroupId][0]

# Set the fonts and sizes
bigFont = ImageFont.truetype(HankenGroteskBold, int(44))
smallFont = ImageFont.truetype(HankenGroteskBold, int(24))

# Create a varible that holds what will be drawn onto the screen
img  = Image.new( mode = "P", size = inky_display.resolution )

# Create a varible that allows access to the drawing functions
draw = ImageDraw.Draw(img)

# Checkthe data is up to date
pktools.pullPeriodic()

# Get the first member in the last switch
firstFront = pktools.getMember(pktools.lastSwitch["members"][0])

# Draw a white background on the display
draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)

# Draw text on the display
draw.text((inky_display.resolution[0] / 2, 32), firstFront["name"], inky_display.BLACK, font=bigFont, anchor="mm")
draw.text((8, 86), firstFront["pronouns"], inky_display.BLACK, font=smallFont, anchor="lm")

if firstFront["uuid"] in flagGroup["members"]:
    draw.text((inky_display.resolution[0] - 8, 86), "ty", inky_display.RED, font=smallFont, anchor="rm")

inky_display.set_image(img)
inky_display.show()
