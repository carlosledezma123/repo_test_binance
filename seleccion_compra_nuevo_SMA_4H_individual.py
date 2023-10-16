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
       
def get_current_price(SYMBOL):
    print ("### GET PRECIO ACTUAL "+SYMBOL+" ###")
    try:
       r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+SYMBOL)
       json_response =  r.json()
       price=json_response['price']
       print (price)
       return (price)
    except Exception as e:
       print ("### EXCEPCION AL CREAR ARRAY ###")
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
       

# r = requests.get('https://www.binance.com/api/v3/ticker/price?symbol='+SYMBOL)
# json_response =  r.json()
# # print (json_response)
# PRICE=json_response['price']
# print (PRICE)
       
      
def get_vela_verde_rojo(data,PRICE):
    print ("### GET VELA VERDE ROJO ###")
    try:
       print (data.json()[-1][1])
       open_price=data.json()[-1][1]
       open_price = float (open_price)
       price = float(PRICE)
       # apertura --- 100
       # precio   --- X
       porc_cambio = (price*100/open_price)-100

       if (open_price > price):
          print ("VELA ROJA")
          r = {"TIPO_VELA":"VELA ROJA","PORC_CAMBIO":porc_cambio}
       if (open_price < price):
          print ("VELA VERDE")
          # print (str(porc_cambio))
          r = {"TIPO_VELA":"VELA VERDE","PORC_CAMBIO":porc_cambio}
       if (open_price == price):
          print ("VELA NEUTRA")
          r = {"TIPO_VELA":"VELA NEUTRA","PORC_CAMBIO":porc_cambio}
       
       # r = {"TIPO_VELA":"VELA VERDE","PORC_CAMBIO":1.2}       
       return (r)
    except Exception as e:
       print ("### EXCEPCION AL OBTENER DATOS VELA ###")
       print (e)
       return None
       
def get_densidad_ordenes(SYMBOL,LIMIT):
    # print ("### GET DATO ###")
    now= datetime.now()
    segundos_atras=now - timedelta(seconds=5)
    print (segundos_atras)
    try:
       url = "https://api.binance.com/api/v3/trades?symbol={}&limit={}".format(SYMBOL, LIMIT)
       res = requests.get(url)
       contador = 0
       for each in res.json():
          order_time = datetime.fromtimestamp(int(str(each['time'])[0:10]))
          # print("dt_object =", order_time)
          if (order_time > segundos_atras):
             contador = contador +1
             print ("Dentro del rango")
       # contador= 10
       return (contador)
          

    except Exception as e:
       print ("### EXCEPCION AL OBTENER DATOS ###")
       print (e)
       return None
 






def get_cantidad_crypto(SYMBOL,CAPITAL,PRICE):
    print ("### GET CANTIDAD SEGUN MERCADO "+SYMBOL+" ###")
    try:
      info_market = client.get_symbol_info(SYMBOL)
      # https://api.binance.com/api/v3/exchangeInfo?symbols=[%22BTCUSDT%22,%22BNBBTC%22]
      # print (info_market)
      ##### CALCULO DE DECIMALES SEGUN EL MERCADO
      LOT_SIZE_MIN_QTY = info_market['filters'][1]['minQty']
      MIN_NOTIONAL = info_market['filters'][6]['minNotional']
      PRICE_FILTER = info_market['filters'][0]['minPrice']
      baseAsset = info_market['baseAsset']
      len_decimales= LOT_SIZE_MIN_QTY.find("1")-1
      len_decimales_price = PRICE_FILTER.find("1")-1


      print("MIN_NOTIONAL-->> "+MIN_NOTIONAL)
      print("LOT SIZE-->> "+LOT_SIZE_MIN_QTY)
      print ("ACTIVO BASE --->>>"+baseAsset)
      print ("DECIMALES --->>>"+str(len_decimales))
      print ("DECIMALES PRICE --->>>"+str(len_decimales_price))
      if (len_decimales == -1):
        len_decimales = 0
        print("NUEVO VALOR DECIMALES="+str(len_decimales))
      print ("\nVALOR A INVERTIR --->>>"+str(CAPITAL))
      print ("PRECIO A COMPRAR CRYTO  --->>>"+str(PRICE))
      v_min = float(CAPITAL)/PRICE
      quantity_compra = float(round(v_min,len_decimales))
      print ("CANTIDAD A COMPRAR CRYPTO  --->>>"+str(quantity_compra))
      if (len_decimales == 0):
        quantity_compra = int(quantity_compra)
        print ("CANTIDAD A COMPRAR CRYPTO **REDONDEADO** --->>>"+str(quantity_compra))
      return ({'quantity_compra':quantity_compra,'len_decimales_price':len_decimales_price})
    except Exception as e:
      print ("### EXCEPCION AL OBTENER CANTIDAD CRYTO COMPRA ###")
      print (e)
      return None
      
