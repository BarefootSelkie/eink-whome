#!/usr/bin/env python3

import time
import yaml
import requests
import logging
from PIL import Image, ImageFont, ImageDraw
from pktools import pktools
from inky.auto import auto

# Logging setup
logging.basicConfig(format="%(asctime)s : %(message)s", filename="./log-eink-whome.log", encoding='utf-8', level=logging.WARN)

# Load settings
try:
    with open("./config-eink-whome.yaml", "r") as read_file:
        config = yaml.safe_load(read_file)
except:
    logging.critical("Settings file missing")
    exit()

# Check that the library is up to date enough
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

# Set the fonts and sizes
bigFont = ImageFont.truetype("./LeagueSpartan-Medium.ttf", int(44))
smallFont = ImageFont.truetype("./LeagueSpartan-Medium.ttf", int(24))
symbolFont = ImageFont.truetype("./NotoSansSymbols2-Regular.ttf", int(24))

# Create a variable that holds what will be drawn onto the screen
img  = Image.new( mode = "P", size = inky_display.resolution )

# Create a variable that allows access to the drawing functions
draw = ImageDraw.Draw(img)

state = { "lastSwitch": {"timestamp": "" }}

# Returns the member that should be displayed on the display
def getFronter():
    global state
    if len(state["lastSwitch"]["members"]) == 0:
        return None
    id = state["lastSwitch"]["members"][0]
    member, private = pktools.getMember(id, state["pkMembers"])
    if private:
        member, private = pktools.getMember("ogymz", state["pkMembers"])
    return member

def fetchState():
    global state
    logging.info("( fetchState )")
    try:
        serverUrl = "http://" + str(config["server"]) + ":" + str(config["port"])
        lastSwitch = requests.get(serverUrl + "/lastSwitch.json").json()
        if state["lastSwitch"]["timestamp"] != lastSwitch["timestamp"]:
            state["pkMembers"] = requests.get(serverUrl + "/pkMembers.json").json()
            state["memberList"] = requests.get(serverUrl + "/memberList.json").json()
            state["lastSwitch"] = lastSwitch
            return True
    except Exception as e:
        logging.warning("( fetchState )")
        logging.warning(e)
    return False


# Create and image to draw on the screen
def drawScreen(fronter):
    # Draw a white background on the display
    draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)
    
    if fronter is not None:    
        # Draw text on the display
        draw.text((inky_display.resolution[0] / 2, 32), fronter["name"], inky_display.BLACK, font=bigFont, anchor="mm")
        if fronter["pronouns"] is not None:
            draw.text((8, 86), fronter["pronouns"], inky_display.BLACK, font=smallFont, anchor="lm")

        # Draw the card suit if one exists
        for member in state["memberList"]:
            if member["memberId"] == fronter["id"]:
                draw.text((inky_display.resolution[0] - 8, 86), member["cardsName"], inky_display.RED, font=symbolFont, anchor="rm")

    # Rotate the image as the pi has power cables coming out the usb ports so is mounted gpio connector down
    return(img.rotate(180))


# Check the data is up to date on first run
fetchState()
inky_display.set_image(drawScreen(getFronter()))
inky_display.show()

### Main code loop ###
minutePast = 0

while True:
    # Don't do anything if the minute hasn't changed
    if minutePast != time.localtime()[4]:
        minutePast = time.localtime()[4]

        # If the minute is divisible by updateInterval check for new fronters
        # this is for rate limiting and not hitting the pluralkit api too hard
        updateInterval = 1
        if ( time.localtime()[4] % updateInterval ) == 0:
            updateNeeded = fetchState()

            # If pullPeriodic returns true update the screen and unset updateNeeded
            if updateNeeded:
                inky_display.set_image(drawScreen(getFronter()))
                inky_display.show()
                updateNeeded = False

    # do nothing for a while
    time.sleep(5)
