from .core import *
from .asset import Asset
from .exchange_rates import exchange_rates


class Position:
    """
    Position computed as disposals less acquisitions
    """
    def __init__(self, symbol):
        self.total_acquire = Asset(0, symbol)
        self.total_dispose = Asset(0, symbol)
        self.total_acquire.set_value(0)
        self.total_dispose.set_value(0)
        self.symbol = symbol
    
    def acquire(self, asset):
        self.total_acquire += asset
    
    def dispose(self, asset):
        self.total_dispose += asset
    
    @classmethod
    def headers_str(cls):
        return ' {} {} {} {}|  {} {} '.format(
            ' (ACQUIRED)'.rjust(16), ' ({})'.format(FIAT_SYMBOL).rjust(10), 
            ' (DISPOSED)'.rjust(16), ' ({})'.format(FIAT_SYMBOL).rjust(10), 
            ' (POSITION)'.rjust(16), ' ({})'.format(FIAT_SYMBOL).rjust(10)
        )

    def __str__(self):
        position = self.total_acquire - self.total_dispose
        exchange_rates.set_asset_value(position)
        return '{:16} {:10} {:16} {:10} | {:16} {:10}  '.format(
            display(self.total_acquire.quantity), self.total_acquire.value_str, 
            display(self.total_dispose.quantity), self.total_dispose.value_str, 
            display(position.quantity), position.value_str
        )


class Positions:
    """
    A set of positions by traded pair
    
    When Isolated Margin trading, then same symbol exists in many traded pairs.
    Can be also used by symbol, then pair is symbol.
    """
    def __init__(self):
        self.positions = {}

    def get(self, pair, symbol):
        return self.positions.setdefault(
            pair, 
            Position(symbol))

    def get_subset(self, pairs):
        subset = Positions()
        for pair in pairs:
            subset.positions[pair] = self.positions[pair]
        return subset
    
    @classmethod
    def headers_str(cls):
        return '{:10} |{}'.format('', Position.headers_str())

    def __str__(self):
        return '\n'.join(
                '{:10} |{}'.format(k, v)
                for k,v in sorted_items(self.positions))

