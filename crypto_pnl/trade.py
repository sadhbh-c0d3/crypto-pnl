from .core import *
from .asset import *


class Trade:
    def __init__(self, 
            date, pair, side, price, executed, amount, fee
        ):
        self.date = get_datetime(date)
        self.pair = pair
        self.side = parse_side(side)
        self.price = parse_price(price)
        self.executed = parse_asset(executed)
        self.amount = parse_asset(amount)
        self.fee = parse_asset(fee)
    
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
