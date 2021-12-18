from .core import *
from .asset import Asset
from .position import (
    Position,
    Positions
)

class Summary:
    def __init__(self):
        self.total = Positions()

    def calculate(self, accounts):
        for name, position in accounts.positions.items():
            result = self.total.get(position.symbol, position.symbol)
            result.total_acquire = Asset(
                result.total_acquire.quantity + position.total_acquire.quantity,
                position.symbol)
            result.total_dispose = Asset(
                result.total_dispose.quantity + position.total_dispose.quantity,
                position.symbol)
    
    def add_fees(self, fees):
        for symbol, fee in fees.pockets.items():
            result = self.total.get(symbol, symbol)
            result.total_dispose = Asset(
                result.total_dispose.quantity + fee.quantity, symbol)
    
    def add_ballances(self, ballances):
        for symbol, ballance in ballances.pockets.items():
            result = self.total.get(symbol, symbol)
            if ballance.quantity < 0:
                result.total_dispose = Asset(
                    result.total_dispose.quantity - ballance.quantity, 
                    symbol)
            else:
                result.total_acquire = Asset(
                    result.total_acquire.quantity + ballance.quantity, 
                    symbol)

    def __str__(self):
        return '{}\n{}'.format(
                Positions.headers_str(),
                self.total)

