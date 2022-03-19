from .core import *


class ExchangeRateCalculator:
    """
    Track asset values based on last trade.

    We exchange through stablecoin: USDT, and then to EUR.
    The marketdata would be 5 minute klines, and is good for general conversion rate calculations,
    however to see gains on frequent transactions, we need to use pricing from traded market, i.e.
    Say we trade 1INCH/BTC, then for every single trade we have exact price in BTC what we pay (Buy)
    or receive (Sell). It wouldn't be accurate to use 1INCH price from market data (5 minute klines),
    so we price 1INCH as the amount we paid/received in BTC, and then we use BTC/USDT market data to
    convert to USDT, and then we use EUR/USDT market data to convert to EUR.
    """
    def __init__(self, last_price_provider):
        self.last_price_provider = last_price_provider
        self.last_prices = {}

    def get_exchange_rate(self, symbol):
        if symbol == FIAT_SYMBOL:
            return Decimal(1.0)
        fiat_price = self.last_price_provider.get_last_price(FIAT_SYMBOL, FIAT_EXCHANGE_SYMBOL)
        if symbol == FIAT_EXCHANGE_SYMBOL:
            return Decimal(1.0) / fiat_price
        symbol_price = self.last_price_provider.get_last_price(symbol, FIAT_EXCHANGE_SYMBOL)
        if symbol_price is not None:
            return symbol_price / fiat_price

    def set_asset_value(self, asset):
        unit_value = self.last_prices.get(asset.symbol)
        if not unit_value:
            unit_value = self.get_exchange_rate(asset.symbol)
        if unit_value:
            asset.set_value(convert(asset.quantity, unit_value), CURRENT_VALUE)
    
    def will_execute(self, trade):
        self._set_trade_assets_value(trade)
        self._set_last_trade(trade)

    # private:
    
    def _set_last_trade(self, trade):
        if trade.exchange_symbol == trade.amount.symbol:
            main_unit_value = trade.exchange_rate
            traded_unit_value = main_unit_value * trade.price
        else:
            traded_unit_value = trade.exchange_rate
            main_unit_value = traded_unit_value / trade.price

        self.last_prices[trade.amount.symbol] = main_unit_value
        self.last_prices[trade.executed.symbol] = traded_unit_value

    def _set_trade_assets_value(self, trade):
        self.last_price_provider.play_market_data_until(trade.date)

        main_rank = get_asset_rank(trade.amount.symbol)
        traded_rank = get_asset_rank(trade.executed.symbol)
        if main_rank < traded_rank:
            self._set_trade_assets_value_from_main(trade)
        else:
            self._set_trade_assets_value_from_traded(trade)

    def _set_trade_assets_value_from_main(self, trade):
        exchange_rate = self.get_exchange_rate(trade.amount.symbol)
        value = convert(trade.amount.quantity, exchange_rate)
        trade.amount.set_value(value, get_main_value_type(trade.side))
        trade.executed.set_value(value, get_traded_value_type(trade.side))
        trade.exchange_rate = exchange_rate
        trade.exchange_symbol = trade.amount.symbol
        if trade.fee.symbol == trade.amount.symbol:
            trade.fee.set_value(
                convert(trade.fee.quantity, exchange_rate),
                FEE_VALUE
            )
        elif trade.fee.symbol == trade.executed.symbol:
            trade.fee.set_value(
                convert(
                    convert(trade.fee.quantity, trade.price), 
                    exchange_rate),
                FEE_VALUE)
        else:
            fee_exchange_rate = self.get_exchange_rate(trade.fee.symbol)
            trade.fee.set_value(convert(trade.fee.quantity, fee_exchange_rate), FEE_VALUE)
    
    def _set_trade_assets_value_from_traded(self, trade):
        exchange_rate = self.get_exchange_rate(trade.executed.symbol)
        value = convert(trade.executed.quantity, exchange_rate)
        trade.executed.set_value(value, get_traded_value_type(trade.side))
        trade.amount.set_value(value, get_main_value_type(trade.side))
        trade.exchange_rate = exchange_rate
        trade.exchange_symbol = trade.executed.symbol
        if trade.fee.symbol == trade.executed.symbol:
            trade.fee.set_value(
                convert(trade.fee.quantity, exchange_rate), 
                FEE_VALUE
            )
        elif trade.fee.symbol == trade.amount.symbol:
            trade.fee.set_value(
                convert(
                    unconvert(trade.fee.quantity, trade.price), 
                    exchange_rate),
                FEE_VALUE)
        else:
            fee_exchange_rate = self.get_exchange_rate(trade.fee.symbol)
            trade.fee.set_value(convert(trade.fee.quantity, fee_exchange_rate), FEE_VALUE)
    
