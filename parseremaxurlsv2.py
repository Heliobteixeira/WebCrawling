# -*- coding: latin-1 -*-
import json
from bs4 import BeautifulSoup
import urllib2
import pdb
from pprint import pprint
import codecs

ADVANCEDSEARCH_URL='http://www.remax.pt/AdvancedListingSearch.aspx'
XMLLISTING_URL='http://www.remax.pt/handlers/listinglist.ashx?Lang=pt-PT&mode=list&sc=12&tt=261&cr=2&cur=EUR&la=All&sb=PriceIncreasing'

JSONFILE='output/json/MinedUrls.json'
MAXRETRIES=30


def loadjsonfile(jsonfile):
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

def readhtml(url):
    fp=urllib2.urlopen(url)
    return fp.read()
    
def soupiffy(html):
    return BeautifulSoup(html)

def getregions(soup):
    """ Retorna dictionary [IdDistrito] = 'Nome Distrito' 
        a partir da soup da pagina da pesquisa avançada da Remax
    """
    regions={}

    regionssoup=soup.find(id="ctl00_GeoSelection_ddlRegionRow")
    for option in regionssoup.find_all('option'):
        value=option.get('value')
        if value<>'' and int(value)>0: 
            regions[int(value)]=option.string

    return regions

def getprovinces(soup):
    """ Retorna dictionary [IdConcelho] = 'Nome Concelho' 
        a partir da soup da pagina da pesquisa avançada da Remax
    """
    provinces={}

    provincessoup=soup.find(id="ctl00_GeoSelection_ddlProvince")
    for option in provincessoup.find_all('option'):
        value=option.get('value')
        if value<>'' and int(value)>0: 
            provinces[int(value)]=option.string

    return provinces

def getcities(soup):
    """ Retorna dictionary [IdCidade] = 'Nome Cidade' 
        a partir da soup da pagina da pesquisa avançada da Remax
    """
    cities={}

    citiessoup=soup.find(id="ctl00_GeoSelection_ddlCity")
    for option in citiessoup.find_all('option'):
        value=option.get('value')
        if value<>'' and int(value)>0: 
            cities[int(value)]=option.string

    return cities

def getpropertytypes(soup):
    """ Retorna dictionary [IdTipoPropriedade] = 'Nome do Tipo de Propriedade' 
        a partir da soup da pagina da pesquisa avançada da Remax
    """
    propertytypes={}

    propertytypessoup=soup.find(id="ctl00_ddlPropertyType")
    for option in propertytypessoup.find_all('option'):
        value=option.get('value')
        if value<>'' and int(value)>0: 
            propertytypes[int(value)]=option.string

    return propertytypes

def scraprecordsfromlistingsoup(soup):
    jsonvar={}
    for td in soup.find_all('td', 'proplist_id'):
        a=td.find('a')
        jsonvar[a.string]=a.get('href')

    return jsonvar


def saveresults(province, propertytype, results, jsonfile):
    jsonvar=loadjsonfile(jsonfile) #Load existing json

    for id, url in results.items():
        data={}  
        print 'Saving:' + id + url
        data['url']=url
        data['province']=province
        data['propertytype']=propertytype
        jsonvar[str(id)]=data
        with codecs.open(jsonfile, 'w', 'utf-8') as file:    
            json.dump(jsonvar, file, indent=4, sort_keys=False, ensure_ascii=False)

def generatelistingurl(page_nbr, region_id, province_id, city_id, propertytype_id):
    global XMLLISTING_URL
    url=XMLLISTING_URL
    
    if region_id>0:
        url+='&r='+str(region_id)

    if province_id>0:
        url+='&p='+str(province_id)

    if city_id>0:
        url+='&c='+str(city_id)

    if propertytype_id>0:
        url+='&pt='+str(propertytype_id)

    url+='&page='+str(page_nbr)

    return url


html=readhtml(ADVANCEDSEARCH_URL)
soup=soupiffy(html)

# Parse several variable IDs
regions=getregions(soup)
provinces=getprovinces(soup)
cities=getcities(soup)
propertytypes=getpropertytypes(soup)

selec_propertytypes = {}
for propertytype_id, propertytype in propertytypes.items():
    answer = str(raw_input("Recolher dados de propriedades do tipo "+propertytype.encode('utf-8')+"? (s/n) R:"))
    if answer.lower() == "s":
        selec_propertytypes[propertytype_id]=propertytype

if len(selec_propertytypes)==0:
    print('Seleccionados todos os tipos de propriedade.')
    selec_propertytypes=propertytypes

pprint(selec_propertytypes)

count=0
for province_id, province_name in provinces.items():
    for selec_propertytype_id, selec_propertytype in selec_propertytypes.items():
        pagecount=1
        while True:
            print(pagecount)
            errorcount=0
            while errorcount<MAXRETRIES:      
                url=generatelistingurl(pagecount, 0, province_id, 0, selec_propertytype_id)
                jsondata=json.loads(readhtml(url))       
                try:
                    soup=soupiffy(jsondata['llContentContainerHtml'])
                except KeyError:
                    print('Unable to fetch proper json array. Got: ',jsondata)
                    print('Url: ',url)
                    errorcount+=1
                    print('Retrying('+str(errorcount)+')...')              
                    continue
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    errorcount+=1
                    print('Retrying('+str(errorcount)+')...')
                    continue
                break

            jsonresults=scraprecordsfromlistingsoup(soup)
            if len(jsonresults)>0:
                count+=len(jsonresults)
                pagecount+=1
                saveresults(province_name, selec_propertytype, jsonresults, JSONFILE)
            else:
                print('No results found. Skipping to next...')
                break

            #saveurl(province_id, selec_propertytype, id, url, jsonfile)
print('Nº Total de Registos:'+str(count))        
pdb.set_trace()
