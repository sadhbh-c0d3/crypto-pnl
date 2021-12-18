from .core import *


class Wallet:
    def __init__(self):
        self.pockets = {}
    
    def add(self, pocket, amount, multiplier=1):
        position = amount * multiplier
        if pocket in self.pockets:
            self.pockets[pocket] += position
        else:
            self.pockets[pocket] = position

    def sub(self, pocket, amount, multiplier=1):
        return self.add(pocket, amount, -multiplier)

    def get_subset(self, pockets):
        subset = Wallet()
        for pocket in pockets:
            subset.pockets[pocket] = self.pockets[pocket]
        return subset
    
    def __str__(self):
        return '\n'.join('{:10} {}'.format(k, v)
            for k,v in sorted_items(self.pockets))

