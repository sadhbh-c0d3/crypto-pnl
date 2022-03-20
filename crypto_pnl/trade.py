# MIT License
#
# Copyright (c) 2021 Sadhbh Code
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .core import *
from .asset import *


# And example of trade data 
#
# - Trades exported from Binance Isolated Margin, Cross Margin, and Spot account
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


def load_trades(path):
    trades_csv = load_csv(path)
    header = next(trades_csv)
    for row in trades_csv:
        try:
            yield Trade(*row)
        except Exception as err:
            print err, row
            raise


def use_trade_streams(trade_streams):
    combined_trades = combine_data_streams(trade_streams, use_reverse=True)
    for which_stream, next_trade in combined_trades:
        yield next_trade


