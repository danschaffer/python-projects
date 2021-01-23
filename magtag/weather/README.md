# magtag/weather

## Overview
Project for displaying the weather on a magtag iot device
https://www.adafruit.com/product/4819

The magtag is a really neat device.  If buying the device from adafruit make sure to get the kit with the magnets. 
When hooked up with magnets and lipo battery you can write circuitpython code to update the eink display once per day then go back to sleep.  When fully charged you can then put the device on your refridgerator and it will update over
wifi once per day and not need to be charged for about a month.

## Steps

* Get the magtag from adafruit,  the kit costs about $40 but provides lots of entertainment
* follow this tutorial https://learn.adafruit.com/magtag-weather
* I modified the project to include the National Food of the Day each day since I know where I am and don't need to display my city
* I created secrets.py.template,  copy it to secrets.py and fill out with your wifi info and open weather info
* copy magtag_weather.py to code.py, copy it when connecting the device over usb to CIRCUIT_PYTHON device, make sure to copy all of the libraries required as described in the tutorial instructions
