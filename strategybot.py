from botengine import *
from utils import *
import json
from decimal import *
        
gnum_variences = 0.0
gtrade_pairs = None
gbalance = 0.0
ginit = False
        
def getPriority(e):
    return e.priority
        
class StrategyBot(Bot):
    def __init__(self, binance_client):
        super().__init__()
        self.binance_client = binance_client
        self.priority = 0
        self.pm = {}
        
        self.loadMeta()
        if self.status.meta['holding']:
            self.priority = 1
        
        bot_handler.append(self)
        
    def checkTime(self):
    
        current_time = time.time()
        day = time.strftime("%Y %b %d ", time.localtime(current_time))
        
        start_timestamp = day+"17:00:00" 
        end_timestamp = day+"17:15:00"
        
        stobj = time.strptime(start_timestamp, "%Y %b %d %H:%M:%S")
        etobj = time.strptime(end_timestamp, "%Y %b %d %H:%M:%S")
        
        slapse = time.mktime(stobj)
        elapse = time.mktime(etobj)
        
        self.pm = loadProgramMeta()
        
        if (current_time >= slapse and current_time < elapse) or self.pm["post_sell"]:
            self.status.istime = True
        else:
            self.status.istime = False

        print(" "+start_timestamp+" "+end_timestamp+" "+str(slapse)+" "+str(elapse)+" ")
          
    def initGlobals(self):
    
        global gnum_variences
        global gtrade_pairs
        global gbalance
        global ginit
    
        if gnum_variences == 0.0:
                    
            trade_pairs = []
                    
            for bt in bot_handler:
                trade_pairs.append(bt.binance_client.pair)
        
            gnum_variences, gtrade_pairs = numUnderMeanVariences(self.binance_client.client, trade_pairs, 0.0)


        gbalance = self.binance_client.getBalance()
        
        ginit = True
        
    def resetGlobals(self):
        global gnum_variences
        global gtrade_pairs
        global gbalance
        global ginit        
    
        gnum_variences = 0.0
        gtrade_pairs = None
        gbalance = 0.0
        ginit = False
    
    def loadMeta(self):
        try:
            with open('./bots_data/'+self.binance_client.pair+'_meta.json') as json_file:
                self.status.meta = json.load(json_file)             
        except FileNotFoundError:
            self.status.meta = {"holding": False}
    def saveMeta(self):
        with open('./bots_data/'+self.binance_client.pair+'_meta.json', 'w') as json_file:
            json.dump(self.status.meta, json_file)            
    
    def checkStrategy(self):
        
        self.log.postMessage(self.binance_client.pair+" Strategy checked")
        self.checkTime()
        
        if (not(self.status.istime)):
            
            self.status.ok = False
            self.resetGlobals()
            return       
        
        self.loadMeta()
            
        try:
            if (ginit == False):
                self.initGlobals()
            
        except BinanceAPIException as be:
            self.status.postError("RUNTIME ERROR (code: 10): "+str(be))
        except KeyError as ke:
            self.status.postError("RUNTIME ERROR (code: 11): "+str(ke))
        except Exception as e:
            self.status.postError("RUNTIME ERROR (code: 12): "+str(e))
        
        if (gtrade_pairs == None):
            return
        
        if (gtrade_pairs[self.binance_client.pair] or self.status.meta['holding']):
            self.status.ok = True
        
    def order(self):
        
        try:
            with open('settings.json') as json_file:
                settings = json.load(json_file)
                
        except FileNotFoundError: 
                self.status.postError("RUNTIME ERROR (code: 9): "+str(e))
                return
        
        max_trade_value = settings['max_trade_value']
        
        
        try: 
            pair_price = self.binance_client.getPairPrice()     
            buy_quantity = 0.0
            
            if (gnum_variences != 0.0):
                buy_quantity = self.binance_client.parseTargetValue(max_trade_value)/gnum_variences
            
                if (gbalance < max_trade_value):
                    buy_quantity = gbalance/gnum_variences
                
            sell_quantity = self.binance_client.getTargetBalance()
            
            info = self.binance_client.client.get_symbol_info(self.binance_client.pair)
            minqty = info['filters'][1]['minQty']
            
            dec = minqty.find('1')-1
            
            buy_quantity = round(round(buy_quantity, dec)-2.0/pow(10.0,dec),dec)
            sell_quantity = round(round(sell_quantity, dec)-2.0/pow(10.0,dec),dec)
            
            
        except BinanceAPIException as e:
            self.status.postError("RUNTIME ERROR (code: 3): "+str(e))
            return
        except Exception as e:
            self.status.postError("RUNTIME ERROR (code: 4): "+str(e))
            return
            
            
        try:
            
            if (not(self.status.meta['holding'])):
                test_order = self.binance_client.client.create_test_order(symbol=self.binance_client.pair, side='BUY', type='MARKET',quantity=buy_quantity)
            else:
                test_order = self.binance_client.client.create_test_order(symbol=self.binance_client.pair, side='SELL', type='MARKET',quantity=sell_quantity)
        
        except BinanceAPIException as e:
            self.status.postError("RUNTIME ERROR (code: 5): "+str(e))
            return
        except BinanceOrderException as e:
            self.status.postError("RUNTIME ERROR (code: 6): "+str(e))
            return
            
        
        if (not(self.status.meta['holding']) and not(self.pm["lock_buy"])):
            try:
                order_result = self.binance_client.client.create_order(symbol=self.binance_client.pair, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=buy_quantity)
                
                self.status.meta['holding'] = True
                              
                self.status.postMessage("Succesfully buyed "+str(buy_quantity)+" "+self.binance_client.target_asset+" at "+str(pair_price)+" USDT\nclientOrderId: "+order_result['clientOrderId'])
                
            except BinanceAPIException as e:
                self.status.postError("RUNTIME ERROR (code: 7): "+str(e))
                return
            
        else:
            try:
                order_result = self.binance_client.client.create_order(symbol=self.binance_client.pair, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=sell_quantity)
                
                self.status.meta['holding'] = False
                
                if (self.pm["post_sell"] == False):               
                    self.pm["lock_buy"] = True
                self.pm["post_sell"] = True
                
                saveProgramMeta(self.pm)                
                              
                self.status.postMessage("Succesfully selled "+str(sell_quantity)+" "+self.binance_client.target_asset+" at "+str(pair_price)+" USDT\nclientOrderId: "+order_result['clientOrderId'])
                
            except BinanceAPIException as e:
                self.status.postError("RUNTIME ERROR (code: 8): "+str(e))
                return
            except Exception as e:
                self.status.postError("RUNTIME ERROR (code: 13): "+str(e))
                return              
        
        self.saveMeta()
        
        self.status.ok = False;
    
    def process(self):
        
        if (self.status.runtime_error):            
            return
        
        self.checkStrategy();
        
        if (self.status.ok):
            self.order()
    
    
       
        