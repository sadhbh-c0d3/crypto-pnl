from .core import *
from .asset import Asset, zero_asset
from .position import Position, Positions


class TransactionLeg:
    def __init__(self, symbol):
        self.symbol = symbol
        self.acquire_stack = []
        self.dispose_stack = []
        self.matched = []
        self.unpaid_fees = []


class Transaction:
    def __init__(self, trade):
        self.trade = trade
        self.legs = {
            symbol: TransactionLeg(symbol) for symbol in {
                trade.executed.symbol,
                trade.amount.symbol,
                trade.fee.symbol }
            }