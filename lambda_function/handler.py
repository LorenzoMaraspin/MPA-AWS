from utility import get_config
from bybitApi import BybitApi
from bybitModel import BybitModel
from aws_lambda_powertools import Logger

logger = Logger()

def lambda_handler(event, context):
    config = get_config(event)
    main(config)
    return 0

def main(config):
    # DEFINE BYBIT MODEL and API objects
    btc_model = BybitModel(config)
    bybit_client = BybitApi(config)

    # GET WALLET BALANCE
    wallet = bybit_client.get_wallet_balance()
    btc_model.calculate_qty_based_on_balance(wallet)

    # CHECK if there are OPEN POSITION to close BEFORE to OPEN NEW POSITION
    position = bybit_client.get_position_info()
    if position['side']:
        side = 'Sell' if position['side'] == 'Buy' else 'Buy'
        bybit_client.close_position(side)

    # OPEN NEW POSITION based on the EVENT received and SET TAKEPROFIT and STOPLOSS
    bybit_client.open_position(btc_model._qty)
    btc_model.choose_tp_sl_strategy(bybit_client)


