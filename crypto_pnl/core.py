import csv
import re

from decimal import Decimal


INCH_RE = re.compile('(?P<quantity>[0-9.]+)1INCH')
MONETARY_RE = re.compile('(?P<quantity>[0-9.]+)(?P<symbol>[A-Z]*)')

ZERO_LEVEL = Decimal('0.0000000001')
QUANTIZER_1 = Decimal('0.0000001')
QUANTIZER_2 = Decimal('0.001')
LINE_LENGTH = 122
FIAT_SYMBOL = 'EUR'
INCH_SYMBOL = '1INCH'
SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'
SIGN_BUY = 1
SIGN_SELL = -1


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


def get_exchange_rate(date, symbol):
    # TODO: Feed from market data
    if symbol == 'EUR':
        return Decimal(1.0)
    if symbol == 'BUSD':
         return Decimal(unconvert(1.0, 1.1921))
    if symbol == 'USDT':
         return Decimal(unconvert(1.0, 1.192))
    if symbol == 'BNB':
         return Decimal(256.13)
    if symbol == 'BTC':
         return Decimal(28480.0)
    raise ValueError(symbol)


def parse_side(side):
    return Decimal(
        SIGN_SELL 
            if side == SIDE_SELL else 
        SIGN_BUY)


def get_side(quantity):
    return SIDE_SELL if quantity < 0 else SIDE_BUY


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

