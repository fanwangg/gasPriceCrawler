'''
    sudo apt-get install
        python-pip
        libmysqlclient
    
    pip install 
        requests
        beautifulsoup4
        mysqlclient

'''

import requests
from bs4 import BeautifulSoup
import MySQLdb

gasTypeDict = {
    u'９２無鉛':'92',
    u'92':'92',
    u'９５無鉛':'95',
    u'95+':'95', 
    u'９８無鉛':'98',
    u'98':'98',
    u'酒精汽油':'alc',
    u'超級柴油':'do' }

'''
    CPC
'''

c_CPC_baseUrl = "http://new.cpc.com.tw/Home"
c_CPC_gasPriceId = "OilPrice2"

r  = requests.get(c_CPC_baseUrl)
data = r.text
soup = BeautifulSoup(data)

for gasPriceInstance in soup.find( id=c_CPC_gasPriceId ).find_all( "dd" ):
    typeName = gasPriceInstance.text.split(u'\xa0')[0]
    typePrice = gasPriceInstance.find("strong").text
    print typeName
    print typePrice

'''
    FPCC
'''

c_FPCC_baseUrl = "http://www.fpcc.com.tw/tc/affiliate.php"
c_FPCC_gasPriceId = "GasPrice3"
r = requests.get(c_FPCC_baseUrl)
data = r.text
soup = BeautifulSoup(data)

for gasClassName in ["GasPrice1", "GasPrice2", "GasPrice3", "GasPrice4"] :
    gasPriceInstance = soup.find("div",class_=gasClassName)
    titleSpan = gasPriceInstance.find("span",class_="gas_l")
    curName = titleSpan.text if titleSpan else u'超級柴油'
    curName = gasTypeDict[curName]
    curPrice = gasPriceInstance.find("p",class_="pricing").text.replace(u'$',u'')
    print curName
    print curPrice



