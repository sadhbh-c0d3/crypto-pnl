import csv
import re

from decimal import Decimal
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

INCH_RE = re.compile('(?P<quantity>[0-9.]+)1INCH')
MONETARY_RE = re.compile('(?P<quantity>[0-9.]+)(?P<symbol>[A-Z]*)')

ZERO_LEVEL = Decimal('0.0000000001')

QUANTIZER_1 = Decimal('0.0000001')
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

LINE_LENGTH = 110


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


def parse_side(side):
    return Decimal(
        SIGN_SELL 
            if side == SIDE_SELL else 
        SIGN_BUY)


def get_side(quantity):
    return SIDE_SELL if quantity < 0 else SIDE_BUY


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
    if abs(quantity) < ZERO_LEVEL:
        return Decimal(0)
    if abs(quantity) < 1:
        return quantity.quantize(QUANTIZER_1)
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
    return fit_line(t,'.')


def line_trade_summary():
    return fit_line('','-')


def line_summary():
    return fit_line('','=')


def combine_data_streams(data_streams):
    def next_or_none(it):
        try:
            return next(it)
        except StopIteration:
            return None
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

