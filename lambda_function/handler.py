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
    model = BybitModel(config)
    bybit_client = BybitApi(config)

    # GET WALLET BALANCE
    wallet = bybit_client.get_wallet_balance()
    model.calculate_qty_based_on_balance(wallet)
    model.choose_tp_sl_strategy(bybit_client)

    # SET POSITION MODE

    bybit_client.switch_margin_mode()
    bybit_client.set_leverage()
    bybit_client.switch_position_mode()
    # CHECK if there are OPEN POSITION to close BEFORE to OPEN NEW POSITION
    """position = bybit_client.get_position_info()
    if position['side'] and position['side'] != 'None':
        side = 'Sell' if position['side'] == 'Buy' else 'Buy'
        bybit_client.close_position(side)

    # OPEN NEW POSITION based on the EVENT received and SET TAKEPROFIT and STOPLOSS
    bybit_client.open_position(model._qty)
    model.choose_tp_sl_strategy(bybit_client)"""


