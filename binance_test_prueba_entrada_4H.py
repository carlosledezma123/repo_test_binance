import requests
import json
import re
import sqlite3
import os
from time import sleep
from datetime import datetime, date, timedelta
import talib #talib library for various calculation related to financial and technical indicators
import numpy as np
from config_produ import api_key , api_secret
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

APP_PATH = os.getcwd()
DB_PATH = APP_PATH+ '\\base_cryto.db'

# https://www.binance.com/api/v3/ticker/price
# https://www.binance.com/api/v3/ticker/price?symbol=USTCBUSD


# QNTY = 0.00065 # we will define quantity over here ....0.00060
def get_data_klines(SYMBOL,TIME_PERIOD,LIMIT):
    # print ("### GET DATO ###")
    try:
       url = "https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD, LIMIT)
       res = requests.get(url) 
       #now we can either save the response or convert it to numpy array , converting is more reasonable 
       # return_data = []
       # for each in res.json():
           # return_data.append(float(each[4]))
       # return np.array(return_data)
       return (res)
    except Exception as e:
       print ("### EXCEPCION AL OBTENER DATOS ###")
       print (e)
       return None
       
def get_array_close_data(data):
    # print ("### GET DATO ###")
    try:
       return_data = []
       for each in data.json():
           return_data.append(float(each[4]))
       return np.array(return_data)
    except Exception as e:
       print ("### EXCEPCION AL CREAR ARRAY ###")
       print (e)
       return None
       
       
def get_vela_verde_rojo(data,PRICE):
    print ("### GET DATO VELA###")
    print ("### PRECIO ACTUAL "+str(PRICE))
    try:
       print (data.json()[-1][1])
       open_price=data.json()[-1][1]
       open_price = float (open_price)
       open_high=float (data.json()[-1][2])
       open_low= float (data.json()[-1][3])
       price = float(PRICE)
       # apertura --- 100
       # precio   --- X
       porc_cambio = (price*100/open_price)-100
       print (str(porc_cambio))
       
       # PARA SACAR VELA ALCISTA/BAJISTA
       longitud_vela= open_high-open_low
       porc_longitud_alcista= 75*longitud_vela/100
       porc_longitud_bajista= 25*longitud_vela/100
       
       precio_75_vela = open_low+porc_longitud_alcista
       precio_25_vela = open_low+porc_longitud_bajista
       try:
          porc_precio_vela = (price-open_low)*100/longitud_vela
       except Exception as e:
          porc_precio_vela = 0



       if (open_price > price):
          print ("VELA ROJA")
          r = {"TIPO_VELA":"VELA ROJA","PORC_CAMBIO":porc_cambio}
       if (open_price < price):
          print ("VELA VERDE")
          # print (str(porc_cambio))
          # r = {"TIPO_VELA":"VELA VERDE","PORC_CAMBIO":porc_cambio}
          if (price >= precio_75_vela):
             print ("###VELA VERDE ALCISTA ###")
             tipo_vela_verde = "VELA VERDE ALCISTA"
          elif (price <= precio_25_vela):
             print ("###VELA VERDE BAJISTA ###")
             tipo_vela_verde = "VELA VERDE BAJISTA"
          else :
             print ("###VELA VERDE NEUTRA ###")
             tipo_vela_verde = "VELA VERDE NEUTRA"
          
          
          
          r = {"TIPO_VELA":"VELA VERDE","PORC_CAMBIO":porc_cambio,"CONDICION":tipo_vela_verde,"PORCETAJE_PRECIO_VELA":porc_precio_vela}
       if (open_price == price):
          print ("VELA NEUTRA")
          r = {"TIPO_VELA":"VELA NEUTRA","PORC_CAMBIO":porc_cambio}
          
       return (r)
    except Exception as e:
       print ("### EXCEPCION AL OBTENER DATOS VELA ###")
       print (e)
       return None
       
def get_densidad_ordenes(SYMBOL,LIMIT):
    # print ("### GET DATO ###")
    now= datetime.now()
    segundos_atras=now - timedelta(seconds=120)
    print (segundos_atras)
    try:
       url = "https://api.binance.com/api/v3/trades?symbol={}&limit={}".format(SYMBOL, LIMIT)
       res = requests.get(url)
       contador = 0
       # for each in data.json():
       for each in res.json():
          order_time = datetime.fromtimestamp(int(str(each['time'])[0:10]))
          # print("dt_object =", order_time)
          if (order_time > segundos_atras):
             contador = contador +1
             # print ("Dentro del rango")
       # contador= 10
       return (contador)
          

    except Exception as e:
       print ("### EXCEPCION AL OBTENER DATOS ###")
       print (e)
       return None
       
