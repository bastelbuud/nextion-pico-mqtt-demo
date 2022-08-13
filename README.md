# nextion-pico-mqtt-demo
Demo app, to control the position of a servomotor with a nextion display using mqtt.
An a nextion display we define a slider. The position (value) of the slider is transferred, via serial port, to a pico w. 
The pico w retroieves the position of the slider, and transform it into a MQTT publish message.
On another pico w, a MQTT subsriber retrieves the new position of the slider and is moving a servo motor in the right position.

Code will follow

