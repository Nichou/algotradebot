from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
import os

class ClientSingleton:
    def __init__(self):
        self.client = None
    def init(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

clientSingleton = ClientSingleton()

def initClient(api_key, api_secret):
    clientSingleton.init(api_key, api_secret)

class BinanceClient:
    def __init__(self, asset, target_asset):
       
        if (clientSingleton.client == None):
            raise Exception('No client detected')
        self.client = clientSingleton.client
        self.asset = asset 
        self.target_asset = target_asset
        self.pair = target_asset+asset
    
    def getBalanceTargetAmount(self):
        
        try:
            amount = round(self.getBalance()/self.getPairPrice(), 5);
        except:
            raise Exception('Failed to get target amount');
        return amount
        
    def parseTargetValue(self, value):
        try:
            amount = round(value/self.getPairPrice(), 5);
        except:
            raise Exception('Failed to get target value');
        return amount
        
    def getBalance(self):
        
        try:
            balance = float(self.client.get_asset_balance(asset=self.asset)['free'])
        except:
            raise Exception('Failed to get balance')
        return balance
        
    def getTargetBalance(self):
        
        try:
            balance = float(self.client.get_asset_balance(asset=self.target_asset)['free'])
        except:
            raise Exception('Failed to get balance')
        return balance        
        
    def getPairPrice(self):
        
        try:     
            price = float(self.client.get_symbol_ticker(symbol=self.pair)['price'])
        except:
            raise Exception('Failed to get target price')
        return price

class Status:
    
    def __init__(self):
        self.ok = False
        self.istime = False
        self.runtime_error = False
        self.update = False
        self.message = "{}"
        self.meta = None
        
    def postMessage(self, msg):
        self.message = msg
        self.update = True
        
    def updated(self):
        if self.update:
            self.update = False
            return True
        return False

class Log:
    def __init__(self):
        self.message_queue = []
        self.reset()
        
    def postMessage(self, msg):
        current_time = time.time()
        timestamp = time.strftime("%Y %b %d %H:%M:%S", time.localtime(current_time))+": "
        
        self.message_queue.append(timestamp+msg+"\n")
        
    def update(self):
    
        body = ""
        for message in self.message_queue:
            body += message
            
        with open("log.txt","a") as log_file:
            log_file.write(body)
            
        self.message_queue = []    
            
    def reset(self):
        if os.path.exists("log.txt"):
            os.remove("log.txt")
            
    def readLog(self):
    
        if not(os.path.exists("log.txt")):
            return "'log.txt' file not found"
              
        with open("log.txt") as log_file:
            return log_file.read()
        
        return " "

class Bot: 

    def __init__(self):
        self.status = Status()
        self.log = Log()
      