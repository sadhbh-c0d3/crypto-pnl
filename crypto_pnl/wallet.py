from .core import *
from .asset import Asset
from .exchange_rates import exchange_rates


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
    
    def format_pocket(self, pocket):
        asset = Asset(self.pockets[pocket].quantity, self.pockets[pocket].symbol)
        exchange_rates.set_asset_value(asset)
        return '{:10} |{:16} {:10}'.format(
            asset.symbol,
            display(asset.quantity), 
            display_fiat(asset.value_data))
    
    @classmethod
    def headers_str(cls):
        return '{:10} | {:16} {:10}'.format(
            '',
            '(QUANTITY)'.rjust(16), 
            '(VALUE)'.rjust(10))
    
    def __str__(self):
        return '\n'.join([self.format_pocket(k)
            for k,v in sorted_items(self.pockets)])

