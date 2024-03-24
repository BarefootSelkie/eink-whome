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

# Checks if a system member is publicly visible and if not returns the default member
def testPrivacy(id):
    if pktools.getMember(id)["privacy"]["visibility"] == "private":
        return pktools.pktsettings["defaultFronter"]
    else: 
        return id

# Returns the member that should be displayed on the display
def getFronter():
    if len(pktools.lastSwitch["members"]) > 0:
        return pktools.getMember(testPrivacy(pktools.lastSwitch["members"][0]))
    else:
        return pktools.getMember(pktools.pktsettings["defaultFronter"])

# Create and image to draw on the scren
def drawScreen(fronter):
    # Draw a white background on the display
    draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)
    
    # Draw text on the display
    draw.text((inky_display.resolution[0] / 2, 32), fronter["name"], inky_display.BLACK, font=bigFont, anchor="mm")
    if fronter["pronouns"] is not None:
        draw.text((8, 86), fronter["pronouns"], inky_display.BLACK, font=smallFont, anchor="lm")

    # if member is in the flagGroup draw the flag
    if fronter["uuid"] in flagGroup["members"]:
        draw.text((inky_display.resolution[0] - 8, 86), "ty", inky_display.RED, font=smallFont, anchor="rm")

    # Rotate the image as the pi has power cables comming out the usb ports so is mounted gpio connector down
    return(img.rotate(180))

# Send a message to discord saying who's fronting
def sendMessage(messageText, mode):
    logging.info("Sending Discord message")
    message = {"content": messageText}
    try:
        requests.post("https://discord.com/api/webhooks/" + pktools.pktsettings["discord"][mode]["serverID"] + "/" + pktools.pktsettings["discord"][mode]["token"], message)
    except requests.exceptions.RequestException as e:
        logging.warning("Unable to send message to discord")
        logging.warning(e) 

# Checkthe data is up to date on first run
pktools.pullPeriodic()
inky_display.set_image(drawScreen(getFronter()))
inky_display.show()

### Main code loop ###
minutePast = 0

while True:
    # Don't do anyting if the minute hasn't changed
    if minutePast != time.localtime()[4]:
        minutePast = time.localtime()[4]

        # If the minute is divisable by updateInterval check for new fronters
        # this is for rate limiting and not hitting the pluralkit api too hard
        updateInterval = 5
        if ( time.localtime()[4] % updateInterval ) == 0:
            updateNeeded = pktools.pullPeriodic()

            # If pullPeriodic returns true update the screen and unset updateNeeded
            if updateNeeded:
                inky_display.set_image(drawScreen(getFronter()))
                inky_display.show()
                
                # Check if not switched out
                if len(pktools.lastSwitch["members"]) > 0:

                    # Build and send full message
                    if pktools.pktsettings["discord"]["full"]["enabled"]:
                        for id in pktools.lastSwitch["members"]:
                            member = pktools.getMember(id)
                            sendMessage("Hi, " + member["name"] + "\n" + 
                                        "You last fronted: " + "\n" +
                                        str(pktools.rsLastSeen(id))[:-10] + " ago\n" + 
                                        str(pktools.hsTimeShort(pktools.hsLastSeen(id))) + "\n---", "full")
                    
                    # Build and send filtered message
                    if pktools.pktsettings["discord"]["filtered"]["enabled"]:
                        message = "Hi, "
                        for id in pktools.lastSwitch["members"]:
                            member = pktools.getMember(testPrivacy(id))
                            message = message + member["name"] + " ( " + member["pronouns"] + " ), "
                        sendMessage(message, "filtered")
                        
                updateNeeded = False

    # do nothing for a while
    time.sleep(5)