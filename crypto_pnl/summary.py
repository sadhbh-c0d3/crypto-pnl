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
            result.total_acquire += position.total_acquire
            result.total_dispose += position.total_dispose
            result.total_fee += position.total_fee
    
    def valuated_str(self, exchange_rate_calculator):
        return '{}\n{}'.format(
                Positions.headers_str(),
                self.total.valuated_str(exchange_rate_calculator))

    def __str__(self):
        raise ValueError

