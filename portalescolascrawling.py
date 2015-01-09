#!/usr/bin/env python
import urllib2
from pprint import pprint
from xml.dom.minidom import parseString
import csv
import codecs


urls=[]
#urls.append('https://www.portaldasescolas.pt/portal/server.pt/gateway/PTARGS_0_15076_514_240_0_43/RoteiroEscolas/AjaxServlet?_=1408125789158&type=markers&dreId=104&concelho=&concelhoId=&escola=&pageValue=')
#urls.append('https://www.portaldasescolas.pt/portal/server.pt/gateway/PTARGS_0_15076_514_240_0_43/RoteiroEscolas/AjaxServlet?_=1408135035207&type=markers&dreId=105&concelho=&concelhoId=&escola=&pageValue=')
#urls.append('https://www.portaldasescolas.pt/portal/server.pt/gateway/PTARGS_0_15076_514_240_0_43/RoteiroEscolas/AjaxServlet?_=1408135098548&type=markers&dreId=102&concelho=&concelhoId=&escola=&pageValue=')
#urls.append('https://www.portaldasescolas.pt/portal/server.pt/gateway/PTARGS_0_15076_514_240_0_43/RoteiroEscolas/AjaxServlet?_=1408135141655&type=markers&dreId=103&concelho=&concelhoId=&escola=&pageValue=')
urls.append('https://www.portaldasescolas.pt/portal/server.pt/gateway/PTARGS_0_15076_514_240_0_43/RoteiroEscolas/AjaxServlet?_=1408148501257&type=markers&dreId=101&concelho=&concelhoId=&escola=&pageValue=')


outputfilename='result.csv'

# Write headers
#with codecs.open(outputfilename, 'a', 'utf-8') as outputfile:
#	fields=['nome', 'morada', 'postal', 'localidade', 'lat', 'lng', 'codigo']
#	outputfile.write(';'.join(fields))

for url in urls:
	page=95
	nbrpages=95
	while page<=nbrpages:
		print page
		file=urllib2.urlopen(url+str(page),None,120)
		data=file.read()
		try:
			dom=parseString(data)
		except:
			print('Error parsing page nbr:'+str(page))
			continue
		else:
			for tag in dom.getElementsByTagName('marker'):
				row=[]
				row.append(tag.getElementsByTagName('nome')[0].firstChild.nodeValue)
				row.append(tag.getElementsByTagName('morada')[0].firstChild.nodeValue)
				row.append(tag.getElementsByTagName('postal')[0].firstChild.nodeValue)
				row.append(tag.getElementsByTagName('localidade')[0].firstChild.nodeValue)
				row.append(tag.getElementsByTagName('lat')[0].firstChild.nodeValue)
				row.append(tag.getElementsByTagName('lng')[0].firstChild.nodeValue)
				row.append(tag.getElementsByTagName('codigo')[0].firstChild.nodeValue)

				nbrpages=dom.getElementsByTagName('nPages')[0].firstChild.nodeValue			
				nbrpages=int(nbrpages)

				print(row[0])
				
				with codecs.open(outputfilename, 'a', 'utf-8') as outputfile:
					outputfile.write("\n"+';'.join(row))
		
		page+=1


