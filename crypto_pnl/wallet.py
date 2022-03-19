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


