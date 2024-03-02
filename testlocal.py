#!/usr/bin/env python3
# This is for testing without a raspberry pi or eink display, it will create and image and open it in preview

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from pktools import pktools

# GroupID of the group that displays a flag in the bottom right of the screen
flagGroupId = "syuzl"
flagGroup = [i for i in pktools.pkGroups if i["id"] == flagGroupId][0]

# Set the fonts and sizes
bigFont = ImageFont.truetype(HankenGroteskBold, int(44))
smallFont = ImageFont.truetype(HankenGroteskBold, int(24))

# Create a dummy screen matching the eink display
resolution = (212, 104)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Create a varible that holds what will be drawn onto the screen
img  = Image.new( mode = "RGB", size = resolution )

# Create a varible that allows access to the drawing functions
draw = ImageDraw.Draw(img)

# Checkthe data is up to date
pktools.pullPeriodic()

# Get the first member in the last switch
firstFront = pktools.getMember(pktools.lastSwitch["members"][0])

# Draw a white background on the display
draw.rectangle(((0, 0), resolution), WHITE, None, 0)

# Draw text on the display
draw.text((resolution[0] / 2, 32), firstFront["name"], BLACK, font=bigFont, anchor="mm")
draw.text((8, 86), firstFront["pronouns"], BLACK, font=smallFont, anchor="lm")

if firstFront["uuid"] in flagGroup["members"]:
    draw.text((resolution[0] - 8, 86), "ty", RED, font=smallFont, anchor="rm")

img.show()

#inky_display.set_image(img)
#inky_display.show()
