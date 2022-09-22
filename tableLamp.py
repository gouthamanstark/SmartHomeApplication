import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

# Allows us to check the current state of the appliance connected to the network
def status():
    GPIO.setup(11,GPIO.OUT)
    status=GPIO.input(11)
    if status==1:
        return "The Lamp is currently in OFF state"
    elif(status==0):
        return "The Lamp is currently in ON state"


# Allows us to turnOn the appliance when it is in Offstate
def turnOn():
    GPIO.setup(11,GPIO.OUT)
    GPIO.output(11,GPIO.LOW)
    return "The lamp is turned on...."

# Allows us to turnOff the appliance when it is in Onstate
def turnOff():
    GPIO.setup(11,GPIO.OUT)
    GPIO.output(11,GPIO.HIGH)
    return "The lamp is tuned off..."
