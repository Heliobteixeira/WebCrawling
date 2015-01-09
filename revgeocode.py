from urllib2 import urlopen
import json

def loadjson(jsonfile):
    emptyjson={}
    try:
        loadedfile=file(jsonfile, 'r')
        filetostring=loadedfile.read().decode("utf-8-sig")
        result=json.loads(filetostring)
        return result
    except IOError as e:
        print 'Ficheito %s vazio' % jsonfile
        return emptyjson
    except Exception as e:
        print e
        #pdb.set_trace()

inputdir='output/json/'
jsonfile='mined_urls.json'
data=loadjson(jsonfile)

lat=0
lng=0

for i, item in data.items():
	if 'lat' in item and 'lng' in  item and item['lat']<>"" and item['lng']<>"" :
		lat=item['lat']
		lng=item['lng']
		response = urlopen('http://open.mapquestapi.com/nominatim/v1/reverse.php?format=json&lat=%s&lon=%s'
									% (lat, lng))
		result=json.loads(response.read())

		if 'error' in result:
			print result['error']+':'+i
		else:
			print(result)