def get_verde_rojo_atras(data):
    # print ("### GET DATO ###")
    try:

       open_price = float(data.json()[-2][1])
       close_price = float(data.json()[-2][4])
    
       
       if (open_price > close_price):
          # print ("VELA ROJA")
          r = {"TIPO_VELA":"VELA ROJA"}
       if (open_price < close_price):
          # print ("VELA VERDE")
          # print (str(porc_cambio))
          r = {"TIPO_VELA":"VELA VERDE"}
       if (open_price == close_price):
          # print ("VELA NEUTRA")
          r = {"TIPO_VELA":"VELA NEUTRA"}
          
       return (r)
       
       
       

    except Exception as e:
       print ("### EXCEPCION AL OBTENER DATOS ###")
       print (e)
       return None


# ############## CONSULTA EN PRODUCCION  ######
try:
   # client = Client(api_key, api_secret, testnet=True) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file
   client = Client(api_key, api_secret) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file

except Exception as e:
   print (e)
print ("### SIGO ###")

buy = False
while 1:	
# r = requests.get('https://www.binance.com/api/v3/ticker/price?symbol=USTCBUSD')

# https://api.binance.com/api/v3/ticker/price
   
   try:
      # r = requests.get('https://www.binance.com/api/v3/ticker/price')
      r = requests.get('https://api.binance.com/api/v3/ticker/price')
      sleep(5)
      json_response =  r.json()
      
      # file = open(APP_PATH+"\\S.txt", "a")
   
      file_entradas = open(APP_PATH+"\\ENTRADAS_RSI_SMA_4H.LOG", "a")
      file_entradas.write("################################################################################################\n")
      file_entradas.close()
      for reg in json_response:
         # print (reg)
         patronBUSD = re.compile('BUSD$')
         patronUSDT = re.compile('USDT$')
         patronUP = re.compile('UP')
         patronDOWN = re.compile('DOWN')
         patronBTC = re.compile('BTC')
         patronETH = re.compile('ETH')
         patronUSDC= re.compile('USDC')
         patronEUR= re.compile('EUR')
         patronTUSD= re.compile('TUSD')
         patronBNB= re.compile('BNB')
         patronLUNA= re.compile('LUNA')
         patronLUNC= re.compile('LUNC')
         patronUSTC= re.compile('USTC')
         patronAUCTION= re.compile('AUCTION')
            # file_lista_completa = open(APP_PATH+"\\LISTADO_COMPLETO.LOG", "a")
            # file_lista_completa.write (SYMBOL+"\n")

         if (patronUSDT.search(reg['symbol']) 
         # and  patronAUCTION.search(reg['symbol'])
         and not(patronUP.search(reg['symbol'])) and not(patronDOWN.search(reg['symbol']))
         and not (patronBTC.search(reg['symbol'])) and not (patronETH.search(reg['symbol']))  
         and not (patronUSDC.search(reg['symbol'])) and not (patronEUR.search(reg['symbol']))
         and not (patronTUSD.search(reg['symbol']))  and not (patronBUSD.search(reg['symbol'])) 
         and not (patronBNB.search(reg['symbol']))  and not (patronLUNA.search(reg['symbol']))
         and not (patronLUNC.search(reg['symbol']))  and not (patronUSTC.search(reg['symbol']))
         ): 
            file_entradas = open(APP_PATH+"\\ENTRADAS_RSI_SMA_4H.LOG", "a")


            print (reg)
            SYMBOL = reg['symbol']
            TIME_PERIOD = "4h"
            LIMIT = "200" 
            dateTimeObj = datetime.now()
            timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
            price = reg['price']
            data_klines = get_data_klines(SYMBOL,TIME_PERIOD,LIMIT)
            array_np_closing_data = get_array_close_data(data_klines)
            SMA_7_sec = round (talib.SMA(array_np_closing_data,7)[-1],4)
            SMA_7_sec_1 =round (talib.SMA(array_np_closing_data,7)[-2],4)
            SMA_7_sec_2 = talib.SMA(array_np_closing_data,7)[-3]
            SMA_7_sec_3 = talib.SMA(array_np_closing_data,7)[-4]
            SMA_50_sec = round(talib.SMA(array_np_closing_data,25)[-1],4)
            SMA_50_sec_1 = round(talib.SMA(array_np_closing_data,25)[-2],4)
            SMA_50_sec_2 = talib.SMA(array_np_closing_data,25)[-3]
            SMA_50_sec_5 = talib.SMA(array_np_closing_data,25)[-5]
            rsi= round(talib.RSI(array_np_closing_data)[-1],4)
            rsi_1= round(talib.RSI(array_np_closing_data)[-2],4)
            VELA_VERDE_ROJA_ACTUAL = get_vela_verde_rojo(data_klines,price)
            VELA_VERDE_ROJA_PASADA = get_verde_rojo_atras (data_klines)
            diferencia_RSI = round(rsi-rsi_1,2)
            diferencia_SMA = round(SMA_7_sec-SMA_50_sec,4)
            diferencia_SMA_1 = round (SMA_7_sec_1-SMA_50_sec_1,4)
            
            
            densidad_ordenes = get_densidad_ordenes(SYMBOL,LIMIT)
            print ("### PRECIO ACTUAL "+str(float(price)))
            print ("### PAR "+SYMBOL+" SMA 7 ACTUAL DE "+str(SMA_7_sec))
            print ("### PAR "+SYMBOL+" SMA 7 -1 ACTUAL DE "+str(SMA_7_sec_1))
            print ("### PAR "+SYMBOL+" SMA 25 ACTUAL DE "+str(SMA_50_sec))
            print ("### PAR "+SYMBOL+" SMA 25 -1 ACTUAL DE "+str(SMA_50_sec_1))

            print ("### PAR "+SYMBOL+" RSI ACTUAL DE "+str(rsi))
            print ("### PAR "+SYMBOL+" RSI -1 PERIODO "+str(rsi_1))
            print ("### PAR "+SYMBOL+" SMA 7 ACTUAL "+str(SMA_7_sec))
            print ("### PAR "+SYMBOL+" SMA 7 -1 PERIODO "+str(SMA_7_sec_1))
            print ("### DENSIDAD DE ORDENES = "+str(densidad_ordenes))
            print ("### VELA_VERDE_ROJA_PASADA= "+VELA_VERDE_ROJA_PASADA['TIPO_VELA'])
            print ("### TIPO_VELA_ACTUAL "+VELA_VERDE_ROJA_ACTUAL['TIPO_VELA'])
            print("#########  DIFERENCIA SMA ACTUALES #########")
            print(str(diferencia_SMA))
            print("#########  DIFERENCIA SMA -1 #########")
            print (str(diferencia_SMA_1))
            
            
            
            # print (info_market)
            
            
            
            # if ((rsi > (rsi_1+3)) and (SMA_7_sec > (SMA_7_sec_1+10))):
            
            # and VELA_VERDE_ROJA_ACTUAL == "VELA VERDE"
            
            # VELA_VERDE_ROJA_ACTUAL['TIPO_VELA'] == 'VELA VERDE'
            # (rsi > (rsi_1+2)) 
            # ((rsi > (rsi-rsi_1) > 1) and (SMA_7_sec > (SMA_7_sec_3)) 
            if ( 
            (SMA_7_sec > SMA_7_sec_1)
            and (SMA_50_sec > SMA_50_sec_1)
            and (diferencia_SMA > diferencia_SMA_1)
            and ((diferencia_SMA < 1) or (diferencia_SMA > -1))
         #   and (SMA_7_sec > SMA_50_sec) 
            # and ( float(price) > SMA_7_sec) 
            and (VELA_VERDE_ROJA_ACTUAL['TIPO_VELA']=='VELA VERDE')
            and (VELA_VERDE_ROJA_PASADA['TIPO_VELA']=='VELA VERDE')
            # and densidad_ordenes >= 40
            ):
            
              info_market = client.get_symbol_info(SYMBOL)
              print (info_market['status'])
              if (info_market['status'] == 'TRADING'):
                 print ("### ENTRADA SYMBOL "+SYMBOL)
                 # file_entradas.write("COMPRA;"+str(price)+";RSI ACTUAL;"+str(rsi)+";RSI ANTERIOR;"+str(rsi_1)+";"+SYMBOL+";"+VELA_VERDE_ROJA_ACTUAL['TIPO_VELA']+";DENSIDAD VENTAS="+str(densidad_ordenes)+";DIF_RSI="+str(diferencia_RSI)+";DIF_SMA="+str(diferencia_SMA)+";"+timestampStr+"\n")
                 file_entradas.write("COMPRA;"+str(price)+";RSI ACTUAL;"+str(rsi)+";RSI ANTERIOR;"+str(rsi_1)+";"+SYMBOL+";"+VELA_VERDE_ROJA_ACTUAL['TIPO_VELA']+";"+VELA_VERDE_ROJA_ACTUAL['CONDICION']+";DENSIDAD VENTAS="+
                 str(densidad_ordenes)+";DIF_RSI="+str(diferencia_RSI)+";DIF_SMA="+str(diferencia_SMA)+";DIF_SMA_PASADA="+str(diferencia_SMA_1)+";SMA_actual="+str(SMA_7_sec)+";SMA_1="+str(SMA_7_sec_1)+";SMA_25_sec_actual="+str(SMA_50_sec)+";SMA_25_sec_1="+str(SMA_50_sec_1)+timestampStr+"\n")
                 file_entradas.close()
                 
                 
                 con_sql3 = sqlite3.connect(DB_PATH)
                 cursor = con_sql3.cursor()
                 sql = ''' INSERT INTO ENTRADAS_COMPRA (CRYTO_PAR,PRECIO_ACTUAL,RSI_ACTUAl,RSI_ANTERIOR,DIF_RSI,TIPO_VELA,DENSIDAD_VENTAS,LOCALTIME,CONDICION,PORC_PRECIO_VELA,PORC_CAMBIO)VALUES(?,?,?,?,?,?,?,DATETIME('now','localtime'),?,?,?)'''
                 cursor.execute(sql,(SYMBOL,price,rsi,rsi_1,diferencia_RSI,VELA_VERDE_ROJA_ACTUAL['TIPO_VELA'],densidad_ordenes,VELA_VERDE_ROJA_ACTUAL['CONDICION'],VELA_VERDE_ROJA_ACTUAL['PORCETAJE_PRECIO_VELA'],VELA_VERDE_ROJA_ACTUAL['PORC_CAMBIO']))
                 con_sql3.commit()
                 con_sql3.close()
                 
                 
              # file = open(APP_PATH+"\\S.txt", "a")
            
         # sql = ''' INSERT INTO PRECIO_CRYPTO (PAR,PRECIO_NUEVO) VALUES(?,?) '''
         # cursor.execute(sql,(reg['symbol'],reg['price']))
     
            # sql = ''' UPDATE PRECIO_CRYPTO SET PRECIO_VIEJO = PRECIO_NUEVO, PRECIO_NUEVO = ? WHERE PAR = ?'''
            # cursor.execute(sql,(reg['price'],reg['symbol']))
            # sql = ''' UPDATE PRECIO_CRYPTO SET PORC_VIEJO_NUEVO = (PRECIO_NUEVO*100/PRECIO_VIEJO)-100 , DIF_NUEVO_VIEJO = (PRECIO_NUEVO-PRECIO_VIEJO) WHERE PAR = ? '''
            # cursor.execute(sql,(reg['symbol'],))
	  
      # # print (sql) 

      # con_sql3.commit()

      # sql = ''' SELECT * FROM PRECIO_CRYPTO WHERE PORC_VIEJO_NUEVO  > 0.2'''
      # cursor.execute(sql)
   
