from .core import *


class Asset:
    def __init__(self, quantity, symbol):
        self.quantity = Decimal(quantity)
        self.symbol = symbol

    def set_value(self, value_data, value_type):
        self.value_data = Decimal(value_data)
        self.value_type = value_type

    @property
    def has_value(self):
        return hasattr(self, 'value_data')
    
    def split(self, quantity):
        total_quantity = self.quantity
        self.quantity -= quantity
        other = Asset(quantity, self.symbol)
        if self.has_value:
            unit_value = self.value_data / total_quantity
            self.value_data = convert(self.quantity, unit_value)
            other.set_value(convert(quantity, unit_value), self.value_type)
        return other
    
    @property
    def value_str(self):
        if self.has_value:
            return '{:10}'.format(display_fiat(self.value_data))
        else:
            return '{:10}'.format(0)

    def __str__(self):
        return '{:16} {:5}'.format( display(self.quantity), self.symbol)
        

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
