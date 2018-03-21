# OctoPrintControlPad
Code used to implement a physical control pad under development for OctoPrint

# Prerequsites
* Raspberry Pi 2 or 3
* OctoPrint 3.x or higher
* OctoPrint [Enclosure plugin](https://plugins.octoprint.org/plugins/enclosure/)

# Supported 3D printers
Currently, this project has only been tested with a Delta Go 3D printer, and containts optional functions specific to the Delta Go.

# GPIO Assignments
listen-for-octoprint.py

GPIO | Device   | Primary Function          | Alt. Function (Button Long-Press)
---- | -------- | ------------------------- | -------------
5    | Relay 1  | Printer Power             | 
6    | Relay 2  | Fan Power                 | 
12   | Speaker  | System Speaker            | 
9    | LED 0    | Printer Power             | 
24   | LED 1    | Printer Connection        | 
22   | LED 2    | Pause/Resume              | 
25   | Button 0 | Printer Power             | Fan Power
4    | Button 1 | Home / Cancel / Reconnect | Printer Calibration Routine
23   | Button 2 | Heat / Cool               | LED Lighting Selection
17   | Button 3 | Extrude                   | Forced Extrude (Ignore hotend temperature)
27   | Button 4 | Pause / Resume            | 

listen-for-shutdown.py

GPIO | Device   | Primary Function
---- | -------- | ----------------
12   | Speaker  | System Speaker
3    | Button 0 | Pi Power

Note: GPIO Mode is BCM. GPIO warnings are disabled (multiple processess will access the same GPIOs, by design)
