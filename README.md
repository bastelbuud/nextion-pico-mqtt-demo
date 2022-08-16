# nextion-pico-mqtt-demo
Demo app, to control the position of a servo-motor with a nextion hmi display using mqtt.
In a nextion hmi display we define a slider. 
The position (value) of the slider is transferred, via serial port, to a pico w. 
The pico w reads the data, and transform it into a MQTT publish message.
On a second pico w an MQTT subsription retrieves the new position of the slider and is moving a servo motor in the right position.

The following files are used:
nextion-mqtt-example.zip contains the files to create the project in the free nextion editor (only for windows) : https://nextion.tech/nextion-editor/

The main_nextion.py file has to be installed as main.py on the pico w which is connected to the nextion display (the sender)

The main_servo.py file has to be copied as main.py on the pico with he servo connected ton GPIO15 ( the receiver).

The file secrets.py conatins the credentials for the wifi network and the mqtt server, and has to be cioied on both of the pico w's




