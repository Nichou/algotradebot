from BtcBot import *

api_key = '>>> API KEY <<<'
api_secret = '>>> API SECRET <<<'

initClient(api_key, api_secret)

btcb = BtcClient()
btcbot = BtcBot(btcb)

