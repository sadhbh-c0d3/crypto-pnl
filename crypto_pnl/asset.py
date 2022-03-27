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


class Asset:
    def __init__(self, quantity, symbol):
        self.quantity = Decimal(quantity).quantize(ZERO_LEVEL)
        self.symbol = symbol
        self.xid = -1

    def set_id(self, xid):
        self.xid = xid

    @property
    def has_id(self):
        return hasattr(self, 'xid')

    def set_value(self, value_data, value_type):
        self.value_data = Decimal(value_data).quantize(ZERO_LEVEL)
        self.value_type = value_type

    @property
    def has_value(self):
        return hasattr(self, 'value_data')
    
    def split(self, quantity):
        total_quantity = self.quantity
        self.quantity = (self.quantity - quantity).quantize(ZERO_LEVEL)
        other = Asset(quantity, self.symbol)
        if self.has_value:
            unit_value = self.value_data / total_quantity
            self.value_data = convert(self.quantity, unit_value).quantize(ZERO_LEVEL)
            other.set_value(convert(quantity, unit_value), self.value_type)
        if self.has_id:
            other.set_id(self.xid)
        return other


def zero_asset(symbol, value_type):
    asset = Asset(0, symbol)
    asset.set_value(0, value_type)
    asset.set_id(0)
    return asset


def copy_asset(asset):
    copy = Asset(asset.quantity, asset.symbol)
    if asset.has_value:
        copy.set_value(asset.value_data, asset.value_type)
    if asset.has_id:
        copy.set_id(asset.xid)
    return copy


def parse_price(price):
    price = price.replace(',','')
    return Decimal(price)


def parse_asset(quantity):
    quantity = quantity.replace(',','')
    g = INCH_RE.match(quantity)
    if g: # 1INCH is special, because it starts with digit
        return Asset(g.groups()[0], INCH_SYMBOL)
    g = MONETARY_RE.match(quantity).groups()
    if len(g) == 2 and g[1]:
        return Asset(*g)
    raise ValueError(quantity)

