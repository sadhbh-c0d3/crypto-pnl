from .core import *


class ExchangeRates:
    """
    Track asset values based on last trade.
    """
    def __init__(self):
        self.last_market_data = {}
        self.exchange_rates = {}

    def set_market_data_streams(self, market_data_streams):
        combined_market_data = combine_data_streams(market_data_streams)
        self.market_data_iter = iter(combined_market_data)
        self.market_data_current = None
        self.market_data_next = None
    
    def play_market_data_until(self, date):
        while True:
            which_stream, self.market_data_next = next(self.market_data_iter)
            if date < self.market_data_next.date:
                break
            key = (
                self.market_data_next.symbol_traded,
                self.market_data_next.symbol_main)
            self.last_market_data[key] = self.market_data_next
            self.market_data_current = self.market_data_next
    
    def get_exchange_rate(self, symbol):
        return get_fixed_exchange_rate(symbol)

    def set_asset_value(self, asset):
        unit_value = self.exchange_rates.get(asset.symbol)
        if unit_value:
            asset.set_value(convert(asset.quantity, unit_value))
    
    def will_execute(self, trade):
        self.set_trade_assets_value(trade)
        self.set_last_trade(trade)
    
    def set_last_trade(self, trade):
        if trade.exchange_symbol == trade.amount.symbol:
            main_unit_value = trade.exchange_rate
            traded_unit_value = main_unit_value * trade.price
        else:
            traded_unit_value = trade.exchange_rate
            main_unit_value = traded_unit_value / trade.price

        self.exchange_rates[trade.amount.symbol] = main_unit_value
        self.exchange_rates[trade.executed.symbol] = traded_unit_value

    def set_trade_assets_value(self, trade):
        self.play_market_data_until(trade.date)

        main_rank = get_asset_rank(trade.amount.symbol)
        traded_rank = get_asset_rank(trade.executed.symbol)
        if main_rank < traded_rank:
            self.set_trade_assets_value_from_main(trade)
        else:
            self.set_trade_assets_value_from_traded(trade)

    def set_trade_assets_value_from_main(self, trade):
        exchange_rate = self.get_exchange_rate(trade.amount.symbol)
        value = convert(trade.amount.quantity, exchange_rate)
        trade.amount.set_value(value)
        trade.executed.set_value(value)
        fee = (trade.fee.quantity 
                    if trade.fee.symbol == trade.amount.symbol
                    else trade.price * trade.fee.quantity)
        trade.fee.set_value(convert(fee, exchange_rate))
        trade.exchange_rate = exchange_rate
        trade.exchange_symbol = trade.amount.symbol
    
    def set_trade_assets_value_from_traded(self, trade):
        exchange_rate = self.get_exchange_rate(trade.executed.symbol)
        value = convert(trade.executed.quantity, exchange_rate)
        trade.executed.set_value(value)
        trade.amount.set_value(value)
        fee = (trade.fee.quantity 
                    if trade.fee.symbol == trade.executed.symbol
                    else trade.fee.quantity / trade.price)
        trade.fee.set_value(convert(fee, exchange_rate))
        trade.exchange_rate = exchange_rate
        trade.exchange_symbol = trade.executed.symbol
    

exchange_rates = ExchangeRates()