# CREATE TABLE ENTRADAS_COMPRA (
    # CRYTO_PAR     VARCHAR (20) DEFAULT NULL,
    # PRECIO_ACTUAL REAL DEFAULT NULL,
    # RSI_ACTUAl  REAL         DEFAULT NULL,
    # RSI_ANTERIOR REAL         DEFAULT NULL,
    # DIF_RSI     REAL     DEFAULT NULL,
    # TIPO_VELA   VARCHAR (20)         DEFAULT NULL,
    # DENSIDAD_VENTAS    REAL         DEFAULT NULL,
    #LOCALTIME     DATETIME     DEFAULT NULL
    
# );

   
   
      # for row in cursor.fetchall():
        # print (row)
      # print (row[0])
         # file.write(str(row)+"\n")
         # sql = ''' INSERT INTO CRYTO_CHANGE (CRYTO_PAR,PRECIO_ANTES,PRECIO_ACTUAL,PORC_CAMBIO,PRECIO_DIF,LOCALTIME)VALUES(?,?,?,?,?,DATETIME('now','localtime'))'''
      # # print (sql)
         # cursor.execute(sql,(row[0],row[1],row[2],row[3],row[4]))
         # con_sql3.commit()
	  

   
      # sql = ''' select cryto_par, count(*) as contador
      # from cryto_change
      # where localtime >= datetime('now', '-5 minutes', 'localtime')
      # group by cryto_par
      # order by contador desc'''
      # cursor.execute(sql)
   
      # for row in cursor.fetchall():
       # # print (row)
       # if (row[1] >= 2):
         # print ("###### CRYPTOS MAYOR CONTADOR #####")
         # print (row)
         # SYMBOL = row[0] #taking this as a example 
         # TIME_PERIOD= "15m" #taking 15 minute time period 
         # LIMIT = "200" # taking 200 candles as limit 
         # # closing_data = get_data(SYMBOL,TIME_PERIOD,LIMIT) #get latest closing data for the candles
         # data_klines = get_data_klines(SYMBOL,TIME_PERIOD,LIMIT) #JSON DE VELAS 15 min 200 velas
         # array_np_closing_data = get_array_close_data(data_klines)
         # SMA_8 = talib.SMA(array_np_closing_data,7)[-1]
         # print ("###### SMA_8 #####")
         # print (SMA_8)
         # sql = ''' select precio_nuevo from precio_crypto where par= ? '''
         # cursor.execute(sql,(SYMBOL,))
         # price_par= cursor.fetchone()
         # print ("###### PRECIO #####")
         # print (price_par)
         # dif_SMA_pricepar= float(price_par[0])-float(SMA_8)
         # tipo_vela_porc_cambio = get_vela_verde_rojo(data_klines,price_par[0])
         # print (tipo_vela_porc_cambio)
         # tipo_vela = tipo_vela_porc_cambio['TIPO_VELA']
         # porc_cambio = tipo_vela_porc_cambio['PORC_CAMBIO']
         # print(tipo_vela)
         # print (porc_cambio)

         # if (price_par[0] > SMA_8):
            # print ("Tentativa compra "+SYMBOL+" a "+str(price_par[0]))
         
            # sql = ''' INSERT INTO CRYTO_CHANGE_SMA (CRYTO_PAR,PRECIO_ACTUAL,SMA8,DIF_SMA_PRICE,LOCALTIME,TIPO_VELA,PORC_CAMBIO)VALUES(?,?,?,?,DATETIME('now','localtime'),?,?)'''
            # cursor.execute(sql,(SYMBOL,price_par[0],SMA_8,dif_SMA_pricepar,tipo_vela,porc_cambio))
            # con_sql3.commit()
         
      # sql = '''select cryto_par, count(*) as contador
      # from cryto_change_SMA
      # where localtime >= datetime('now', '-5 minutes', 'localtime') 
      # group by cryto_par
      # order by contador desc'''
      # cursor.execute(sql)
      # for row in cursor.fetchall():
         # if (row[1] >= 3):
            # print ("###### CRYPTOS MAYOR FILTRADO SMA #####")
            # print (row)
            # sql = '''select c1.CRYTO_PAR,c1.PRECIO_ACTUAL,c1.SMA8,(c1.PRECIO_ACTUAL*100/c1.SMA8)-100 as porc_dif_SMA_price,c1.TIPO_VELA,c1.PORC_CAMBIO,
            # c1.LOCALTIME
            # from cryto_change_SMA c1
            # where c1.cryto_par=? and
            # c1.localtime >= datetime('now', '-60 minutes', 'localtime') and
            # c1.localtime = 
           # (select max(c2.localtime) from cryto_change_SMA c2 where c2.CRYTO_PAR=c1.cryto_par)'''
            # cursor.execute(sql,(row[0],))
            # crypto_SMA = cursor.fetchone()
            # print (crypto_SMA)
         
            # if (crypto_SMA[4]== 'VELA VERDE'):
               # sql = ''' INSERT INTO CRIPTO_INFO_BUY (CRYPTO_PAR,CONTADOR,PRECIO_ACTUAL,SMA_8,PORC_DIF_SMA_PRICE,TIPO_VELA,PORC_CAMBIO,LOCALTIME)VALUES(?,?,?,?,?,?,?,DATETIME('now','localtime'))'''
               # cursor.execute(sql,(crypto_SMA[0],row[1],crypto_SMA[1],crypto_SMA[2],crypto_SMA[3],crypto_SMA[4],crypto_SMA[5]))
               # con_sql3.commit()

      # con_sql3.close()
      dateTimeObj = datetime.now()
      timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
      delay=20
      print ("##### ESPERA "+str(delay)+" SEGUNDOS ##### "+timestampStr)
      # file.write("\n##### ESPERA  "+str(delay)+" SEGUNDOS ##### "+timestampStr +"\n")
      # file.close()
      sleep(delay)
   except Exception as e:
      print ("### EXCEPCION DURANTE CORRIDA DEL PROGRAMA PRINCIPAL ###")
      print (e)
      sleep(60)

  
   
