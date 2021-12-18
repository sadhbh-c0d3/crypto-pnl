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
        self.symbol = symbol
    
    def acquire(self, asset):
        self.total_acquire = Asset(
            self.total_acquire.quantity + asset.quantity,
            self.total_acquire.symbol)
    
    def dispose(self, asset):
        self.total_dispose = Asset(
            self.total_dispose.quantity + asset.quantity,
            self.total_dispose.symbol)
    
    @classmethod
    def headers_str(cls):
        return ' {} {}|  {} {}'.format(
            '(ACQUIRED)'.rjust(16), 
            '(DISPOSED)'.rjust(16), 
            '(POSITION)'.rjust(16),
            '(VALUE)'.rjust(10)
        )

    def __str__(self):
        position = Asset(self.total_acquire.quantity - self.total_dispose.quantity, self.symbol)
        exchange_rates.set_asset_value(position)
        return '{:16} {:16} | {:16} {:10}'.format(
            display(self.total_acquire.quantity),
            display(self.total_dispose.quantity),
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

