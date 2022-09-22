import Adafruit_DHT


DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=24   # Raspberry Pi Pin Number to which the DHT sensor is connected  

# Reads the temperature and humidity values from teh DHT sensor
def readSensor():
	while True:
		
		humidity,temperature=Adafruit_DHT.read_retry(DHT_SENSOR,DHT_PIN)
		if humidity is not None and temperature is not None:
			return [humidity,temperature]
			
		else:
			return  "Data Couldn't be read from the sensor"

