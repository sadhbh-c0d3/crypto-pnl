from .core import *
from .asset import Asset


class Position:
    """
    Position computed as disposals less acquisitions
    """
    def __init__(self, symbol):
        self.total_acquire = 0
        self.total_dispose = 0
        self.total_fee = 0
        self.symbol = symbol
    
    def acquire(self, asset):
        self.total_acquire += asset.quantity
    
    def dispose(self, asset):
        self.total_dispose += asset.quantity
    
    def pay_fee(self, asset):
        self.total_fee += asset.quantity
    
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

