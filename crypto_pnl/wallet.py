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
    
    def execute(self, trade):
        self.add(trade.executed.symbol, trade.executed, trade.side)
        self.sub(trade.amount.symbol, trade.amount, trade.side)
        self.sub(trade.fee.symbol, trade.fee)

    def process_ledger_entry(self, entry):
        self.add(entry.change.symbol, entry.change)


