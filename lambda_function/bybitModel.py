from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()

class BybitModel:
    def __init__(self, config):
        self._config = config
        self._order_type = self._config['bybit']['order_type']
        self._category = self._config['bybit']['category']
        self._symbol = self._config['bybit']['symbol']
        self._market_unit = self._config['bybit']['market_unit']
        self._is_leverage = self._config['bybit']['is_leverage']
        self._side = self._config['event']['side']
        self._price = self._config['event']['price']

    def calculate_tp_sl_trade(self, value, type_op):
        if type_op == 'tp':
            if self._side == 'Buy':
                result = f"{float(self._price) + (float(self._price) * value /100):.4f}"
            else:
                result = f"{float(self._price) - (float(self._price) * value / 100):.4f}"
        else:
            if self._side == 'Buy':
                result = f"{float(self._price) - (float(self._price) * value / 100):.4f}"
            else:
                result = f"{float(self._price) + (float(self._price) * value / 100):.4f}"

        logger.info(f"Defined: {type_op} value = {result}")

        return result

    def calculate_qty_based_on_balance(self, wallet_balance):
        balance = float(wallet_balance['coin'][0]['walletBalance'])
        leverage = int(self._config['bybit']['buy_leverage'])
        risk = float(self._config['bybit']['trade_size'])
        quantity = ((balance * risk) * leverage) / float(self._price)

        logger.append_keys(
            balance=balance,
            leverage=leverage,
            risk=risk,
            quantity=f"{quantity:.3f}"
        )
        logger.info("Calculated the quantity used to open a position")
        self._qty = f"{quantity:.3f}"

    def set_multiple_tp_sl(self, tp_sl_list):
        trade_tp_sl = []
        if not isinstance(tp_sl_list, list):
            logger.error(f"The list of tp provided it's not a list")
            raise TypeError

        for item in tp_sl_list:
            take_profit = self.calculate_tp_sl_trade(item['tp_percentage'], 'tp')
            stop_loss = self.calculate_tp_sl_trade(item['sl_percentage'], 'sl')
            size = f"{float(self._qty) * (float(item['size']) / 100):.3f}"
            trade_tp_sl.append({"take_profit": take_profit, "size": size, "stop_loss": stop_loss})
            logger.info(f"Defined trade tp/sl: {take_profit},{stop_loss},{size}")
        return trade_tp_sl

    def choose_tp_sl_strategy(self, bybit_api):
        operativity = self._config['bybit']['trading_management']
        if operativity == 'OPS-1':
            operativity_selected = self._config['ssm']['ops_1_value']
            ops_details = self.set_multiple_tp_sl(operativity_selected)
            for item in ops_details:
                bybit_api.set_tp_sl(item, 'Partial')
            logger.info(f"Selected operative type: OPS-1: {ops_details}")
        elif operativity == 'OPS-2':
            operativity_selected = self._config['ssm']['ops_2_value']
            ops_details = self.set_multiple_tp_sl(operativity_selected)
            for item in ops_details:
                bybit_api.set_tp_sl(item, 'Partial')
            logger.info(f"Selected operative type: OPS-2: {ops_details}")
        else:
            index = self._config['bybit']['trading_management_index']
            operativity_selected = self._config['ssm']['ops_2_value']
            ops_details = self.set_multiple_tp_sl(operativity_selected[index])
            bybit_api.set_tp_sl(ops_details[index], 'Full')
            logger.info(f"Selected operative type: OPS-3: {ops_details[index]}")