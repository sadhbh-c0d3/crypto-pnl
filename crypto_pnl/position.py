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


class PositionTracker:
    def __init__(self):
        self.main = Positions()
        self.traded = Positions()
        self.all = Positions()

    def execute(self, trade):
        main_pair_position = self.main.get(trade.pair, trade.amount.symbol)
        main_total_position = self.all.get(trade.amount.symbol, trade.amount.symbol)

        traded_pair_position = self.traded.get(trade.pair, trade.executed.symbol)
        traded_total_position = self.all.get(trade.executed.symbol, trade.executed.symbol)

        fee_total_position = self.all.get(trade.fee.symbol, trade.fee.symbol)

        if trade.side == SIGN_SELL:
            main_pair_position.acquire(trade.amount)
            main_total_position.acquire(trade.amount)
        else:
            traded_pair_position.acquire(trade.executed)
            traded_total_position.acquire(trade.executed)

        fee_total_position.pay_fee(trade.fee)

        if trade.side == SIGN_SELL:
            traded_pair_position.dispose(trade.executed)
            traded_total_position.dispose(trade.executed)
        else:
            main_pair_position.dispose(trade.amount)
            main_total_position.dispose(trade.amount)