def get_cantidad_crypto_venta(SYMBOL,QTY):
    print ("### GET CANTIDAD SEGUN MERCADO "+SYMBOL+" ###")
    try:
      info_market = client.get_symbol_info(SYMBOL)
      # print (info_market)
      ##### CALCULO DE DECIMALES SEGUN EL MERCADO
      LOT_SIZE_MIN_QTY = info_market['filters'][1]['minQty']
      MIN_NOTIONAL = info_market['filters'][6]['minNotional']
      baseAsset = info_market['baseAsset']
      len_decimales= LOT_SIZE_MIN_QTY.find("1")-1


      print("MIN_NOTIONAL-->> "+MIN_NOTIONAL)
      print("LOT SIZE-->> "+LOT_SIZE_MIN_QTY)
      print ("ACTIVO BASE --->>>"+baseAsset)
      print ("DECIMALES --->>>"+str(len_decimales))
      if (len_decimales == -1):
        len_decimales = 0
        print("NUEVO VALOR DECIMALES="+str(len_decimales))
      
      quantity_venta = QTY[0:(QTY.find(".")+len_decimales+1)]
      print (quantity_venta)
      quantity_venta = float(quantity_venta)
      print ("CANTIDAD A VENDER CRYPTO  --->>>"+str(quantity_venta))
      if (len_decimales == 0):
        quantity_venta = int(quantity_venta)
        print ("CANTIDAD A COMPRAR CRYPTO **REDONDEADO** --->>>"+str(quantity_venta))
      return (quantity_venta)
    except Exception as e:
      print ("### EXCEPCION AL CREAR CANTIDAD CRYPTO VENTA ###")
      print (e)
      return None



 
# def compra_market(SYMBOL,LIMIT):
    # # print ("### GET DATO ###")
    # now= datetime.now()
    # segundos_atras=now - timedelta(seconds=5)
    # print (segundos_atras)
    # try:
       # url = "https://api.binance.com/api/v3/trades?symbol={}&limit={}".format(SYMBOL, LIMIT)
       # res = requests.get(url)
       # contador = 0
       # for each in res.json():
          # order_time = datetime.fromtimestamp(int(str(each['time'])[0:10]))
          # # print("dt_object =", order_time)
          # if (order_time > segundos_atras):
             # contador = contador +1
             # print ("Dentro del rango")
       # return (contador)
          

    # except Exception as e:
       # print ("### EXCEPCION AL OBTENER DATOS ###")
       # print (e)
       # return None
       
# def place_order_market(order_type,precio):
    # #order type could be buy or sell 
    # # before that , we have to initialize the binance client 
    # if(order_type == "buy"):
        # # we will place buy order
        # # order = client.create_order(symbol=SYMBOL, side="buy",quantity=QNTY,type="MARKET") # for type i am going with market order, so whatever price at market. it will place order 
        
    # else:
        # # order = client.create_order(symbol=SYMBOL, side="sell", quantity=QNTY,type="MARKET") # same thing but changed side 

    # print("order placed successfully!") 
    # # print(order)
    # return


