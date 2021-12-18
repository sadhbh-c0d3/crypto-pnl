from .core import *
from .asset import *


class MarketData:
    def __init__(self,
            unix, date, symbol, open_price, high_price, low_price, close_price
        ):
        self.unix = unix
        self.date = get_datetime(date)
        (self.symbol_traded, self.symbol_main) = symbol.split('/')
        self.open_price = parse_price(open_price)
        self.high_price = parse_price(high_price)
        self.low_price = parse_price(low_price)
        self.close_price = parse_price(close_price)
    
    def info(self):
        return '\n'.join([
            'Date:           {}'.format(self.date),
            'Symbol(Main):   {}'.format(self.symbol_main),
            'Symbol(Traded): {}'.format(self.symbol_traded),
            'Open:           {}'.format(self.open_price),
            'High:           {}'.format(self.high_price),
            'Low:            {}'.format(self.low_price),
            'Close:          {}'.format(self.close_price),
        ])

    def __str__(self):
        return '{} {} / {}  {} {} {} {}'.format(
            self.date, 
            self.symbol_traded, 
            self.symbol_main,
            self.open_price,
            self.high_price,
            self.low_price,
            self.close_price)


def load_market_data(path):
    market_data_csv = load_csv(path)
    header = next(market_data_csv)
    for row in market_data_csv:
        try:
            yield MarketData(*row)
        except Exception as err:
            print err, row
            raise
