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
from .asset import Asset, copy_asset


class Position:
    """
    Position computed as disposals less acquisitions
    """
    def __init__(self, symbol):
        self.total_acquire = Decimal(0)
        self.total_dispose = Decimal(0)
        self.total_fee = Decimal(0)
        self.symbol = symbol
    
    def acquire(self, asset):
        self.total_acquire = (self.total_acquire + asset.quantity).quantize(ZERO_LEVEL)
    
    def dispose(self, asset):
        self.total_dispose = (self.total_dispose + asset.quantity).quantize(ZERO_LEVEL)
    
    def pay_fee(self, asset):
        self.total_fee = (self.total_fee + asset.quantity).quantize(ZERO_LEVEL)
    
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

    def process_ledger_entry(self, entry):
        total_position = self.all.get(entry.change.symbol, entry.change.symbol)
        if entry.change.quantity > 0:
            total_position.acquire(entry.change)

        elif entry.change.quantity < 0:
            change = copy_asset(entry.change)
            change.quantity = -change.quantity
            change.value_data = -change.value_data
            total_position.dispose(change)
