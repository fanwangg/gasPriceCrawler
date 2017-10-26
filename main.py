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
from datetime import datetime

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

class GasPriceEntity:
    def __init__( self, supplier, gasType, price):
        self.supplier = supplier
        self.gasType = gasType
        self.price = price

class Sql:
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
            db = self.dbname )   

    def executeQuery( self, query ):
        self.cur = self.connection.cursor()
        self.cur.execute( query )

    def insertData( self, priceEntity ):
        today = datetime.today()
        query = 'INSERT INTO gas VALUES (NOW(), \'{0}\', \'{1}\', \'{2}\', \'{3}\')'.format( today.strftime("%U"), priceEntity.supplier, priceEntity.gasType, priceEntity.price)
        self.executeQuery( query )
        self.connection.commit()

    def showData( self ):
        query = 'SELECT * FROM gas'
        self.executeQuery( query )
        for row in self.cur.fetchall():
            print row

    def disconnectDB( self ):
        self.connection.close()

class Crawler:
    def __init__( self, configPath ):
        self.db = Sql( configPath )

    '''
    CPC
    '''
    def updateCPC( self ):
        c_CPC_baseUrl = "http://new.cpc.com.tw/Home"
        c_CPC_gasPriceId = "OilPrice2"

        r  = requests.get(c_CPC_baseUrl)
        data = r.text
        soup = BeautifulSoup(data,"html.parser")

        for gasPriceInstance in soup.find( id=c_CPC_gasPriceId ).find_all( "dd" ):
            curType = gasPriceInstance.text.split(u'\xa0')[0]
            curType = gasTypeDict[curType]
            curPrice = gasPriceInstance.find("strong").text
            p = GasPriceEntity( 'CPC', curType, curPrice )
            self.db.insertData( p )

    '''
        FPCC
    '''
    def updateFPCC( self ):
        c_FPCC_baseUrl = "http://www.fpcc.com.tw/tc/affiliate.php"
        c_FPCC_gasPriceId = "GasPrice3"
        r = requests.get(c_FPCC_baseUrl)
        data = r.text
        soup = BeautifulSoup(data,"html.parser")

        for gasClassName in ["GasPrice1", "GasPrice2", "GasPrice3", "GasPrice4"] :
            gasPriceInstance = soup.find("div",class_=gasClassName)
            titleSpan = gasPriceInstance.find("span",class_="gas_l")
            curType = titleSpan.text if titleSpan else u'超級柴油'
            curType = gasTypeDict[curType]
            curPrice = gasPriceInstance.find("p",class_="pricing").text.replace(u'$',u'')
            p = GasPriceEntity( 'FPCC', curType, curPrice )
            self.db.insertData( p )

if __name__ == '__main__':
    if len(sys.argv) < 2: 
        print 'too few argument, missing config.ini'

    crawler = Crawler( sys.argv[1] )
    crawler.updateCPC()
    crawler.updateFPCC()

    #crawler.db.showData()
    crawler.db.disconnectDB()