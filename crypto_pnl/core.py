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

import csv
import re

from decimal import Decimal
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

INCH_RE = re.compile('(?P<quantity>[0-9.]+)1INCH')
MONETARY_RE = re.compile('(?P<quantity>[0-9.]+)(?P<symbol>[A-Z]*)')

ZERO_LEVEL = Decimal('0.00000001')

QUANTIZER_1 = Decimal('0.000001')
QUANTIZER_2 = Decimal('0.001')

FIAT_QUANTIZER = Decimal('0.001')
FIAT_SYMBOL = 'EUR'
FIAT_EXCHANGE_SYMBOL = 'USDT'

INCH_SYMBOL = '1INCH'

SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'

SIGN_BUY = 1
SIGN_SELL = -1

CURRENT_VALUE = 'value'
ACQUIRE_VALUE = 'cost'
DISPOSE_VALUE = 'earn'
FEE_VALUE = 'fee'
GAIN_VALUE = 'gain'

MATCH_EVENT = 'Close'
CARRY_EVENT = 'Open'

BUY_MATCH_ACTION = ('Acquire', 'Buy',  'Close', 'Short') # We went short earlier when we sold asset, so this buy covers that borrowing
SELL_MATCH_ACTION = ('Dispose', 'Sell', 'Close', 'Long') # Sell assets that we own
PAY_FEE_MATCH_ACTION = ('Dispose', 'Fee', 'Close', 'Long') # We just pay fee with assets we own
REPAY_FEE_MATCH_ACTION = ('Acquire', 'Fee', 'Close', 'Short') # We went short earlier when we paid fee, so this buy covers that borrowing

STACK_CARRY_ACTION = ('Acquire', 'Buy', 'Open', 'Long') # Buy assets
BORROW_CARRY_ACTION = ('Dispose', 'Sell', 'Open', 'Short') # Sell borrowed asset
UNPAID_FEE_CARRY_ACTION = ('Dispose', 'Fee', 'Open', 'Short') # Pay fee using borrowed asset

ACQUIRE_ACTION = 'Acquire'
DISPOSE_ACTION = 'Dispose'
PAY_FEE_ACTION = 'Pay Fee'

TRACKER_FIFO = 0
TRACKER_LIFO = -1

LINE_LENGTH = 110


def die(message):
    raise ValueError(message)


def get_asset_rank(symbol):
    if symbol == 'EUR':
        return 1
    if symbol == 'USDT':
         return 2
    if symbol == 'BTC':
         return 3
    if symbol == 'BNB':
         return 4
    if symbol == 'BUSD':
         return 5
    return 1000


def get_datetime(date):
    return datetime.strptime(date, DATE_FORMAT)


def get_datetime_from_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp/1000.0)


def parse_side(side):
    return Decimal(
        SIGN_SELL 
            if side == SIDE_SELL else 
        SIGN_BUY)


def get_side(quantity):
    return SIDE_SELL if quantity < 0 else SIDE_BUY


def get_main_action(side):
    return DISPOSE_ACTION if side != SIGN_SELL else ACQUIRE_ACTION


def get_traded_action(side):
    return DISPOSE_ACTION if side == SIGN_SELL else ACQUIRE_ACTION


def get_carry_action(action):
    return (
        BORROW_CARRY_ACTION if action == SELL_MATCH_ACTION else (
        STACK_CARRY_ACTION if action == BUY_MATCH_ACTION else (
        UNPAID_FEE_CARRY_ACTION if action == PAY_FEE_MATCH_ACTION else
        die("It's impossible! Pay can only open short position and never long!"))))


def get_main_value_type(sign):
    return (
        DISPOSE_VALUE 
            if sign == SIGN_BUY else 
        ACQUIRE_VALUE)


def get_traded_value_type(sign):
    return (
        ACQUIRE_VALUE 
            if sign == SIGN_BUY else 
        DISPOSE_VALUE)


def convert(quantity, rate):
    return (quantity * rate)


def unconvert(quantity, rate):
    return (quantity / rate)


def display(quantity):
    if quantity is None:
        return Decimal(0)
    if abs(quantity) < QUANTIZER_1:
        return Decimal(0)
    if abs(quantity) < 1:
        return quantity.quantize(QUANTIZER_1)
    else:
        return quantity.quantize(QUANTIZER_2)


def display_fiat(quantity):
    return quantity.quantize(FIAT_QUANTIZER)


def load_csv(path):
    with open(path) as fp:
        return csv.reader(fp.readlines())

def sorted_items(d):
    return sorted(d.items(), key=lambda x:x[0])


def fit_line(t, c):
    s = len(c)
    n = len(t)
    m = LINE_LENGTH - n
    m /= s
    k = m / 2
    m -= k
    return '{}{}{}'.format(c * k, t, c * m)


def line_title(t):
    return fit_line(t,'=')


def line_section(t):
    return fit_line(t,'-')


def line_trade_summary():
    return fit_line('','-')


def line_summary():
    return fit_line('','=')


def combine_data_streams(data_streams, use_reverse=False, use_sort=False):
    def next_or_none(it):
        try:
            return next(it)
        except StopIteration:
            return None
    if use_reverse:
        data_streams = map(lambda s: reversed(list(s)), data_streams)
    if use_sort:
        data_streams = map(lambda s: sorted(list(s), key=lambda x: x.date), data_streams)
    iters = map(iter, data_streams)
    current = map(next_or_none, iters)
    while not all(x is None for x in current):
        next_i = None
        for (i, it) in enumerate(iters):
            if (current[i] is None):
                continue
            if (next_i is None or current[i].date < current[next_i].date):
                next_i = i
        yield (next_i, current[next_i])
        current[next_i] = next_or_none(iters[next_i])

