#!/usr/bin/env python3

import time
import yaml
import requests
import logging
import argparse
from PIL import Image, ImageFont, ImageDraw
from pktools import pktools
from inky.auto import auto

# Arguments and logging
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
args = parser.parse_args()

if args.verbose:
  logging.basicConfig(format="%(asctime)s : %(message)s", filename="log-eink-whome.log", encoding='utf-8', level=logging.DEBUG)
else:
  logging.basicConfig(format="%(asctime)s : %(message)s", filename="log-eink-whome.log", encoding='utf-8', level=logging.WARN)

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
symbolFont = ImageFont.truetype("./NotoSansSymbols2-Regular.ttf", int(32))

# Create a variable that holds what will be drawn onto the screen
img  = Image.new( mode = "P", size = inky_display.resolution )

# Create a variable that allows access to the drawing functions
draw = ImageDraw.Draw(img)

state = { "lastSwitch": {"timestamp": "" }}

# Returns the member that should be displayed on the display
def getFirstFronter(currentFronters):
  displayText = {}

  if len(currentFronters["members"]) == 0:
    displayText["name"] = str(config["outMessage"])
  else:
    firstFronter = currentFronters["members"][0]
    
    if firstFronter["visible"]:
      displayText["name"] = firstFronter["name"]
      if firstFronter["pronouns"] is not None:
        displayText["pronouns"] = firstFronter["pronouns"]
    else:
      displayText["name"] = currentFronters["system"]["name"]
      if currentFronters["system"]["pronouns"] is not None:
        displayText["pronouns"] = currentFronters["system"]["pronouns"]
        
    if firstFronter["cardSuit"] is not None:
      displayText["cardSuit"] = firstFronter["cardSuit"]
  
  return displayText

def checkFronters(storedFronters):
  try:
    serverUrl = "http://" + str(config["server"]) + ":" + str(config["port"])
    currentFronters = requests.get(serverUrl + "/currentFronters.json").json()  
  except Exception as e:
    logging.warning("Cannot fetch current front ( checkFronters() )")
    logging.warning(e)
  
  if storedFronters is None or currentFronters["switch"]["timestamp"] != storedFronters["switch"]["timestamp"]:
    return True, currentFronters
  else:
    return False, storedFronters

# Create and image to draw on the screen
def drawScreen(displayText):
  # Draw a white background on the display
  draw.rectangle(((0, 0), inky_display.resolution), inky_display.WHITE, None, 0)
  
  draw.text((inky_display.resolution[0] / 2, 32), displayText["name"], inky_display.BLACK, font=bigFont, anchor="mm")

  if displayText["pronouns"] is not None:
    draw.text((8, 86), displayText["pronouns"], inky_display.BLACK, font=smallFont, anchor="lm")

  # Draw the card suit if one exists
  if displayText["cardSuit"] is not None:
    cardSuit = displayText["cardSuit"][:1]
    if cardSuit in ["♠", "♣"]:
      cardColour = inky_display.BLACK
    else:
      cardColour = inky_display.RED

    draw.text((inky_display.resolution[0] - 6, 92), cardSuit, cardColour, font=symbolFont, anchor="rm")

  # Rotate the image as the pi has power cables coming out the usb ports so is mounted gpio connector down
  return(img.rotate(180))

### Main Code ###

# Make a blank storedFronters object and then check the server for the up to date infomation
storedFronters = {}
updateNeeded, storedFronters = checkFronters(storedFronters)

inky_display.set_image(drawScreen(getFirstFronter(storedFronters)))
inky_display.show()

### Main Loop ###
minutePast = 0

while True:
  # Don't do anything if the minute hasn't changed
  if minutePast != time.localtime()[4]:
    minutePast = time.localtime()[4]

    # If the minute is divisible by updateInterval check for new fronters
    # this is for rate limiting and not hitting the pluralkit api too hard
   
    if ( time.localtime()[4] % config["updateInterval"] ) == 0:
      updateNeeded, currentFronters = checkFronters(storedFronters)

      # If checkFronters returns true update the screen and unset updateNeeded
      if updateNeeded:
        inky_display.set_image(drawScreen(getFirstFronter(currentFronters)))
        inky_display.show()
        storedFronters = currentFronters

  # do nothing for a while
  time.sleep(5)
