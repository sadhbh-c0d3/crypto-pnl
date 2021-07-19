from .core import *
from .asset import *


class Trade:
    def __init__(self, 
            date, pair, side, price, executed, amount, fee
        ):
        self.date = date
        self.pair = pair
        self.side = parse_side(side)
        self.price = parse_price(price)
        self.executed = parse_asset(executed)
        self.amount = parse_asset(amount)
        self.fee = parse_asset(fee)
        self.set_asset_values()

    def set_asset_values(self):
        main_rank = get_asset_rank(self.amount.symbol)
        traded_rank = get_asset_rank(self.executed.symbol)
        if main_rank < traded_rank:
            self.set_asset_values_from_main()
        else:
            self.set_asset_values_from_traded()

    def set_asset_values_from_main(self):
        exchange_rate = get_exchange_rate(self.date, self.amount.symbol)
        value = convert(self.amount.quantity, exchange_rate)
        self.amount.set_value(value)
        self.executed.set_value(value)
        fee = (self.fee.quantity 
                    if self.fee.symbol == self.amount.symbol
                    else self.price * self.fee.quantity)
        self.fee.set_value(convert(fee, exchange_rate))
        self.exchange_rate = exchange_rate
        self.exchange_symbol = self.amount.symbol
    
    def set_asset_values_from_traded(self):
        exchange_rate = get_exchange_rate(self.date, self.executed.symbol)
        value = convert(self.executed.quantity, exchange_rate)
        self.executed.set_value(value)
        self.amount.set_value(value)
        fee = (self.fee.quantity 
                    if self.fee.symbol == self.executed.symbol
                    else self.fee.quantity / self.price)
        self.fee.set_value(convert(fee, exchange_rate))
        self.exchange_rate = exchange_rate
        self.exchange_symbol = self.executed.symbol
    
    def __str__(self):
        return '\n'.join((
            'Date:        {}'.format(self.date),
            'Pair:        {}'.format(self.pair),
            'Transaction: {:4} {:16} {:5} ({} EUR) @ {:16} {:5}'.format(
                get_side(self.side), 
                display(self.executed.quantity), 
                self.executed.symbol, 
                self.executed.value_str,
                display(self.price),
                self.amount.symbol),
            'Cost:             {:16}'.format(self.amount),
            'Fee:              {:16}'.format(self.fee),
            'Conversion:       {:5} @ {:16} EUR'.format(
                self.exchange_symbol, 
                display(self.exchange_rate)
            )))


def load_trades(path):
    trades_csv = load_csv(path)
    header = next(trades_csv)
    for row in trades_csv:
        try:
            yield Trade(*row)
        except Exception as err:
            print err, row
            raise
