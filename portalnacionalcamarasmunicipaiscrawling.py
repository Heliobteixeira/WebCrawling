#!/usr/bin/env python
import urllib2
from pprint import pprint
from bs4 import BeautifulSoup
import csv
import codecs
import os.path
from urlparse import urlparse, parse_qs

resulturls=[]
for page in range(1,32):
	if page == 1:
		resulturls.append('http://portalnacional.com.pt/entidades/administracao-publica/camaras-municipais/')
	else:
		resulturls.append('http://portalnacional.com.pt/entidades/administracao-publica/camaras-municipais/%i/' % page)

outputfilename='camarasmunicipais.csv'
rooturl='http://portalnacional.com.pt'

# Write headers if file does not already exists
if not os.path.isfile(outputfilename):
	with codecs.open(outputfilename, 'a', 'utf-8') as outputfile:
		fields=['nome','lat', 'lng', 'link']
		outputfile.write(';'.join(fields))

for resulturl in resulturls:
	camarasurls=[]
	print resulturl
	try:
		file=urllib2.urlopen(resulturl,None,120)
	except:
		print('Cannot open:'+resulturl)
		continue ## Cotinues with next

	try:
		soup=BeautifulSoup(file.read())
	except:
		print('Error parsing soup from : '+str(resulturl))
		continue
	else:
		# ** Parse all camaras found in the current page **
		for item in soup.body.find_all(class_="item"):
			try:
				btag=item.find('b')
			except:
				continue
			
			try:
				atag=btag.find('a')
			except:
				continue

			camarasurls.append(atag['href'])

		tempCamarasData=[]
		for camaraurl in camarasurls:
			# ** Parse each camara url info **
			print('Parsing %s:' % camaraurl)
			try:
				file=urllib2.urlopen(rooturl+camaraurl,None,120)
			except:
				print('Cannot open Camara Url: %s . Continuing with next one...' % camaraurl)
				continue

			try:
				soup=BeautifulSoup(file.read())
			except:
				print('Error parsing soup from : '+str(camaraurl))
				continue

			# Parse latitude and longitude
			fotoThumb=soup.body.find(class_="fotoThumb")
				
			imgTag=fotoThumb.find('img')
			imgSrc=imgTag['src']
			parsedUrl=urlparse(imgTag['src'])
			queryVars=parse_qs(parsedUrl.query)

			(lat, lng) = queryVars['center'][0].split(',')


			# Parse remaining data
			fotoPageInfo=soup.body.find(class_="fotoPageInfo")

			for dataField in fotoPageInfo.find_all(class_="fotoInfoField"):
				if dataField.find(class_="field").string=='Empresa / Entidade':
					nomeCamara=dataField.find(class_="value").string

			print(nomeCamara)
			print('latitude: %s  longitude: %s' % (lat, lng) )
			tempCamarasData.append([nomeCamara,lat, lng, rooturl+camaraurl])

		# Write urls to file
		with codecs.open(outputfilename, 'a', 'utf-8') as outputfile:
			for fieldsLine in tempCamarasData:
				outputfile.write("\n"+';'.join(fieldsLine))






