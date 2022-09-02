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

def flashLed(times,duration=0.5):
    for i in range(0,times,1):
        led.value(1)            #Set led turn on
        time.sleep(duration)
        led.value(0)            #Set led turn off
        time.sleep(duration)
    led.value(0)

# the following functions are only to ensure the mqtt connection is still alice

mqtt_con_flag = False #mqtt connection flag
pingresp_rcv_flag = True #indicator that we received PINGRESP
lock = True #to lock callback function from recursion when many commands are received look mqqt.py line 138
PING_INTERVAL = 60
next_ping_time = 0 

def ping_reset():
 global next_ping_time
 next_ping_time = time.time() + PING_INTERVAL #we use time.time() for interval measuring interval
 print("Next MQTT ping at", next_ping_time)

def ping():
 client.ping()
 ping_reset()


def check():
 global next_ping_time
 global mqtt_con_flag
 global pingresp_rcv_flag
 if (time.time() >= next_ping_time): #we use time.time() for interval measuring interval
   if not pingresp_rcv_flag :
    mqtt_con_flag = False #we have not received an PINGRESP so we are disconnected
    print("We have not received PINGRESP so broker disconnected")
   else :
    print("MQTT ping at", time.time())
    ping()
    pingresp_rcv_flag = False
 res = client.check_msg()
 if(res == b"PINGRESP") :
  pingresp_rcv_flag = True
  print("PINGRESP")

def mqtt_connect():
 global next_ping_time 
 global pingresp_rcv_flag
 global mqtt_con_flag
 global lock
 while not mqtt_con_flag:
  
  try:
   client.connect()
   client.subscribe(prefix+"MOTOR")
   # when subsribed flah led 10 times
   flashLed(10)
   client.publish(prefix+'mesg', "subscribed")
   mqtt_con_flag=True
   pingresp_rcv_flag = True
   next_ping_time = time.time() + PING_INTERVAL
   lock = False # we allow callbacks only after everything is set
  except Exception as e:
   print("Error in mqtt connect: [Exception] %s: %s" % (type(e).__name__, e))
  time.sleep(0.5) # to brake the loop
  
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

client = MQTTClient(prefix+"picow-read", secrets.MQTTSERVER,secrets.MQTTUSER, secrets.MQTTPWD, keepalive=300, ssl=False, ssl_params={})
client.set_callback(callback)

startC = time.ticks_ms()
while True:
    mqtt_connect()#ensure connection to broker
    try:
     check()
    except Exception as e:
     print("Error in Mqtt check message: [Exception] %s: %s" % (type(e).__name__, e))
     print("MQTT disconnected due to network problem")
     lock = True # reset the flags for restart of connection
     mqtt_con_flag = False 
    #client.check_msg()
     if time.ticks_diff(time.ticks_ms(),startC) > 10000:
        flashLed(2,0.125)
        print("heartbeat")
        startC = time.ticks_ms()
