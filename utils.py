import pandas as pd

class CSVHandler:
    
    def __init__(self):
        self.df = None

    def parseCSV(self, path):   
        if (self.df is None):
            return
        self.df.to_csv(path)
        
    def readCSV(self, path):
        self.df = pd.read_csv(path)
        return self.df
        
    def parseCSVColunm(self, colunm, path):
        if (self.df is None):
            return
        try:
            self.df[colunm].to_csv(path)
        except KeyError:
            raise KeyError("Failed to parse csv colunm")
    
    def getDataFrame(self, data):
        colunms = {'open time':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[], 'close time':[], 'quote asset volume':[], 'number of trades':[], 'taker buy base asset volume':[], 'taker buy quote asset volume':[], 'ignore':[]}
        
        if (not(isinstance(data, list))):
            return
        if (len(data) == 0):
            return
        if (len(data[0]) != 12):
            return
        
        for line in data:
            colunms['open time'].append(line[0]) 
            colunms['open'].append(line[1]) 
            colunms['high'].append(line[2]) 
            colunms['low'].append(line[3]) 
            colunms['close'].append(line[4]) 
            colunms['volume'].append(line[5]) 
            colunms['close time'].append(line[6]) 
            colunms['quote asset volume'].append(line[7]) 
            colunms['number of trades'].append(line[8]) 
            colunms['taker buy base asset volume'].append(line[9]) 
            colunms['taker buy quote asset volume'].append(line[10]) 
            colunms['ignore'].append(line[11])
       
        self.df = pd.DataFrame(data=colunms)    

def updateClosePrices(handler, new_price):
    
    try:
        handler.readCSV("close.csv")
        array = handler.df['close'].values.tolist()
        array = array[1:]
        array.append(new_price)
        
        handler.df = pd.DataFrame({'close': array})
        handler.parseCSV("close.csv")
        
    except FileNotFoundError:
        raise FileNotFoundError("Failed to found 'close.csv' file")
    except KeyError:
        raise KeyError("No 'close' colunm in 'close.csv'")
    
def getClosePricesNegativeVariationsMean(df):
    
    try:
        close_prices = df['close'].values
    except KeyError as e:
        raise KeyError("No 'close' colunm")
        return 0.0
    
    erlier_price = float(close_prices[0]);
    
    sum_variations = 0;
    total_variations = 0;
    
    for price in close_prices:
        
        current_price = float(price)
        
        variation = current_price/erlier_price - 1.0
        
        if (variation < 0.0):
            sum_variations += variation
            total_variations += 1
        
        erlier_price = current_price
         
        
    return sum_variations/total_variations
    
def refit5digits(number):
    return round(number, 5)
        
    