from botengine import *
from utils import *
import json

class BtcClient(BinanceClient):
    def __init__(self, api_key, api_secret):
        super().__init__(api_key, api_secret, "USDT", "BTC")
        
class BtcBot(Bot):
    def __init__(self, binance_client):
        super().__init__()
        self.binance_client = binance_client
        
    def checkTime(self):
        current_time = time.time()
        day = time.strftime("%Y %b %d ", time.localtime(current_time))
        
        start_timestamp = day+"17:00:00" 
        end_timestamp = day+"17:15:00"
        
        stobj = time.strptime(start_timestamp, "%Y %b %d %H:%M:%S")
        etobj = time.strptime(end_timestamp, "%Y %b %d %H:%M:%S")
        
        slapse = time.mktime(stobj)
        elapse = time.mktime(etobj)
        
        if (current_time >= slapse and current_time < elapse):
            self.status.istime = True 

        print(" "+start_timestamp+" "+end_timestamp+" "+str(slapse)+" "+str(elapse)+" ")
            
    def checkStrategy(self):
        
        self.checkTime()
        
        if (not(self.status.istime)):
            self.log.postMessage("Time checked")
            return       
        
        try:
            with open('meta.json') as json_file:
                self.status.meta = json.load(json_file)             
        except FileNotFoundError:
            self.status.meta = {"holding": False}
        
        bars = self.binance_client.client.get_historical_klines('BTCUSDT', '1d', limit=1000)
        symbol = self.binance_client.client.get_symbol_ticker(symbol="BTCUSDT")
        btc_price = float(symbol['price'])

        csv_handler = CSVHandler()
        
        try:
            updateClosePrices(csv_handler, btc_price)
        
        except FileNotFoundError:
            csv_handler.getDataFrame(bars)
            try:
                csv_handler.parseCSVColunm('close','close.csv')
            except KeyError as ke:
                self.status.runtime_error = True;
                self.status.postMessage("RUNTIME ERROR (code: 1): "+str(ke))
                return
        
        try:
            mean = getClosePricesNegativeVariationsMean(csv_handler.df)
        except KeyError as ke:
            self.status.runtime_error = True;
            self.status.postMessage("RUNTIME ERROR (code: 2): "+str(ke))
            return
            
        former_price = float(csv_handler.df['close'].iloc[-2])
        
        if (btc_price/former_price-1.0 < mean or self.status.meta['holding']):
            self.status.ok = True
        
    def order(self):
        
        fit_factor = 0.00001
        
        try:
            btc_price = self.binance_client.client.get_symbol_ticker(symbol="BTCUSDT")
            cash = self.binance_client.client.get_asset_balance(asset='USDT')
            buy_quantity = round(float(cash['free'])/float(btc_price['price']), 5)-fit_factor
            sell_quantity = round(float(self.binance_client.client.get_asset_balance(asset='BTC')['free']), 5)-fit_factor
            
            buy_quantity = refit5digits(buy_quantity)
            sell_quantity = refit5digits(sell_quantity)
            
        except BinanceAPIException as e:
            self.status.postMessage("RUNTIME ERROR (code: 3): "+str(e))
            return
        except Exception as e:
            self.status.postMessage("RUNTIME ERROR (code: 4): "+str(e))
            return
            
        try:
            
            if (not(self.status.meta['holding'])):
                test_order = self.binance_client.client.create_test_order(symbol='BTCUSDT', side='BUY', type='MARKET',quantity=buy_quantity)
            else:
                test_order = self.binance_client.client.create_test_order(symbol='BTCUSDT', side='SELL', type='MARKET',quantity=sell_quantity)
        
        except BinanceAPIException as e:
            self.status.postMessage("RUNTIME ERROR (code: 5): "+str(e))
            return
        except BinanceOrderException as e:
            self.status.postMessage("RUNTIME ERROR (code: 6): "+str(e))
            return
            
        
        if (not(self.status.meta['holding'])):
            try:
                order_result = self.binance_client.client.create_order(symbol='BTCUSDT', side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=buy_quantity) #success
                
                self.status.meta['holding'] = True
                
                self.status.postMessage("Succesfully buyed "+str(buy_quantity)+" BTC at "+btc_price['price']+" USDT\nclientOrderId: "+order_result['clientOrderId'])
                
            except BinanceAPIException as e:
                self.status.postMessage("RUNTIME ERROR (code: 7): "+str(e))
                return
            
        else:
            try:
                order_result = self.binance_client.client.create_order(symbol='BTCUSDT', side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=sell_quantity)
                
                self.status.meta['holding'] = False
                
                self.status.postMessage("Succesfully selled "+str(sell_quantity)+" BTC at "+btc_price['price']+" USDT\nclientOrderId: "+order_result['clientOrderId'])
                
            except BinanceAPIException as e:
                self.status.postMessage("RUNTIME ERROR (code: 8): "+str(e))
                return          
        
        with open('meta.json', 'w') as json_file:
            json.dump(self.status.meta, json_file)
        
        self.status.ok = False;
    
    def process(self):
        
        if (self.status.runtime_error):            
            return
        
        self.checkStrategy();
        
        if (self.status.ok):
            self.order()
    
    
       
        