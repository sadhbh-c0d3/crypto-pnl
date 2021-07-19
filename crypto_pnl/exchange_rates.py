from .core import *


class ExchangeRates:
    """
    Track asset values based on last trade.
    """
    def __init__(self):
        self.exchange_rates = {}

    def set_last_trade(self, trade):
        if trade.exchange_symbol == trade.amount.symbol:
            main_unit_value = trade.exchange_rate
            traded_unit_value = main_unit_value * trade.price
        else:
            traded_unit_value = trade.exchange_rate
            main_unit_value = traded_unit_value / trade.price

        self.exchange_rates[trade.amount.symbol] = main_unit_value
        self.exchange_rates[trade.executed.symbol] = traded_unit_value

    def set_asset_value(self, asset):
        unit_value = self.exchange_rates.get(asset.symbol)
        if unit_value:
            asset.set_value(convert(asset.quantity, unit_value))
    

exchange_rates = ExchangeRates()