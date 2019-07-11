


from machine import Pin
import time

def run(): 

    num = 20

    t = 0.1

    for i in range(num):

        led=Pin(2,Pin.OUT)

        led.value(1)              #turn off

        time.sleep(t)

        led.value(0)              #turn on

        time.sleep(t)


