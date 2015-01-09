from bs4 import BeautifulSoup
import mechanize
import cookielib
from copy import copy
from time import sleep

def getnexturl(soup):
    """Returns the next page url for a given soup"""
    global BASE_URL
    for a in soup.find_all('a', 'ajax-page-link'):
        if a.find('i', 'page-next') is not None:
            return BASE_URL+a['href']
        else:
            pass
    return False

def getspecimenlinks(soup):
    """Returns a dictionary[id]=href containing the captured specimend links"""
    global BASE_URL
    links={}
    for td in soup.find_all('td', 'proplist_id'):
        links[td.a.string]=td.a['href']

    return links

def printfpgeneraldata(sopa):
    for div in sopa.find_all('table', 'high-prop-tbl'):
        id=div.find('td', 'proplist_id')
        id=id.a

        address=div.find('td', 'proplist_address')
        address=address.a
        
        price=div.find('a', 'proplist_price')

        desc=div.find('div', 'proplist_main')
        desc=desc.div.a

        caract={}
        for subdiv in div.find_all('div', 'data-item'):
            auxsubdiv=copy(subdiv)
            spantag=auxsubdiv.span.extract()
            caract[auxsubdiv.text.strip()]=spantag.text.strip()

        try:
            print 'ID:'+id.text + ' Morada:' + address.text + ' Preco:' + price.text + ' Desc:'+desc.text
            for idx, c in caract.items():
                print idx+':'+c
        except:
            print 'Error parsing one speciment'
            pass

def newconfbrowser():
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=10000)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]    
    return br

BASE_URL = "http://www.remax.pt"
LISTING_URL = "/PublicListingList.aspx"


 
br=newconfbrowser()

soup=BeautifulSoup(br.open(BASE_URL+LISTING_URL).read())
if soup is not None:
    while True:
        printfpgeneraldata(soup)
        sleep(1)
        br=newconfbrowser()
        soup=BeautifulSoup(br.open(getnexturl(soup)).read())
    
else:
    print 'Unable to retreive data from site'
