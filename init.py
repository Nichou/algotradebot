from strategybot import *

api_key = '>>> API KEY<<<'
api_secret = '>>> API SECRET <<<'

initClient(api_key, api_secret)

btcb = BinanceClient("USDT", "BTC")
ethb = BinanceClient("USDT", "ETH")
bnbb = BinanceClient("USDT", "BNB")
xrpb = BinanceClient("USDT", "XRP")
solb = BinanceClient("USDT", "SOL")
trxb = BinanceClient("USDT", "TRX")

btcbot = StrategyBot(btcb)
ethbot = StrategyBot(ethb)
bnbbot = StrategyBot(bnbb)
xrpbot = StrategyBot(xrpb)
solbot = StrategyBot(solb)
trxbot = StrategyBot(trxb)

