# -*- coding: latin-1 -*-
import json
from bs4 import BeautifulSoup
from pprint import pprint
from time import time
import urllib2
import pdb
import codecs
import sys

ADVANCEDSEARCH_URL='http://www.remax.pt/AdvancedListingSearch.aspx'
XMLLISTING_URL='http://www.remax.pt/handlers/listinglist.ashx?Lang=pt-PT&mode=list&sc=12&tt=261&cr=2&cur=EUR&la=All&sb=PriceIncreasing'

JSONFILE='output/json/MinedUrls.json'
MAXRETRIES=30

STARTTIME=time()
COUNT=0

# Support for enumerations on Python<3
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

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
        sys.exit('Erro ao abrir ficheiro Json')
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

def getmarketstatus(soup):
    """ Retorna dictionary [IdTipoEstadoMercado] = 'Nome do Estado de Mercado' 
        a partir da soup da pagina da pesquisa avançada da Remax
    """
    marketstatus={}

    marketstatussoup=soup.find(id="ctl00_ddlmarketStatus")
    for option in marketstatussoup.find_all('option'):
        value=option.get('value')
        if value<>'' and int(value)>0: 
            marketstatus[int(value)]=option.string

    return marketstatus


def scraprecordsfromlistingsoup(soup):
    records={}
    for td in soup.find_all('td', 'proplist_id'):
        a=td.find('a')
        records[a.string]=a.get('href')

    return records

def saveresults(fieldlabel, fieldvalue, records):
    global JSONFILE
    # Load existing json
    saveddata=loadjsonfile(JSONFILE)
    
    for id, url in records.items():
    	print 'Saving:' + id + url

    	id_data={}

    	# Only saves url if record doesnt exist.
    	if saveddata is not None and saveddata.has_key(str(id)):
    		id_data=saveddata[id]
    	else:
        	id_data['url']=url
        	
        id_data[fieldlabel]=fieldvalue

        saveddata[str(id)]=id_data

        # Consider removing out of for loop
        with codecs.open(JSONFILE, 'w', 'utf-8') as file:    
            json.dump(saveddata, file, indent=4, sort_keys=False, ensure_ascii=False)

def generatelistingurl(page_nbr, region_id, province_id, city_id, propertytype_id, marketstatus_id):
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

    if marketstatus_id>0:
        url+='&msu='+str(marketstatus_id)

    url+='&page='+str(page_nbr)

    return url

def collectuserforsubselection(dictlist, labelstring):
	selecteditems = {}
	for id, value in dictlist.items():
	    answer = str(raw_input("Recolher dados de "+labelstring+" "+value.encode('utf-8')+"? (s/n) :"))
	    if answer.lower() == "s":
	        selecteditems[id]=value
	    if answer.lower() == "t":
	    	selecteditems=dictlist
	    	break

	if len(selecteditems)==0:
	    print('Seleccionados todos '+ labelstring +' .')
	    selecteditems=dictlist

	pprint(selecteditems)

	return selecteditems

def fetchdatafield(Field, listingdict):
    global COUNT
    for idcode, name in listingdict.items():
        pagecount=1
        while True:
            if Field == 1: # REGION
                url=generatelistingurl(pagecount, idcode, 0, 0, 0, 0)
                fieldname='distrito'
            elif Field == 2: # PROVINCE
                url=generatelistingurl(pagecount, 0, idcode, 0, 0, 0)
                fieldname='concelho'
            elif Field == 3: # CITY
                url=generatelistingurl(pagecount, 0, 0, idcode, 0, 0)
                fieldname='cidade'
            elif Field == 4: # PROPERTY TYPE
                url=generatelistingurl(pagecount, 0, 0, 0, idcode, 0)
                fieldname='tipo_propriedade'
            elif Field == 5: # MARKET STATUS
                url=generatelistingurl(pagecount, 0, 0, 0, 0, idcode)
                fieldname='estado_mercado'
            else:
            	sys.exit('Campo desconhecido. Abortando...')


            print('Parsing: ', url)
            errorcount=0
            while errorcount<MAXRETRIES:      
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

            records=scraprecordsfromlistingsoup(soup)
            if len(records)>0:
                COUNT+=len(records)
                pagecount+=1
                saveresults(fieldname, name, records)
                elapsed=time()-STARTTIME
                parspersec=COUNT/elapsed
                print('Fetched '+str(len(records))+ "(%s urls in %0.2f min " % (COUNT, elapsed/60.0) + " | %0.2furls/sec | " % parspersec + ')')
            else:
                print('No results found. Skipping to next...')
                break        


Fields=enum('URL', 'REGION', 'PROVINCE', 'CITY', 'PROPERTYTYPE', 'MARKETSTATUS')

html=readhtml(ADVANCEDSEARCH_URL)
soup=soupiffy(html)

# Parse several variable IDs

regions=getregions(soup)
provinces=getprovinces(soup)
cities=getcities(soup)
propertytypes=getpropertytypes(soup)
marketstatuses=getmarketstatus(soup)

selec_regions = collectuserforsubselection(regions, '[Distrito]')
selec_provinces = collectuserforsubselection(provinces, '[Concelho]')
selec_cities = collectuserforsubselection(cities, '[Cidade]')
selec_proptypes = collectuserforsubselection(propertytypes, '[Tipo Propriedade]')
selec_mktstatus = collectuserforsubselection(marketstatuses, '[Estado Mercado]')


fetchdatafield(Fields.REGION, selec_regions)
fetchdatafield(Fields.PROVINCE, selec_provinces)
fetchdatafield(Fields.CITY, selec_cities)
fetchdatafield(Fields.PROPERTYTYPE, selec_proptypes)
fetchdatafield(Fields.MARKETSTATUS, selec_mktstatus)

pdb.set_trace()