# def place_order_limit(order_type):
    # #order type could be buy or sell 
    # # before that , we have to initialize the binance client 
    # if(order_type == "buy"):
        # # we will place buy order
        # # order = client.create_order(symbol=SYMBOL, side="buy",quantity=QNTY,type="MARKET") # for type i am going with market order, so whatever price at market. it will place order 
        
    # else:
        # # order = client.create_order(symbol=SYMBOL, side="sell", quantity=QNTY,type="MARKET") # same thing but changed side 

    # print("order placed successfully!") 
    # # print(order)
    # return
    
# ############## CONSULTA EN PRODUCCION  ######
try:
   # client = Client(api_key, api_secret, testnet=True) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file
   client = Client(api_key, api_secret) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file

except Exception as e:
   print (e)
print ("### SIGO ###")


buy = False #it means we are yet to buy and have not bought
sell = True #we have not sold , but if you want to buy first then set it to True xh7zj91u 2kziuiwa


while 1:
   file = open(APP_PATH+"\\SELECCION_COMPRA_NUEVO_MODELO_4H.LOG", "a")
   try:
      dateTimeObj = datetime.now()
      timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
      con_sql3 = sqlite3.connect(DB_PATH)
      cursor = con_sql3.cursor()
      sql = '''select *, (100.15*precio_actual/100) as ganancia from entradas_compra 
      where  localtime >= datetime('now', '-3 minutes', 'localtime') AND STATUS_CV IS NULL
      and (condicion='VELA VERDE NEUTRA' 
      OR condicion='VELA VERDE ALCISTA'
      )
      order by DIF_RSI desc '''
      cursor.execute(sql)
      row = cursor.fetchone()
      # row = ('TROYUSDT',0.0032)
    
      if (row):
         print (row)
         # if (row[6] > 0.5):
         SYMBOL = row[0]
           # TIME_PERIOD = "15m"
           # LIMIT = "200"
         # price = row[1]          ## LO QUE VIENE DE BD PARA EL MODELO DE PRUEBA
         price = float(get_current_price(SYMBOL))
         rsi_actual = row[2]
         
         ##################LOGICA DE COMPRA MARKET POR APIS  ###########
         
         CAPITAL = 15
         QNTY= get_cantidad_crypto(SYMBOL,CAPITAL,price)
         QNTY_COMPRA = QNTY['quantity_compra']
         LEN_DECIMALES_PRECIO = QNTY['len_decimales_price']
         if (LEN_DECIMALES_PRECIO == -1):
            LEN_DECIMALES_PRECIO = 0
         #### PRICE CUANDO CAMBIA DE PRECIO
         # price = 0.0032
         CAPITAL_REAL_INVERTIDO = QNTY_COMPRA*price
         # len_decimales_price= len((str(price).split("."))[1])
         print (CAPITAL_REAL_INVERTIDO)
         print ("CAPITAL REAL INVERTIDO ="+str(CAPITAL_REAL_INVERTIDO))
         ##### PARA CALCULAR CANTIDAD NETA LUEGO DE LAS COMISIONES
         QNTY_VENTA =QNTY_COMPRA-(0.1*QNTY_COMPRA/100)
         print ("CANTIDAD NETA A VENDER= "+str(QNTY_VENTA))

         # order = client.create_order(symbol=SYMBOL, side="buy",quantity=QNTY,type="MARKET")
         # price= order['fills'][0]['price']
         # QNTY = float(order['fills'][0]['qty'])
         # price= round(float(price),len_decimales_price)
         # ACTIVO_BASE= order['fills'][0]['commissionAsset']

         # #### PARA OBTENER EL FACTOR + GANANCIA   

         # ##################### VENTA A LIMITE EN PRODUCCION ################################
         # BalanceCrypto = client.get_asset_balance(asset=ACTIVO_BASE).get('free')
         # print("ACTIVO BASE BALANCE: "+BalanceCrypto)
         # QNTY_VENTA = get_cantidad_crypto_venta(SYMBOL,BalanceCrypto)
         
         FACTOR_IGUALACION = (QNTY_COMPRA * 100 / QNTY_VENTA)-100

         print ("FACTOR_IGUALACION= " +str(FACTOR_IGUALACION))
         precio_compra = price
         porc_ganador =  FACTOR_IGUALACION + 0.2 + 0.1
         porc_perdida = 0.5
         # # # precio_venta_ganador = precio_compra+(porc_ganador*precio_compra/100)
         # # # precio_venta_perdida = precio_compra-(porc_perdida*precio_compra/100)
         precio_venta_ganador = round(precio_compra+(porc_ganador*precio_compra/100),LEN_DECIMALES_PRECIO)
         precio_venta_perdida = round(precio_compra-(porc_perdida*precio_compra/100),LEN_DECIMALES_PRECIO)
         
         print ("######## COMPRA MARKET  A "+str(price)+"###########")
         
         print("Precio COMPRA " +str(price))
         print("QTY COMPRA " +str(QNTY_COMPRA))
         print("QTY VENTA " +str(QNTY_VENTA))
         print("Porcentaje Ganador  " +str(porc_ganador))
         print("FACTOR_IGUALACION " +str(FACTOR_IGUALACION))
         print("Precio venta Ganador " +str(precio_venta_ganador))
         print("Precio venta Perdedor " +str(precio_venta_perdida))
         
         file.write("COMPRA;"+str(price)+";"+str(CAPITAL_REAL_INVERTIDO)+";"+SYMBOL+";"+timestampStr+"\n")
         # file.write (str(order)+"\n")
         
         
         
         # ##################### VENTA A LIMITE EN PRODUCCION ################################
         # # BalanceCrypto = client.get_asset_balance(asset=ACTIVO_BASE).get('free')
         # # print("ACTIVO BASE BALANCE: "+BalanceCrypto)
         # # QNTY_VENTA = get_cantidad_crypto_venta(SYMBOL,BalanceCrypto)
         # print ("CANTIDAD A VENDER CRYPTO "+ACTIVO_BASE+"=", QNTY_VENTA)
         # order_limit_ganadora = client.order_limit_sell(symbol=SYMBOL, quantity=QNTY_VENTA, price=precio_venta_ganador)
         # print ("#### ORDEN LIMITE GANADORA ####")
         # print(order_limit_ganadora)
         # file.write (str(order_limit_ganadora)+"\n")
         file.close()
         # orderid=order_limit_ganadora['orderId']
        # ##################### FIN A LIMITE EN PRODUCCION ################################
        
         buy = True
         while buy:
         

         
         
         
           try:
              precio_tiempo_real = float(get_current_price(SYMBOL))
           except Exception as e:
              print ("### EXCEPCION OBTENER PRECIO ACTUAL ###")
              print (e)
              sleep(10)
           print("Precio COMPRA " +str(precio_compra))
           print("QTY COMPRA " +str(QNTY_COMPRA))
           print("QTY VENTA " +str(QNTY_VENTA))
           print("Porcentaje Ganador + " +str(porc_ganador))
           print("FACTOR_IGUALACION" +str(FACTOR_IGUALACION))
           print("Precio venta Ganador " +str(precio_venta_ganador))
           print("Precio venta Perdedor " +str(precio_venta_perdida))
           sleep(2)
           ########################### OBTENCION VELA ROJA ACTUAL Y PASADA
           #### TENGO 2 OPCIONES, O 1 VELA ROJA Y 0.50 , O 2 VELAS ROJAS SEGUIDAS
           TIME_PERIOD = "15m"
           LIMIT = "200" 
           data_klines = get_data_klines(SYMBOL,TIME_PERIOD,LIMIT)
           sleep (3)
           VELA_VERDE_ROJA_ACTUAL = get_vela_verde_rojo(data_klines,precio_tiempo_real)
           VELA_VERDE_ROJA_PASADA = get_verde_rojo_atras (data_klines)
           
           
           
           
           # #### AQUI VALIDO EL STATUS DE LA ORDEN LIMITE
           # ##SI SE EJECUTO, MARCO BUY = FALSE
           # ##SI NO SE EJECUTÓ, SIGO ESPERANDO Y MANTENGO BUY =TRUE
           # status_order_json = client.get_order( symbol=SYMBOL, orderId=orderid)
           # status_order_limit = status_order_json['status']
           # print (status_order_json)
           # print (status_order_limit)
           # sleep(1)
           # if (status_order_limit == 'FILLED'):
           
           if (precio_tiempo_real >= precio_venta_ganador):
              dateTimeObj = datetime.now()
              timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
              print ("### VENDO Y GANO "+str(porc_ganador)+" PORCIENTO al PRECIO MERCADO DE "+str(precio_tiempo_real))
              print (precio_tiempo_real)
              print (precio_venta_ganador)
              file = open(APP_PATH+"\\SELECCION_COMPRA_NUEVO_MODELO_4H.LOG", "a")
              USDT_GANADOR = QNTY_VENTA*precio_tiempo_real - (((QNTY_VENTA*precio_tiempo_real)*0.1)/100)
              file.write("VENTA GANADORA;"+str(precio_venta_ganador)+";PORCENTAJE GANADOR: "+str(porc_ganador)+";CANT_USDT_LUEGO_VENTA: "+str(USDT_GANADOR)+";"+SYMBOL+";"+timestampStr+"\n")
              # file.write(str(status_order_json)+"\n")  
              buy= False
              file.close()  
              sql = ''' UPDATE ENTRADAS_COMPRA SET STATUS_CV='GANADORA' WHERE CRYTO_PAR= ?  AND RSI_ACTUAL = ? '''
              cursor.execute(sql,(SYMBOL,rsi_actual))
              con_sql3.commit()
              # con_sql3.close()
              
              
           if (precio_tiempo_real <= precio_venta_perdida and (VELA_VERDE_ROJA_ACTUAL['TIPO_VELA']== 'VELA ROJA')):
              # ##### PRIMERO AQUI DEBO CANCELAR ORDEN LIMIT 
              # result = client.cancel_order(symbol=SYMBOL,orderId=orderid)
              # print (result)
              # sleep (2)
              # ##### SEGUNDO AQUI DEBO GENERAR ORDEN MERCADO
              # order = client.create_order(symbol=SYMBOL, side="sell",quantity=QNTY_VENTA,type="MARKET")
              # print (order)
              # sleep (1)
              
              dateTimeObj = datetime.now()
              timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
              print ("### VENDO Y PIERDO "+str(porc_perdida)+" PORCIENTO al PRECIO MERCADO DE "+str(precio_tiempo_real))
              print (precio_tiempo_real)
              print (precio_venta_perdida)
              file = open(APP_PATH+"\\SELECCION_COMPRA_NUEVO_MODELO.LOG", "a")
              file.write("VENTA PERDEDORA;"+str(precio_venta_perdida)+";"+str(porc_perdida)+";"+SYMBOL+";"+timestampStr+"\n")
              # file.write(str(status_order_json)+"\n")  
              file.close()
              buy= False
              sql = ''' UPDATE ENTRADAS_COMPRA SET STATUS_CV='PERDEDORA' WHERE CRYTO_PAR= ?  AND RSI_ACTUAL = ? '''
              cursor.execute(sql,(SYMBOL,rsi_actual))
              con_sql3.commit()
              break
              
           if (VELA_VERDE_ROJA_ACTUAL['TIPO_VELA']== 'VELA ROJA' and  VELA_VERDE_ROJA_PASADA['TIPO_VELA']== 'VELA ROJA'):
              # ##### PRIMERO AQUI DEBO CANCELAR ORDEN LIMIT 
              # result = client.cancel_order(symbol=SYMBOL,orderId=orderid)
              # print (result)
              # sleep (2)
              # ##### SEGUNDO AQUI DEBO GENERAR ORDEN MERCADO
              # order = client.create_order(symbol=SYMBOL, side="sell",quantity=QNTY_VENTA,type="MARKET")
              # print (order)
              # sleep (1)
              
              dateTimeObj = datetime.now()
              timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
              print ("### VENDO Y PIERDO POR DOBLE VELA ROJA"+str(porc_perdida)+" PORCIENTO al PRECIO MERCADO DE "+str(precio_tiempo_real))
              print (precio_tiempo_real)
              print (precio_venta_perdida)
              file = open(APP_PATH+"\\SELECCION_COMPRA_NUEVO_MODELO.LOG", "a")
              file.write("VENTA PERDEDORA;"+str(precio_venta_perdida)+";"+str(porc_perdida)+";"+SYMBOL+";"+timestampStr+"\n")
              # file.write(str(status_order_json)+"\n")  
              file.close()
              buy= False
              sql = ''' UPDATE ENTRADAS_COMPRA SET STATUS_CV='PERDEDORA' WHERE CRYTO_PAR= ?  AND RSI_ACTUAL = ? '''
              cursor.execute(sql,(SYMBOL,rsi_actual))
              con_sql3.commit()
              break
              
 


      con_sql3.close()
      dateTimeObj = datetime.now()
      timestampStr= dateTimeObj.strftime("%d%m%Y %H:%M:%S")
      delay=5
      print ("##### ESPERA "+str(delay)+" SEGUNDOS ##### "+timestampStr)
      # file.write("\n##### ESPERA  "+str(delay)+" SEGUNDOS ##### "+timestampStr +"\n")
      # file.close()
      sleep(delay)
   except Exception as e:
      print ("### EXCEPCION DURANTE CORRIDA DEL PROGRAMA PRINCIPAL ###")
      print (e)
      sleep(20)

  
   
   
   
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
# from cryto_change_sma
# where localtime >= datetime('now', '-5 minutes', 'localtime')
# group by cryto_par
# order by contador desc


