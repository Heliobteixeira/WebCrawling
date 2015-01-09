import json
import csv
import pdb
import codecs
from pprint import pprint
import cStringIO

def loadjson(jsonfile):
    emptyjson={}
    try:
        loadedfile=file(jsonfile, 'r')
        filetostring=loadedfile.read().decode("utf-8-sig")
        result=json.loads(filetostring)
        print result
        return result
    except IOError as e:
        print 'Ficheito %s vazio' % jsonfile
        return emptyjson
    except Exception as e:
        print e
        #pdb.set_trace()
inputdir='output/json/'
outputdir='output/csv/'
inputfilename='mined_urls_classNC_out.json'
jsondata = loadjson(inputdir+inputfilename)
outputfilename=outputdir+inputfilename.strip('.json')+'.csv'


fields=["titulo", "preco", "desc", 'erate', 'url', 'lat', 'lng']
propertyfields=[]
for id, line in jsondata.iteritems():
    for field, value in line['properties'].iteritems():
        if field not in propertyfields:
            propertyfields.append(field)

#header=map(lambda f: f.encode('utf-8'), fields+propertyfields)
header=fields+propertyfields

with codecs.open(outputfilename, 'w', 'utf-8') as outputfile:
    outputfile.write(';'.join(header))

    for id, line in jsondata.iteritems():
        row=[]
        for field in fields:
            value=""
            if field in line:
                if isinstance(line[field], list):
                    value=line[field][0].replace(';', ',')
                else:
                    value=line[field].replace(';', ',')
            row.append(value)
                
        for field in propertyfields:
            value=""
            properties=line['properties']
            if field in properties:
                value=properties[field].replace(';', ',')
            row.append(value)
        
        print len(row)        
        outputfile.write("\n"+';'.join(row))
    
