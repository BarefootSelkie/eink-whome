#!/usr/bin/env python3
# This is for testing without a raspberry pi or eink display, it will create and image and open it in preview

import time
import requests
import logging
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
bigFont = ImageFont.truetype("./LeagueSpartan-Medium.ttf", int(44))
smallFont = ImageFont.truetype("./LeagueSpartan-Medium.ttf", int(24))

# Create a varible that holds what will be drawn onto the screen
img  = Image.new( mode = "P", size = inky_display.resolution )

# Create a varible that allows access to the drawing functions
draw = ImageDraw.Draw(img)

# Create and image to draw on the scren
def drawScreen():
    # Draw a white background on the display
    draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)

    # Check if we are in the situation where no-one is switched in at all
    if len(pktools.lastSwitch["members"]) == 0:
        # TODO: show something if no-one is switched in
        return(img)

    # Get the first member in the last switch
    firstFront = pktools.getMember(pktools.lastSwitch["members"][0])
    
    # Draw text on the display
    draw.text((inky_display.resolution[0] / 2, 32), firstFront["name"], inky_display.BLACK, font=bigFont, anchor="mm")
    if firstFront["pronouns"] is not None:
        draw.text((8, 86), firstFront["pronouns"], inky_display.BLACK, font=smallFont, anchor="lm")

    # if member is in the flagGroup draw the flag
    if firstFront["uuid"] in flagGroup["members"]:
        draw.text((inky_display.resolution[0] - 8, 86), "ty", inky_display.RED, font=smallFont, anchor="rm")

    # Rotate the image as the pi has power cables comming out the usb ports so is mounted gpio connector down
    return(img.rotate(180))

# Send a message to discord saying who's fronting
def sendMessage(messageText):
    logging.info("Sending Discord message")
    message = {"content": messageText}
    try:
        requests.post("https://discord.com/api/webhooks/" + pktools.pktsettings["discord"]["serverID"] + "/" + pktools.pktsettings["discord"]["token"], message)
    except requests.exceptions.RequestException as e:
        logging.warning("Unable to send message to discord")
        logging.warning(e) 

# Checkthe data is up to date on first run
pktools.pullPeriodic()
inky_display.set_image(drawScreen())
inky_display.show()

### Main code loop ###
minutePast = 0

while True:
    # Don't do anyting if the minute hasn't changed
    if minutePast != time.localtime()[4]:
        minutePast = time.localtime()[4]

        # If the minute is divisable by five check for new fronters
        # this is for rate limiting and not hitting the pluralkit api too hard
        if ( time.localtime()[4] % 1 ) == 0:
            updateNeeded = pktools.pullPeriodic()

            # If pullPeriodic returns true update the screen and unset updateNeeded
            if updateNeeded:
                inky_display.set_image(drawScreen())
                inky_display.show()
                for id in pktools.lastSwitch["members"]:
                    member = pktools.getMember(id)
                    sendMessage("Hi, " + member["name"] + "\n" + 
                                "You last fronted: " + str(pktools.rsLastSeen(id)) + " ago \n" + 
                                "Headspace time: " + str(pktools.hsTimeShort(pktools.hsLastSeen(id))))
                updateNeeded = False

    # do nothing for a while
    time.sleep(5)