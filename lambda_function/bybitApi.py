from pybit.unified_trading import HTTP
from aws_lambda_powertools import Logger

logger = Logger()

class BybitApi:
    def __init__(self, config):
        self._config = config
        self._env = True if self._config['lambda']['env'] == 'dev' else False
        self._session = HTTP(testnet=self._env,api_key=self._config['secret']['api_key'],api_secret=self._config['secret']['api_secret'])

    def get_wallet_balance(self):
        logger.info(f"Trying to get wallet balance details")
        try:
            response = self._session.get_wallet_balance(
                accountType=self._config['bybit']['account_type'],
                coin="USDT",
            )
            if response['retMsg'] == 'OK':
                logger.info(f"Wallet balance details received correctly: {response['retMsg']}")
                return response['result']['list'][0]

        except Exception as e:
            logger.info(f"Unable to get wallet balance details : {e}")
            raise e

    def get_position_info(self):
        logger.info(f"Trying to get open trade")
        try:
            response = self._session.get_positions(
                category=self._config['bybit']['category'],
                symbol=self._config['bybit']['symbol'],
            )
            logger.append_keys(
                category=self._config['bybit']['category'],
                symbol=self._config['bybit']['symbol'],
            )
            if response['retMsg'] == 'OK':
                result = response['result']['list'][0]
                return result
        except Exception as e:
            logger.error(f"Unable to get trade due: {e}")
            raise e


    def open_position(self, qty):
        logger.info(f"Trying to open trade: {self._config['event']['side']}")
        try:
            response = self._session.place_order(
                category=self._config['bybit']['category'],
                symbol=self._config['bybit']['symbol'],
                side=self._config['event']['side'],
                orderType=self._config['bybit']['order_type'],
                qty=qty,
                positionIdx=0,
                price=self._config['event']['price'],
                marketUnit=self._config['bybit']['market_unit'],
                reduceOnly=False
            )
            logger.append_keys(
                order_id=response['result']['orderId'],
                side=self._config['event']['side'],
                symbol=self._config['bybit']['symbol'],
                qty=qty
            )
            logger.info(f"Opened trade: {self._config['event']['side']}")
            return {"orderId": response['result']['orderId'], "timeStamp": response['time']}
        except Exception as e:
            logger.error(f"Unable to open trade due: {e}")
            raise e

    def close_position(self, side):
        logger.info(f"Trying to close trade: {side}")
        try:
            response = self._session.place_order(
                category=self._config['bybit']['category'],
                symbol=self._config['bybit']['symbol'],
                side=side,
                orderType=self._config['bybit']['order_type'],
                qty=0,
                positionIdx=0,
                marketUnit=self._config['bybit']['market_unit'],
                reduceOnly=True
            )
            logger.append_keys(
                order_id=response['result']['orderId'],
                side=side,
                symbol=self._config['bybit']['symbol'],
                qty=0
            )
            logger.info(f"Closed trade: {side}")
            return {"orderId": response['result']['orderId'], "timeStamp": response['time']}
        except Exception as e:
            logger.error(f"Unable to close trade due: {e}")

    def set_tp_sl(self, order, mode):
        logger.info(f"Trying to set TP/SL for order: {self._config['bybit']['symbol']}")
        try:
            response = self._session.set_trading_stop(
                category=self._config['bybit']['category'],
                symbol=self._config['bybit']['symbol'],
                takeProfit=order['take_profit'],
                stopLoss=order['stop_loss'],
                tpTriggerBy="MarkPrice",
                slTriggerB="MarkPrice",
                tpslMode=mode,
                tpSize=order['size'],
                slSize=order['size'],
                positionIdx=0
            )
            if response['retMsg'] == 'OK':
                logger.append_keys(
                    takeProfit=order['take_profit'],
                    stopLoss=order['stop_loss'],
                    tpslMode=mode,
                    tpSize=order['size'],
                    slSize=order['size'],
                )
                logger.info(f"Setted up TP/SL for position: {self._config['bybit']['symbol']}")
        except Exception as e:
            logger.info(f"Unable to set TP/SL details for position: {self._config['bybit']['symbol']}, {e}")
            raise e