from .core import *


class Asset:
    def __init__(self, quantity, symbol):
        self.quantity = Decimal(quantity)
        self.symbol = symbol

    def set_value(self, val):
        self.value = Decimal(val)

    @property
    def has_value(self):
        return hasattr(self, 'value')
    
    def __mul__(self, scalar):
        result = Asset(self.quantity * scalar, self.symbol)
        if self.has_value:
            result.value = self.value * scalar
        return result
    
    def __neg__(self):
        return self.__mul__(Decimal(-1))
    
    def __add__(self, other):
        result = Asset(self.quantity + other.quantity, self.symbol)
        if self.has_value and other.has_value:
            result.value = self.value + other.value
        return result
    
    def __sub__(self, other):
        result = Asset(self.quantity - other.quantity, self.symbol)
        if self.has_value and other.has_value:
            result.value = self.value - other.value
        return result
    
    def split(self, quantity):
        total_quantity = self.quantity
        self.quantity -= quantity
        other = Asset(quantity, self.symbol)
        if self.has_value:
            unit_value = self.value / total_quantity
            self.value = convert(self.quantity, unit_value)
            other.set_value(convert(quantity, unit_value))
        return other
    
    @property
    def value_str(self):
        if self.has_value:
            return '{:10}'.format(display_fiat(self.value))
        else:
            return '     ???'

    def __str__(self):
        return '{:16} {:5} ({:10} {:3})'.format(
            display(self.quantity), self.symbol, 
            self.value_str, FIAT_SYMBOL)
        

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