# CREATE TABLE CRIPTO_INFO_BUY (
    # CRYPTO_PAR              VARCHAR (20) DEFAULT NULL,
    # CONTADOR INTEGER(3)
    # PRECIO_ACTUAL    REAL         DEFAULT NULL,
    # SMA_8     REAL         DEFAULT NULL,
    # PORC_DIF_SMA_PRICE REAL         DEFAULT NULL,
    # TIPO_VELA  REAL         DEFAULT NULL,
    # PORC_CAMBIO  REAL         DEFAULT NULL,
    # LOCALTIME        DATETIME     DEFAULT NULL
# );
   
   
   # select cryto_par,count(*) 
# as apariciones from cryto_change where localtime >= Datetime('now', '-5 minutes','localtime')
# group by cryto_par
# order by apariciones desc
   
   
   
	  
	  # file = open(APP_PATH+"\\ARCHIVOS_ROLES_PAGO\\"+datos['concepto']+".txt", "w")
  # file.write("Primera línea" + os.linesep)
  
  
  
# select cryto_par, count(*) as contador
# from cryto_change
# where localtime >= datetime('now', '-5 minutes', 'localtime')
# group by cryto_par
# order by contador desc
	  
      
      ################ QUERY FILTRADO  #####
# select cryto_par, count(*) as contador
# from cryto_change_SMA
# where localtime >= datetime('now', '-5 minutes', 'localtime')
# group by cryto_par
# order by contador desc


