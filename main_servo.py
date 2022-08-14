# Move a servo motor on a PICO w based on a value received via a subscription of an MQTT Topic
# the Topic is DUMSHOME/SERVOTEST/MOTOR
# the value contains an integer from 0 to 180. This value represents the angle of the servo to move to
#
# tested with MQTT explorer by sending a raw value between 0 and 180 to topic DUMSHOME/SERVOTEST/MOTOR
#
# Dem Jevy seng Bastelbuud 08/2022

import network
import time
from umqtt.simple import MQTTClient
from machine import Pin, PWM
import secrets


# the led is used to flash when certain events occur (as we use a PICO W, the LED is not on pin 25, but on "LED")
# the servo is connected to GPIO15

LEDGPIO = "LED"
MOTORGPIO = 15
prefix = "DUMSHOME/SERVOTEST/"

led = Pin(LEDGPIO,Pin.OUT)
servo = PWM(Pin(MOTORGPIO))

servo.freq(50)

# the servo used is a TS90A, the following DATA are found by trial and Error


DEG0 = 1600
DEG180 = 7200
DEG90 = 4400

# function to flash LED a certain amount of times

def flashLed(times):
    for i in range(0,times,1):
        led.value(1)            #Set led turn on
        time.sleep(0.5)
        led.value(0)            #Set led turn off
        time.sleep(0.5)
    led.value(0)
    
# mqtt subscribe callback function

def callback(topic, msg):
    t = topic.decode("utf-8")
    # certain functions are not available in micropython, se we split the topic into an array and check if the last element is MOTOR
    array = t.split("/")
    flashLed(2)
    if array[len(array)-1] == 'MOTOR':
        flashLed(4)
        data = int(msg.decode("utf-8"))
        
        #housekeeping to force the value between 0 and 180
        if data < 0:
            date = 0
        if data > 180:
            data = 180
        
        # we transform the value from 0 to 180 degrees into a suitable duty value for the PWM
        data = int(data*(5600/180)+1600)
        servo.duty_u16(data)

# the heartbeat is used to keep the connection establishe

def heartbeat(first):
    global lastping
    if first:
        client.ping()
        lastping = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), lastping) >= 300000:
        client.ping()
        lastping = time.ticks_ms()
    return

# we initiate the netowrk with the credentials from the secrets.py file

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while not wlan.isconnected() and wlan.status() >= 0:
	print("Waiting to connect:")
	time.sleep(1)
# when connected flah led 5 times
flashLed(5)

client = MQTTClient(prefix+"picow-read", secrets.MQTTSERVER,user=secrets.MQTTUSER, password=secrets.MQTTPWD, keepalive=300, ssl=False, ssl_params={})
client.connect()
heartbeat(True)
client.set_callback(callback)
client.subscribe(prefix+"MOTOR")
# when subsribed flah led 10 times
flashLed(10)
client.publish(prefix+'mesg', "subscribed")

while True:
    client.check_msg()
    heartbeat(False)

    
    
    
