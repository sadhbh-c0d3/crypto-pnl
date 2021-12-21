from .core import *
from .asset import Asset


class Wallet:
    def __init__(self):
        self.pockets = {}
    
    def add(self, pocket, amount, multiplier=1):
        quantity = amount.quantity * multiplier
        if pocket in self.pockets:
            assert self.pockets[pocket].symbol == amount.symbol

            self.pockets[pocket] = Asset(
                quantity + self.pockets[pocket].quantity, 
                self.pockets[pocket].symbol)
        else:
            self.pockets[pocket] = Asset(quantity, amount.symbol)

    def sub(self, pocket, amount, multiplier=1):
        return self.add(pocket, amount, -multiplier)

    def get_subset(self, pockets):
        subset = Wallet()
        for pocket in pockets:
            subset.pockets[pocket] = self.pockets[pocket]
        return subset
    
    def format_pocket(self, pocket, exchange_rate_calculator):
        asset = Asset(self.pockets[pocket].quantity, self.pockets[pocket].symbol)
        if exchange_rate_calculator:
            exchange_rate_calculator.set_asset_value(asset)
        return '{:10} |{:16} {:10}'.format(
            asset.symbol,
            display(asset.quantity), 
            asset.value_str
        )
    
    @classmethod
    def headers_str(cls):
        return '{:10} | {:16} {:10}'.format(
            '',
            '(QUANTITY)'.rjust(16), 
            '(VALUE)'.rjust(10))
    
    def valuated_str(self, exchange_rate_calculator):
        return '\n'.join([self.format_pocket(k, exchange_rate_calculator)
            for k,v in sorted_items(self.pockets)])

    def __str__(self):
        raise self.valuated_str(None)

