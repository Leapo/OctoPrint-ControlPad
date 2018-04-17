#!/usr/bin/env python

import RPi.GPIO as GPIO
import subprocess
import os
import json
import yaml
from multiprocessing import Process
from time import sleep
import sys

# User Vars
var_conf_warmup_target = 200 # Target temperature when warming-up the hotend (Degrees C)
var_conf_shutdown_auto = 1   # Enable (1) or Disable (0) automatic printer shutdown
var_conf_shutdown_time = 12  # Automatic printer shutdown delay time (Seconds)

# Assign GPIOs
var_gpio_rly1 = 5            # Relay 1   Printer Power
var_gpio_rly2 = 6            # Relay 2   Fan Power
var_gpio_spk1 = 12           # Speaker   System Speaker
var_gpio_led0 = 9            # LED 0     Printer Power
var_gpio_led1 = 24           # LED 1     Printer Connection
var_gpio_led2 = 22           # LED 2     Pause/Resume
var_gpio_btn0 = 25           # Button 0  Printer Power
var_gpio_btn1 = 4            # Button 1  Home / Cancel / Reconnect
var_gpio_btn2 = 23           # Button 2  Heat / Cool
var_gpio_btn3 = 17           # Button 3  Extrude
var_gpio_btn4 = 27           # Button 4  Pause / Resume
var_gpio_sen0 = 21           # Sensor 0  Filament Sensor