# 1. DETERMINAR DENTRO DE LAS OPCIONES, CUALES SON EL MERCADO QUE TIENE LA MAYOR DIFERENCIA.
# 2. MAYOR DIFERENCIA ENTRE PRECIO DE APERTURA Y PRECIO ACTUAL PORCENTUAL
# 3. DETERMINAR SI ES VELA ROJA O VELA VERDE
	  
      
      # select c1.CRYTO_PAR,c1.PRECIO_ACTUAL,c1.SMA8,(c1.PRECIO_ACTUAL*100/c1.SMA8)-100 as porc_dif_SMA_price,
# c1.LOCALTIME
# from cryto_change_SMA c1
# where c1.cryto_par='ACMUSDT' and
# c1.localtime = 
# (select max(c2.localtime) from cryto_change_SMA c2 where c2.CRYTO_PAR=c1.cryto_par)  

####################################################
# select * from cripto_info_buy c1 where 
# c1.crypto_par in (
# select distinct crypto_par from cripto_info_buy 
# where localtime >= datetime('now', '-1 minutes', 'localtime')
# ) 
# and 
# c1.localtime = 
# (select max(c2.localtime) from cripto_info_buy c2 where c2.CRYPTO_PAR=c1.crypto_par)  
# order by porc_cambio desc
	  
      
      
# select * from cripto_info_buy c1 where 
# c1.crypto_par in (
# select distinct crypto_par from cripto_info_buy 
# where localtime >= datetime('now', '-5 minutes', 'localtime')
# ) 
# and 
# c1.localtime = 
# (select max(c2.localtime) from cripto_info_buy c2 where c2.CRYPTO_PAR=c1.crypto_par)  
# order by porc_cambio desc


###### BINANCE TIME PERIOD RECIENTE
# https://api.binance.com/api/v3/trades?symbol=ACHUSDT&limit=10
	  
	  
	  