# 1. DETERMINAR DENTRO DE LAS OPCIONES, CUALES SON EL MERCADO QUE TIENE LA MAYOR DIFERENCIA.
# 2. MAYOR DIFERENCIA ENTRE PRECIO DE APERTURA Y PRECIO ACTUAL PORCENTUAL
# 3. DETERMINAR SI ES VELA ROJA O VELA VERDE
	  
      
      # select c1.CRYTO_PAR,c1.PRECIO_ACTUAL,c1.sma8,(c1.PRECIO_ACTUAL*100/c1.sma8)-100 as porc_dif_sma_price,
# c1.LOCALTIME
# from cryto_change_sma c1
# where c1.cryto_par='ACMUSDT' and
# c1.localtime = 
# (select max(c2.localtime) from cryto_change_sma c2 where c2.CRYTO_PAR=c1.cryto_par)  

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


# Cancel an order
# result = client.cancel_order(
# symbol='BNBBTC',
# orderId='orderId')
	  
	  
   # Get all open orders   
 # orders = client.get_open_orders(symbol='BNBBTC')

# Get all orders
# orders = client.get_all_orders(symbol='BNBBTC')


# balance = client.get_asset_balance(asset='BTC')

# trades = client.get_my_trades(symbol='BNBBTC')


# order = client.create_order(
    # symbol = symbol, 
    # side = SIDE_BUY, 
    # type = ORDER_TYPE_STOP_LOSS_LIMIT, 
    # timeInForce = TIME_IN_FORCE_GTC, 
    # quantity = quantity, 
    # price = price, 
    # stopPrice = stopPrice)
	  
