#!/usr/bin/python
#-*-coding:utf-8 -*-

'''
    sudo apt-get install
        python-pip
        libmysqlclient
    
    pip install 
        requests
        beautifulsoup4
        mysqlclient

'''
import sys
import requests
from bs4 import BeautifulSoup
import MySQLdb
import ConfigParser

gasTypeDict = {
    u'９２無鉛':'92',
    u'92':'92',
    u'９５無鉛':'95',
    u'95+':'95', 
    u'９８無鉛':'98',
    u'98':'98',
    u'酒精汽油':'alcohol',
    u'超級柴油':'diesel',
    u'LPG價格':'lpg' }

class sql:
    def __init__( self, configPath):
        self.parseConfig( configPath )
        self.connectDB()

    def parseConfig( self, configPath ):
        cp = ConfigParser.ConfigParser()
        cp.read( configPath )
        self.host = cp.get( 'db', 'host' )
        self.uid = cp.get( 'db', 'uid' )
        self.pwd = cp.get( 'db', 'pwd' )
        self.port = cp.get( 'db', 'port' )
        self.dbname = 'gaspricesql'

    def connectDB( self ):
        self.connection = MySQLdb.connect(
            host = self.host,
            user = self.uid,
            passwd = self.pwd,
            db = self.dbname)   
    
    def insertDB( self, query ):
        cur = self.connection.cursor()
        cur.execute( query )

        for row in cur.fetchall():
            print row

    def disconnectDB():
        self.connection.close()

'''
    CPC
'''
def crawlCPC():
    c_CPC_baseUrl = "http://new.cpc.com.tw/Home"
    c_CPC_gasPriceId = "OilPrice2"

    r  = requests.get(c_CPC_baseUrl)
    data = r.text
    soup = BeautifulSoup(data,"html.parser")

    for gasPriceInstance in soup.find( id=c_CPC_gasPriceId ).find_all( "dd" ):
        curName = gasPriceInstance.text.split(u'\xa0')[0]
        curName = gasTypeDict[curName]
        curPrice = gasPriceInstance.find("strong").text
        print curName, curPrice

'''
    FPCC
'''
def crawlFPCC():
    c_FPCC_baseUrl = "http://www.fpcc.com.tw/tc/affiliate.php"
    c_FPCC_gasPriceId = "GasPrice3"
    r = requests.get(c_FPCC_baseUrl)
    data = r.text
    soup = BeautifulSoup(data,"html.parser")

    for gasClassName in ["GasPrice1", "GasPrice2", "GasPrice3", "GasPrice4"] :
        gasPriceInstance = soup.find("div",class_=gasClassName)
        titleSpan = gasPriceInstance.find("span",class_="gas_l")
        curName = titleSpan.text if titleSpan else u'超級柴油'
        curName = gasTypeDict[curName]
        curPrice = gasPriceInstance.find("p",class_="pricing").text.replace(u'$',u'')
        print curName,curPrice

if __name__ == '__main__':
    if len(sys.argv) < 2: 
        print 'too few argument, missing config.ini'

    db = sql( sys.argv[1] )
    #crawlCPC()
    #crawlFPCC()