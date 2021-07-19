from .core import *
from .position import (
    Position,
    Positions
)

class Summary:
    def __init__(self):
        self.total = Positions()
        self.total_value = Position(FIAT_SYMBOL)

    def calculate(self, accounts):
        for name, position in accounts.positions.items():
            result = self.total.get(position.symbol, position.symbol)
            result.total_acquire += position.total_acquire
            result.total_dispose += position.total_dispose
    
    def add_fees(self, fees):
        for symbol, fee in fees.pockets.items():
            result = self.total.get(symbol, symbol)
            result.total_dispose += fee
    
    def add_ballances(self, ballances):
        for symbol, ballance in ballances.pockets.items():
            result = self.total.get(symbol, symbol)
            if ballance.quantity < 0:
                result.total_dispose -= ballance
            else:
                result.total_acquire += ballance

    def calculate_total_value(self):
        for k, v in self.total.positions.items():
            self.total_value.total_acquire.quantity += v.total_acquire.value
            self.total_value.total_dispose.quantity += v.total_dispose.value
        self.total_value.total_acquire.set_value(self.total_value.total_acquire.quantity)
        self.total_value.total_dispose.set_value(self.total_value.total_dispose.quantity)

    def __str__(self):
        total_value = Positions()
        total_value.positions['SUMMARY'] = self.total_value
        return '{}\n{}\n{}\n{}'.format(
                Positions.headers_str(),
                self.total, line_summary(), total_value)

