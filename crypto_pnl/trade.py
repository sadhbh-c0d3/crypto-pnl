from .core import *
from .asset import *


# And example of trade data 
#
# - exported trades from Binance Isolated Margin account
#
# NOTE Trades exported from Binance Spot account need to be manually converted into this format.
# Additionally any other exported conversions need to be converted into this format.
#
# Date(UTC),Pair,Side,Price,Executed,Amount,Fee
# 2021-06-05 16:36:56,DOGEEUR,BUY,0.31031,500DOGE,155.15500000EUR,0.5DOGE
# 2021-06-07 16:02:28,DOGEBTC,SELL,0.00001006,200.0000000000DOGE,0.00201200BTC,0.0000020100BTC


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
            'Transaction: {:4} {:16} {:5} ({} EUR)'.format(
                get_side(self.side), 
                display(self.executed.quantity), 
                self.executed.symbol, 
                self.executed.value_str
            ),
            'Unit Price:           {:16} {:5}'.format(
                display(self.price),
                self.amount.symbol
            ),
            (
                'Consideration:    {:16}'.format(self.amount)
                    if self.side == SIGN_SELL else
                'Cost:             {:16}'.format(self.amount)
            ),
            'Fee:              {:16}'.format(self.fee),
            'Conversion Rate:         1.0 {:5} @ {:16} {}'.format(
                self.exchange_symbol,
                display(self.exchange_rate),
                FIAT_SYMBOL)
            ))


def load_trades(path):
    trades_csv = load_csv(path)
    header = next(trades_csv)
    for row in trades_csv:
        try:
            yield Trade(*row)
        except Exception as err:
            print err, row
            raise
