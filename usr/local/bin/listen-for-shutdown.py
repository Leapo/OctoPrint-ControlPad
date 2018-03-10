#!/usr/bin/env python
import RPi.GPIO as GPIO
import subprocess
from time import sleep

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Starup Sound
p = GPIO.PWM(12, 600)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.18)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 600)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.07)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 300)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.08)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 600)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.09)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 1800)       #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.07)                  #Sustain
p.stop()

# Wait for power button
GPIO.wait_for_edge(3, GPIO.FALLING)

# Shutdown Sound
p = GPIO.PWM(12, 1800)       #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.18)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 600)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.07)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 300)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.08)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 600)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.09)                  #Sustain
p.stop()
sleep(0.05)                  #Pause
p = GPIO.PWM(12, 200)        #GPIO, Hz
p.start(50)                  #Duty cycle
sleep(0.07)                  #Sustain
p.stop()

subprocess.call(['shutdown', '-h', 'now'], shell=False)
