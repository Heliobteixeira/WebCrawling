from bs4 import BeautifulSoup
import mechanize
import cookielib
from copy import copy
from time import sleep
import json
import pdb
import re

def getspecimenlinks(soup):
    """Returns a dictionary[id]=href containing the captured specimend links"""
    links={}
    for td in soup.find_all('td', 'proplist_id'):
        links[td.a.string]=td.a['href']

    return links

def loadjson(jsonfile):
    emptyjson={}
    try:
        with open(jsonfile, 'r') as file:
            return json.load(file)
    except:
        print 'Ficheiro '+jsonfile+' vazio'
        return emptyjson

def savedata(id, item, jsonfile):
    id=str(id)
    jsonvar=loadjson(jsonfile) #Load existing json
    if id in jsonvar:
        print id+' already parsed before...overwriting'
    jsonvar[str(id)]=item
    
    with open(jsonfile, 'w') as file:    
        json.dump(jsonvar, file)

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
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=10000)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]    
    return br,cj

def parsetabledata(sopa):
    caract={}
    for div in sopa.find_all('div', 'data-item'):
        #pdb.set_trace()
        value=div.contents[1]
        field=div.contents[2]
        #pdb.set_trace()
        if all([field, value]):
            caract[field.text]=value.text
        else:
            pdb.set_trace()
            print 'Value'+str(value)
            print 'Field'+str(field)
            print 'Erro parsing field'
    return caract       

def extractfloat(string):
    return re.findall("[-+]?\d*\.\d+|\d+", string)

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

print 'Started...'
jsonfile='urlsdb.json'
outputjsonfile='remaxdata_A.json'
urls=loadjson(jsonfile)
for id, url in urls.items():
    if idexists(id, outputjsonfile):
        print id+' already parsed. Continuing to the next one...'
        continue
    data={}
    print 'Parsing:'+url
    (br, cj)=newconfbrowser()
    try:
        html=br.open(url).read()
    except:
        print id+' unavailable'
        continue
    soup=BeautifulSoup(html)
    
    title=soup.find(id='ctl00_lblListingTitle')
    price=soup.find(attrs={"class":"key-price"})
    properties=parsetabledata(soup)
    desc=soup.find(attrs={"class":'desc-short'})
    erating=soup.find(attrs={"id":'ctl02_imgEnergyRating'})
    #pdb.set_trace()
    data['titulo']=title.text
    data['preco']=price.text
    data['properties']=properties
    data['desc']=desc.text
    data['erate']=erating['src']
    data['url']=url
    
    gps=parsegpscoords(soup)
    if gps:
        (data['lat'], data['lng'])=gps
    
    savedata(id, data, outputjsonfile)
        
        
