from bs4 import BeautifulSoup
import mechanize
import cookielib
from copy import copy
from time import sleep

class remaxcrawling:
    def __init__(self):
        self.BASE_URL = "http://www.remax.pt"
        self.LISTING_URL = "/PublicListingList.aspx"
        self.br=self.newconfbrowser()
        self.soup=BeautifulSoup(self.br.open(self.BASE_URL+self.LISTING_URL).read())
    
    def getnexturl(self):
        """Returns the next page url for a given soup"""
        for a in self.soup.find_all('a', 'ajax-page-link'):
            if a.find('i', 'page-next') is not None:
                return self.BASE_URL+a['href']
            else:
                pass
        return False

    def getspecimenlinks(soup):
        """Returns a dictionary[id]=href containing the captured specimend links"""
        links={}
        for td in soup.find_all('td', 'proplist_id'):
            links[td.a.string]=td.a['href']

        return links

    def printfpgeneraldata(sopa):
        for div in self.sopa.find_all('table', 'high-prop-tbl'):
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

    @staticmethod
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


 
