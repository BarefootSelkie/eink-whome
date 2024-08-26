# eink whome
a script to display who is currently fronting on an eink display attached to a raspberry pi zero

This is for the older screen size of 212 x 104

screen is divided up into a top section of 64 px that will display the name, a 4px spacer, and the 36px area that will display pronouns and group

## Setup

**Currently won't run on versions of Raspbian higher than Bulleye, as there is no software for the Inky for Bookworm**

- Install the software for the inky, as described on [Pimoroni's Inky Page](https://learn.pimoroni.com/article/getting-started-with-inky-phat)
- Clone repo `git clone https://github.com/BarefootSelkie/eink-whome.git`
- Initialise the submodule `git submodule init`
- Update the submodule `git submodule update`
- Rename the config file `mv config-eink-whome-example.yaml config-eink-whome.yaml`
- Get yaml and requests `pip install pyyaml requests`
- If there server is not local update the ip address and port to point at correct server location
- Download the font `wget https://github.com/theleagueof/league-spartan/raw/master/fonts/ttf/LeagueSpartan-Medium.ttf`