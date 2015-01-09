from urllib2 import urlopen


lat=0
lng=0

for i in range(0, 6000)
	lat+=0.001
	lng+=0.001
	response = urlopen('http://open.mapquestapi.com/nominatim/v1/reverse.php?format=json&lat=%s&lon=%s'
								% (lat, lng))
	print(response.read())