# Setup GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(var_gpio_rly1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(var_gpio_rly2, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(var_gpio_spk1, GPIO.OUT)
GPIO.setup(var_gpio_led1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(var_gpio_led2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(var_gpio_led0, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(var_gpio_btn0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(var_gpio_btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(var_gpio_btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(var_gpio_btn3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(var_gpio_btn4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(var_gpio_sen0, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Get OctoPrint API Key
with open("/home/pi/.octoprint/config.yaml") as stream:
    var_yaml_string = yaml.load(stream)
    var_api_key = str(var_yaml_string['api']['key'])
    print("OctoPrint API Key: {}").format(var_api_key)

# Define Beep Codes
def pwm_beep(var_gpio, var_hz, var_sustain, var_pause, var_dutycycle=50):
    p = GPIO.PWM(var_gpio, var_hz)
    p.start(var_dutycycle)
    sleep(var_sustain)
    p.stop()
    sleep(var_pause)

def beep(var_beeptype='beep'):
    if var_beeptype == 'beep':
        pwm_beep(var_gpio_spk1, 400, 0.07, 0)     #GPIO, Hz, Sustain, Pause, Duty Cycle
    elif var_beeptype == 'up':
        pwm_beep(var_gpio_spk1, 200, 0.07, 0.05)  #GPIO, Hz, Sustain, Pause, Duty Cycle
        pwm_beep(var_gpio_spk1, 460, 0.08, 0)     #GPIO, Hz, Sustain, Pause, Duty Cycle
    elif var_beeptype == 'down':
        pwm_beep(var_gpio_spk1, 460, 0.07, 0.05)  #GPIO, Hz, Sustain, Pause, Duty Cycle
        pwm_beep(var_gpio_spk1, 180, 0.08, 0)     #GPIO, Hz, Sustain, Pause, Duty Cycle
    elif var_beeptype == 'error':
        pwm_beep(var_gpio_spk1, 80, 0.09, 0.05)   #GPIO, Hz, Sustain, Pause, Duty Cycle
        pwm_beep(var_gpio_spk1, 50, 0.09, 0)      #GPIO, Hz, Sustain, Pause, Duty Cycle
    else:
        print("{} is not a valid beep type. Please use one of the following: beep, up, down, error").format(var_beeptype)

# OctoPrint REST API Pull function
def printer_pull(var_command, var_input1='none'):
    if var_command == 'state':
        for _ in range(3):
            try:
                var_json_string = os.popen (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X GET http://127.0.0.1/api/connection').format(var_api_key)).read()
                var_json_parsed = json.loads(var_json_string)
                var_state = str(var_json_parsed['current']['state'])
                if (var_input1 == 'basic') or (var_input1 == 'none'):
                    if (var_state == 'Operational') or (var_state == 'Printing') or (var_state == 'Paused'):
                        return 'Connected'
                    else:
                        return 'Disconnected'
                elif var_input1 == 'detailed':
                    if (var_state != 'Operational') and (var_state != 'Printing') and (var_state != 'Paused'):
                        return 'Disconnected'
                    else:
                        return var_state
                elif var_input1 == 'raw':
                    return var_state
                else:
                    print("{} is not a valid verbosity. Please use one of the following: basic, detailed, raw").format(var_input1)
                    return 'Error'
            except:
                sleep(0.5)
        return 'Error'
    elif var_command == 'target':
        for _ in range(3):
            try:
                var_json_string = os.popen (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X GET http://127.0.0.1/api/printer/tool').format(var_api_key)).read()
                var_json_parsed = json.loads(var_json_string)
                var_target = str(var_json_parsed['tool0']['target'])
                return var_target
            except:
               sleep(0.5)
        return 'Error'
    elif var_command == 'job':
        for _ in range(3):
            try:
                var_json_string = os.popen (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X GET http://127.0.0.1/api/job').format(var_api_key)).read()
                var_json_parsed = json.loads(var_json_string)
                var_jobstatus = str(var_json_parsed['state'])
                return var_jobstatus
            except:
                sleep(0.5)
        return 'Error'
    else:
        print("{} is not a valid command. Please use one of the following: connection, target, job").format(var_command)

# OctoPrint REST API Push function
def printer_push(var_command, var_input1='none', var_input2='none', var_input3='none'):
    if var_command == 'connect':
        for _ in range(16):
            os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"connect" }}\' http://127.0.0.1/api/connection').format(var_api_key))
            sleep(0.55)
            var_state = printer_pull('state')
            if var_state == 'Connected':
                GPIO.output(var_gpio_led1, GPIO.HIGH)
                break
            else:
                GPIO.output(var_gpio_led1, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(var_gpio_led1, GPIO.LOW)
    elif var_command == 'disconnect':
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"disconnect" }}\' http://127.0.0.1/api/connection').format(var_api_key))
    elif var_command == 'cancel':
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"cancel" }}\' http://127.0.0.1/api/job').format(var_api_key))
    elif var_command == 'home':
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"target", "targets": {{ "tool0":0.0 }} }}\' http://127.0.0.1/api/printer/tool').format(var_api_key))
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"home", "axes":"xyz" }}\' http://127.0.0.1/api/printer/printhead').format(var_api_key))
    elif var_command == 'pause':
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X POST -d \'{{ "command":"pause","action":"pause" }}\' http://127.0.0.1/api/job').format(var_api_key))
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X POST -d \'{{ "command":"jog","absolute":1,"x":0,"y":-60 }}\' http://127.0.0.1/api/printer/printhead').format(var_api_key))
    elif var_command == 'resume':
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X POST -d \'{{ "command":"pause","action":"resume" }}\' http://127.0.0.1/api/job').format(var_api_key))
    elif var_command == 'calibrate':
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X POST -d \'{{ "command":"play /sd/factory_setup.gcode" }}\' http://127.0.0.1/api/printer/command').format(var_api_key))
    elif var_command == 'temp':
        if var_input1 != 'none':
            os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"target", "targets": {{ "tool0":{1} }} }}\' http://127.0.0.1/api/printer/tool').format(var_api_key, var_input1))
    elif (var_command == 'extrude') and (var_input1 != 'none'):
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"extrude", "amount":{1} }}\' http://127.0.0.1/api/printer/tool').format(var_api_key, var_input1))
    elif (var_command == 'rgb') and (var_input1 != 'none') and (var_input2 != 'none') and (var_input3 != 'none'):
        os.system (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {0}" -X POST -d \'{{ "command":"M150 R{1} U{2} B{3}" }}\' http://127.0.0.1/api/printer/command').format(var_api_key, var_input1, var_input2, var_input3))
    else:
        print("{} is not a valid command. Please use one of the following: connect, disconnect, cancel, home, temp, extrude, rgb").format(var_command)

# Wait for OctoPrint to load
def conwait():
    print("Connecting to OctoPrint...")
    while True:
        GPIO.output(var_gpio_led0, GPIO.HIGH)
        try:
            var_json_string = os.popen (('curl -s -H "Content-Type: application/json" -H "X-Api-Key: {}" -X GET http://127.0.0.1/api/connection').format(var_api_key)).read()
            var_json_parsed = json.loads(var_json_string)
            var_state = str(var_json_parsed['current']['state'])
        except:
            var_state = 'none'
        if (var_state == 'Closed') or (var_state == 'Operational') or ('Failed' in var_state):
            print("Connection established")
            sleep(0.2)
            GPIO.output(var_gpio_led1, GPIO.HIGH)
            sleep(0.5)
            beep('up')
            sleep(0.2)
            GPIO.output(var_gpio_led1, GPIO.LOW)
            GPIO.output(var_gpio_led0, GPIO.LOW)
            return
        else:
            sleep(0.2)
            GPIO.output(var_gpio_led0, GPIO.LOW)
            sleep(0.15)

# Monitoring Process
def loop_monitor():
    var_state = 'none'
    var_state_previous = 'none'
    output_value = 'none'
    output_value_previous = GPIO.input(var_gpio_rly1)

    while True:
        # LED 0 - Printer Power Status
        output_value = GPIO.input(var_gpio_rly1)
        if output_value != output_value_previous:
            if output_value == False:
                GPIO.output(var_gpio_led0, GPIO.HIGH)
                beep()
                print("Monitor, GPIO {1}, Relay 1 (GPIO {0}) ON").format(var_gpio_rly1, var_gpio_led0)
                var_state_previous = 'none'
            else:
                GPIO.output(var_gpio_led0, GPIO.LOW)
                GPIO.output(var_gpio_led1, GPIO.LOW)
                GPIO.output(var_gpio_led2, GPIO.LOW)
                beep('down')
                print("Monitor, GPIO {1}, Relay 1 (GPIO {0}) OFF").format(var_gpio_rly1, var_gpio_led0)
        output_value_previous = output_value

        # LED 1 - Printer Connection Status
        # LED 2 - Paused Status
        if output_value == False:
            var_state = printer_pull('state', 'detailed')
            if var_state != var_state_previous:
                if (var_state == 'Operational') and (var_state_previous in ('Printing', 'Paused')) and (var_conf_shutdown_auto == 1):
                    GPIO.output(var_gpio_led1, GPIO.HIGH)
                    GPIO.output(var_gpio_led2, GPIO.LOW)
                    beep('up')
                    sleep(0.5)
                    print("Monitor, GPIO {0}, Print completed or canceled. Automated shutdown initiated, {1} second delay...").format(var_gpio_led1, var_conf_shutdown_time)
                    printer_push('temp', 0.0)
                    printer_push('disconnect')
                    var_state_previous = 'Disconnected'
                    for _ in range(var_conf_shutdown_time):
                        GPIO.output(var_gpio_led1, GPIO.LOW)
                        beep()
                        sleep(0.5)
                        GPIO.output(var_gpio_led1, GPIO.HIGH)
                        sleep(0.5)
                    GPIO.output(var_gpio_led1, GPIO.LOW)
                    beep()
                    sleep(0.25)
                    GPIO.output(var_gpio_rly1, GPIO.HIGH)
                    GPIO.output(var_gpio_rly2, GPIO.HIGH)
                    sleep(0.25)
                elif (var_state == 'Operational'):
                    GPIO.output(var_gpio_led1, GPIO.HIGH)
                    GPIO.output(var_gpio_led2, GPIO.LOW)
                    beep('up')
                    print("Monitor, GPIO {}, Printer connected to OctoPrint").format(var_gpio_led1)

                if (var_state == 'Paused'):
                    GPIO.output(var_gpio_led1, GPIO.HIGH)
                    GPIO.output(var_gpio_led2, GPIO.HIGH)
                    beep('down')
                    print("Monitor, GPIO {}, Paused print").format(var_gpio_led2)

                if (var_state == 'Printing') and (var_state_previous == 'Paused'):
                    GPIO.output(var_gpio_led1, GPIO.HIGH)
                    GPIO.output(var_gpio_led2, GPIO.LOW)
                    beep('up')
                    print("Monitor, GPIO {}, Resumed print").format(var_gpio_led2)
                elif (var_state == 'Printing'):
                    GPIO.output(var_gpio_led1, GPIO.HIGH)
                    GPIO.output(var_gpio_led2, GPIO.LOW)
                    beep('up')
                    print("Monitor, GPIO {}, Started Print").format(var_gpio_led2)

                if (var_state == 'Disconnected') and ((var_state_previous == 'Operational') or (var_state_previous == 'Paused') or (var_state_previous == 'Printing')):
                    GPIO.output(var_gpio_led1, GPIO.LOW)
                    GPIO.output(var_gpio_led2, GPIO.LOW)
                    beep()
                    print("Monitor, GPIO {}, Printer disconnected from OctoPrint").format(var_gpio_led1)
                elif (var_state == 'Disconnected'):
                    GPIO.output(var_gpio_led1, GPIO.LOW)
                    GPIO.output(var_gpio_led2, GPIO.LOW)
                    print("Monitor, GPIO {}, Printer not connected to OctoPrint").format(var_gpio_led1)
            sensor_value = GPIO.input(var_gpio_sen0)
            if (var_state == 'Paused') or (sensor_value == True):
                GPIO.output(var_gpio_led2, GPIO.LOW)
                sleep(0.5)
                GPIO.output(var_gpio_led2, GPIO.HIGH)
            if (sensor_value == False):
                sleep(0.5)
                GPIO.output(var_gpio_led2, GPIO.LOW)

            var_state_previous = var_state

        sleep(0.25)

# Main Process
def loop():
    var_target = 'none'
    var_jobstatus = 'none'

    while True:
        # Button - Printer Power
        input_value = GPIO.input(var_gpio_btn0)
        if input_value == False:

            # Button Long-Press - Fan Power
            var_longpress = 0
            while input_value == False:
                if  var_longpress >= 15:
                    output_value = GPIO.input(var_gpio_rly2)
                    if output_value == True:
                        print("Button, GPIO {}, Relay 2 ON").format(var_gpio_btn0)
                        GPIO.output(var_gpio_rly2, GPIO.LOW)
                        beep('up')
                    else:
                        print("Button, GPIO {}, Relay 2 OFF").format(var_gpio_btn0)
                        GPIO.output(var_gpio_rly2, GPIO.HIGH)
                        beep('down')
                    sleep(0.5)
                    while input_value == False:
                        input_value = GPIO.input(var_gpio_btn0)
                var_longpress = var_longpress + 1
                input_value = GPIO.input(var_gpio_btn0)
                sleep(0.05)

            # Button Short-Press - Printer Power
            if var_longpress < 15:
                output_value = GPIO.input(var_gpio_rly1)
                if output_value == True:
                    print("Button, GPIO {}, Relay 1 ON, Connecting to Printer").format(var_gpio_btn0)
                    #beep()                # Handled by monitor
                    GPIO.output(var_gpio_rly1, GPIO.LOW)
                    printer_push('connect')
                    var_state = printer_pull('state')
                    if var_state == 'Connected':
                        printer_push('home')
                    else:
                        print("Button, GPIO {}, Error: Failed to connect to printer").format(var_gpio_btn0)
                        beep('error')
                else:
                    print("Button, GPIO {}, Disconnecting from Printer, Relay 1 OFF, Relay 2 OFF").format(var_gpio_btn0)
                    #beep()                # Handled by monitor
                    printer_push('disconnect')
                    sleep(0.75)
                    GPIO.output(var_gpio_rly1, GPIO.HIGH)
                    GPIO.output(var_gpio_rly2, GPIO.HIGH)
                    #beep('down')          # Handled by monitor
            var_longpress = 0
            sleep(0.5)
            while input_value == False:
                input_value = GPIO.input(var_gpio_btn0)

        # Button - Home / Cancel / Reconnect
        input_value = GPIO.input(var_gpio_btn1)
        if input_value == False:
            output_value = GPIO.input(var_gpio_rly1)
            if output_value == False:
                var_state = printer_pull('state', 'detailed')

                # Button Long-Press - Calibrate Printer
                var_longpress = 0
                if var_state == 'Operational':
                    while input_value == False:
                        if  var_longpress >= 15:
                            print("Button, GPIO {}, Calibrating Printer").format(var_gpio_btn1)
                            beep('up')
                            printer_push('calibrate')
                            sleep(0.5)
                            while input_value == False:
                                input_value = GPIO.input(var_gpio_btn1)
                        var_longpress = var_longpress + 1
                        input_value = GPIO.input(var_gpio_btn1)
                        sleep(0.05)

                # Button Short-Press - Home / Cancel / Reconnect
                if var_longpress < 15:
                    #var_state = printer_pull('state', 'detailed')
                    if var_state == 'Operational':
                        print("Button, GPIO {}, Home Printhead").format(var_gpio_btn1)
                        beep('up')
                        printer_push('home')
                    elif (var_state == 'Printing') or (var_state == 'Paused'):
                        print("Button, GPIO {}, Cancel Print, Home Printhead").format(var_gpio_btn1)
                        printer_push('cancel')
                        #beep('up')            # Handled by monitor
                        printer_push('temp', 0.0)
                        printer_push('home')
                    else:
                        print("Button, GPIO {}, Connecting to Printer, Home Printhead").format(var_gpio_btn1)
                        printer_push('connect')
                        var_state = printer_pull('state')
                        if var_state == 'Connected':
                            print("Button, GPIO {}, Connection successful").format(var_gpio_btn1)
                            #beep('up')        # Handled by monitor
                            printer_push('home')
                        else:
                            print("Button, GPIO {}, Error: Failed to connect to printer").format(var_gpio_btn1)
                            beep('error')
                var_longpress = 0
            else:
                print("Button, GPIO {}, Error: Printer is currently powered-off").format(var_gpio_btn1)
                beep('error')
            sleep(0.5)
            while input_value == False:
                input_value = GPIO.input(var_gpio_btn1)

        # Button - Heat / Cool
        input_value = GPIO.input(var_gpio_btn2)
        if input_value == False:
            var_state = printer_pull('state')
            if var_state == 'Connected':

                # Button Long-Press - Printer RGB
                var_longpress = 0
                while input_value == False:
                    if var_longpress == 15:
                        print("Button, GPIO {}, RGB Color Selection").format(var_gpio_btn2)
                        printer_push('rgb', 000, 000, 000) # Off
                        sleep(0.5)
                    elif var_longpress == 16:
                        printer_push('rgb', 000, 000, 255) # Blue
                        sleep(0.5)
                    elif var_longpress == 17:
                        printer_push('rgb', 255, 000, 000) # Red
                        sleep(0.5)
                    elif var_longpress == 18:
                        printer_push('rgb', 000, 255, 000) # Green
                        sleep(0.5)
                    elif var_longpress == 19:
                        printer_push('rgb', 255, 158, 108) # On Natural
                        sleep(0.5)
                    elif var_longpress >= 20:
                        printer_push('rgb', 255, 255, 255) # On Full
                        while input_value == False:
                            input_value = GPIO.input(var_gpio_btn2)
                    var_longpress = var_longpress + 1
                    input_value = GPIO.input(var_gpio_btn2)
                    sleep(0.05)

                # Button Short-Press - Heat / Cool
                if var_longpress < 15:
                    var_target = printer_pull('target')
                    if var_target != 'Error':
                        if var_target == '0.0':
                            print("Button, GPIO {}, Warming Up (200c)").format(var_gpio_btn2)
                            beep('up')
                            printer_push('temp', var_conf_warmup_target)
                        else:
                            print("Button, GPIO {}, Cooling Down (0c)").format(var_gpio_btn2)
                            beep('down')
                            printer_push('temp', 0.0)
                    else:
                        print("Button, GPIO {}, Error: Unable to get current temp target").format(var_gpio_btn2)
                        beep('error')
                var_longpress = 0
            else:
               print("Button, GPIO {}, Error: Connection test failed").format(var_gpio_btn2)
               beep('error')
            sleep(0.5)
            while input_value == False:
                input_value = GPIO.input(var_gpio_btn2)

        # Button - Extrude
        input_value = GPIO.input(var_gpio_btn3)
        if input_value == False:
            var_state = printer_pull('state')
            if var_state == 'Connected':

                # Button Long-Press - Cold Extrude (Forced)
                var_longpress = 0
                while input_value == False:
                    if  var_longpress >= 15:
                        while input_value == False:
                            input_value = GPIO.input(var_gpio_btn3)
                            print("Button, GPIO {}, Extruding (2mm) - Forced").format(var_gpio_btn3)
                            beep('up')
                            printer_push('extrude', 2)
                            sleep(0.7)

                    var_longpress = var_longpress + 1
                    input_value = GPIO.input(var_gpio_btn3)
                    sleep(0.05)

                # Button Short-Press - Extrude (Temp Check)
                if var_longpress < 15:
                    var_target = printer_pull('target')
                    if var_target != 'Error':
                        var_target_float = float(var_target)
                        if var_target_float >= 180.0:
                            print("Button, GPIO {}, Extruding (2mm)").format(var_gpio_btn3)
                            beep('up')
                            printer_push('extrude', 2)
                        else:
                            print("Button, GPIO {}, Error: Hotend too cold to extrude").format(var_gpio_btn3)
                            beep('error')
                    else:
                        print("Button, GPIO {}, Error: Unable to get current temp target").format(var_gpio_btn3)
                var_longpress = 0
            else:
                print("Button, GPIO {}, Error: Connection test failed").format(var_gpio_btn3)
                beep('error')
            sleep(0.5)
            while input_value == False:
                input_value = GPIO.input(var_gpio_btn3)

        # Button - Play / Pause
        input_value = GPIO.input(var_gpio_btn4)
        if input_value == False:
            var_jobstatus = printer_pull('job')
            if var_jobstatus == 'Printing':
                print("Button, GPIO {}, Pause Print").format(var_gpio_btn4)
                #beep('down')              # Handled by monitor
                printer_push('pause')
            elif var_jobstatus == 'Paused':
                print("Button, GPIO {}, Resume Print").format(var_gpio_btn4)
                #beep('up')                # Handled by monitor
                printer_push('resume')
            else:
                print("Button, GPIO {}, Error").format(var_gpio_btn4)
                beep('error')
            sleep(0.5)
            while input_value == False:
                input_value = GPIO.input(var_gpio_btn4)

        sleep(0.05) # Reduce CPU usage of while loop

# Cleanup on Exit
def destroy():
    printer_push('disconnect')
    GPIO.output(var_gpio_led2, GPIO.LOW)   # led 2 off
    sleep(0.75)
    GPIO.output(var_gpio_led1, GPIO.LOW)   # led 1 off
    GPIO.output(var_gpio_rly1, GPIO.HIGH)  # Relay 1 off (printer)
    GPIO.output(var_gpio_rly2, GPIO.HIGH)  # Relay 2 off (fan)
    GPIO.output(var_gpio_led0, GPIO.LOW)   # led 0 off
    p1.terminate()
    GPIO.cleanup()

# Begin Execution
conwait()
print("Ready! Listening for inputs and state changes...")
try:
    p1 = Process(target=loop_monitor)
    p1.start()
    loop()
except KeyboardInterrupt:
    beep('down')
    destroy()
    sys.exit(1)
except Exception:
    destroy()
    sys.exit(1)
else:
    destroy()
    sys.exit(0)
