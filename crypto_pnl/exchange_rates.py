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
            try:
                which_stream, self.market_data_next = next(self.market_data_iter)
                if date < self.market_data_next.date:
                    break
                key = (
                    self.market_data_next.symbol_traded,
                    self.market_data_next.symbol_main)
                self.last_market_data[key] = self.market_data_next
                self.market_data_current = self.market_data_next
            except StopIteration:
                break
    
    def get_exchange_rate(self, symbol):
        if symbol == FIAT_SYMBOL:
            return Decimal(1.0)
        fiat_to_exch = self.last_market_data[(FIAT_SYMBOL, FIAT_EXCHANGE_SYMBOL)]
        if symbol == FIAT_EXCHANGE_SYMBOL:
            return Decimal(1.0) / fiat_to_exch.value
        symbol_to_exch = self.last_market_data[(symbol, FIAT_EXCHANGE_SYMBOL)]
        symbol_to_fiat = symbol_to_exch.value / fiat_to_exch.value
        return symbol_to_fiat

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
        trade.exchange_rate = exchange_rate
        trade.exchange_symbol = trade.amount.symbol
        if trade.fee.symbol == trade.amount.symbol:
            trade.fee.set_value(
                convert(trade.fee.quantity, exchange_rate)
            )
        elif trade.fee.symbol == trade.executed.symbol:
            trade.fee.set_value(
                convert(
                    convert(trade.fee.quantity, trade.price), 
                    exchange_rate))
        else:
            fee_exchange_rate = self.get_exchange_rate(trade.fee.symbol)
            trade.fee.set_value(convert(trade.fee.quantity, fee_exchange_rate))
    
    def set_trade_assets_value_from_traded(self, trade):
        exchange_rate = self.get_exchange_rate(trade.executed.symbol)
        value = convert(trade.executed.quantity, exchange_rate)
        trade.executed.set_value(value)
        trade.amount.set_value(value)
        trade.exchange_rate = exchange_rate
        trade.exchange_symbol = trade.executed.symbol
        if trade.fee.symbol == trade.executed.symbol:
            trade.fee.set_value(
                convert(trade.fee.quantity, exchange_rate)
            )
        elif trade.fee.symbol == trade.amount.symbol:
            trade.fee.set_value(
                convert(
                    unconvert(trade.fee.quantity, trade.price), 
                    exchange_rate))
        else:
            fee_exchange_rate = self.get_exchange_rate(trade.fee.symbol)
            trade.fee.set_value(convert(trade.fee.quantity, fee_exchange_rate))
    

exchange_rates = ExchangeRates()


def get_asset_rank(symbol):
    if symbol == 'EUR':
        return 1
    if symbol == 'BUSD':
         return 2
    if symbol == 'USDT':
         return 3
    if symbol == 'BNB':
         return 4
    if symbol == 'BTC':
         return 5
    return 1000

