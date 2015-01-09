#!/usr/bin/env python
# -*- coding: latin-1 -*-

from bs4 import BeautifulSoup
import mechanize
import cookielib
from copy import copy
from time import sleep
import json
import pdb
import re
from time import time
from Queue import Queue, Empty
from threading import Thread
from threading import Lock
import codecs

STARTTIME=time()
COUNT=0
LASTSAVE=time()
MAXSAVEINTERVAL=60  # seconds
JSONDATA={}

inputdir='output/json/'
outputdir='output/json/'
jsonfile='mined_urls_classNC.json'


def getspecimenlinks(soup):
    """Returns a dictionary[id]=href containing the captured specimend links"""
    links={}
    for td in soup.find_all('td', 'proplist_id'):
        links[td.a.string]=td.a['href']

    return links

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

def savedata(JSONDATA, jsonfile):
    #jsonvar=loadjson(jsonfile) #Load existing json
    #try:
    #    jsonvar[id]=item
    #except Exception as e:
    #    print e
        #pdb.set_trace()
    
    with codecs.open(jsonfile, 'w', 'utf-8') as output_file:
        #try:
        json.dump(JSONDATA, output_file, indent=4, sort_keys=False, ensure_ascii=False)
        #except Exception as e:
        #    print e
        #    print 'Jsonvar:'
        #    print jsonvar
        #    print 'Json inserido: '
        #    print item
        #    pdb.set_trace()

def idexists(id, jsonfile):
    id=str(id)
    jsonvar=loadjson(jsonfile) #Load existing json
    if id in jsonvar:
        return True
    else:
        return False

def newconfbrowser():
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=10)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]    
    return br,cj

def parsetabledata(sopa):
    caract={}
    for div in sopa.find_all('div', 'data-item'):
        #pdb.set_trace()
        value=div.contents[1].text
        field=div.contents[2].text
        #pdb.set_trace()
        if all([field, value]):
            caract[field]=value
        else:
            pdb.set_trace()
            print 'Value'+str(value)
            print 'Field'+str(field)
            print 'Erro parsing field'
    return caract       

def extractfloat(string):
    return re.findall("[-+]?\d*\.\d+|\d+", string)[0] # re.findall returns a list

def parsegpscoords(soup):
    scripts=soup.find_all(has_no_src)
    lat=None
    lng=None
    for js in scripts:
        jstext=js.text
        
        for l in jstext.splitlines():
            
            if l.find(' var lat') >0:
                lat=extractfloat(l)
                
            if l.find(' var lng') >0:
                lng=extractfloat(l)
    if all([lat, lng]):
        return lat, lng
    else:
        return False
    
def has_no_src(tag):
    return tag.name=='script' and not tag.has_attr('src') and not tag.has_attr('type')

class ThreadMechanizeUrl(Thread):
    
    def __init__ (self, outputfile, queue, lock):
        self.outputfile = outputfile
        self.queue=queue
        self.lock=lock
        Thread.__init__ (self)

    def run(self):
        global STARTTIME
        global COUNT
        global JSONDATA
        global LASTSAVE

        while True:
            elapsed=time()-STARTTIME
            parspersec=COUNT/elapsed
            (id, url)=self.queue.get()
            data={}
            print "%s urls in %0.2f min " % (COUNT, elapsed/60.0) + " | %0.2furls/sec | " % parspersec +'Parsing:'+id
            (br, cj)=newconfbrowser()
            
            try:
                html=br.open(url).read()
                #pdb.set_trace()
            except:
                print id+' unavailable'
                continue
            else:       
                soup=BeautifulSoup(html)
                
                # Default values
                data['titulo']=""
                data['preco']=""
                data['properties']=""
                data['desc']=""
                data['erate']=""
                data['url']=""
                data['lat']=""
                data['lng']=""


                title=soup.find(id='ctl00_lblListingTitle')
                price=soup.find(attrs={"class":"key-price"})
                properties=parsetabledata(soup)
                desc=soup.find(attrs={"class":'desc-short'})
                erating=soup.find(attrs={"id":'ctl02_imgEnergyRating'})

                try:
                    data['titulo']=title.text
                except:
                    print 'Error parsing title of '+id
                    pass

                try:
                    data['preco']=price.text
                except:
                    print 'Error parsing price of '+id
                    pass

                try:
                    data['properties']=properties
                except:
                    print 'Error parsing properties of '+id
                    pass

                try:
                    data['desc']=desc.text
                except:
                    print 'Error parsing description  of '+id
                    pass

                try:
                    classif=erating['src'].split('_')[1].split('.')[0]
                    data['erate']=classif
                except:
                    print 'Error parsing rate of '+id
                    pass

                try:
                    data['url']=url
                except:
                    print 'Error parsing url of '+id
                    pass

                try:
                    gps=parsegpscoords(soup)
                    if gps:
                        (data['lat'], data['lng'])=gps
                except:
                    print 'Error parsing coords of '+id
                    pass

                # Adds data
                JSONDATA[id]=data

                self.lock.acquire()

                if (time()-LASTSAVE) > MAXSAVEINTERVAL:
                    savedata(copy(JSONDATA), outputjsonfile)
                    LASTSAVE=time()
                    print "Data saved..."

                self.lock.release()
                COUNT+=1
                self.queue.task_done()

        self.lock.acquire()
        savedata(copy(JSONDATA), outputjsonfile)
        self.lock.release()
        print "End of task"
        
            
        
print 'Started...'

queue = Queue()
lock = Lock()

outputjsonfile=outputdir+jsonfile.strip(".json")+'_out.json'
urls=loadjson(inputdir+jsonfile)
JSONDATA=loadjson(outputjsonfile)
#spawn a pool of threads, and pass them queue instance 
for i in range(5):
    t = ThreadMechanizeUrl(outputjsonfile, queue, lock)
    t.setDaemon(True)
    t.start()
    
for id, url in urls.items():
    if id in JSONDATA:
        print id+' already parsed. Continuing to the next one...'
    else:
        try:
            queue.put((id, url))      
        except KeyboardInterrupt:
            print "Stopping..."
queue.join()
savedata(copy(JSONDATA), outputjsonfile)
