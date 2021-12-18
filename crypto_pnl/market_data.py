from .core import *
from .asset import *

# An example of market data
#
# - downloaded from https://www.CryptoDataDownload.com
# - edited to get only first 7 columns
# - and only some selected date range
#
# unix,date,symbol,open,high,low,close
# 1622851200000,2021-06-05 00:00:00,BNB/USDT,390.68,408.87,387.6,408
# 1622854800000,2021-06-05 01:00:00,BNB/USDT,408,414.76,404.76,411.66
# 1622858400000,2021-06-05 02:00:00,BNB/USDT,411.63,413.74,407.81,411.96
# 1622862000000,2021-06-05 03:00:00,BNB/USDT,411.97,415.73,408.85,410.17
# 1622865600000,2021-06-05 04:00:00,BNB/USDT,410.17,416,410.17,415.77
# 1622869200000,2021-06-05 05:00:00,BNB/USDT,415.78,417.24,412.84,415.35
# 1622872800000,2021-06-05 06:00:00,BNB/USDT,415.35,423.32,415.22,422.04

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
    
    @property
    def value(self):
        return (
            self.open_price + 
            self.close_price + 
            2 * (self.high_price + self.low_price)
        ) / 6

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
