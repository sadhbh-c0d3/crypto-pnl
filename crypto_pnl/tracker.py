from .core import *
from .asset import Asset


class Tracker:
    """
    Asset disposal tracker

    Tracks asset disposals matching with acquisitions.
    Also matches acquisitions with loans.
    """
    def __init__(self, symbol):
        self.symbol = symbol
        self.acquire_stack = []
        self.dispose_stack = []
        self.matched = []
        self.last_transaction_index = 0
    
    def begin_transaction(self):
        self.last_transaction_index = len(self.matched)
    
    def acquire(self, asset):
        matched, remaining = self.match(asset, self.dispose_stack, SIGN_BUY)
        self.matched.extend(matched)
        if remaining:
            self.acquire_stack.append(remaining)
    
    def dispose(self, asset):
        matched, remaining = self.match(asset, self.acquire_stack, SIGN_SELL)
        self.matched.extend(matched)
        if remaining:
            self.dispose_stack.append(remaining)
    
    def match(self, asset, stack, sign):
        matched = []
        remaining = Asset(asset.quantity, asset.symbol)
        remaining.set_value(asset.value_data, asset.value_type)
        while stack and remaining:
            borrowed = stack[-1]
            if borrowed.quantity <= remaining.quantity:
                match = remaining.split(borrowed.quantity)
                stack.pop()
            else:
                borrowed = borrowed.split(remaining.quantity)
                match, remaining = remaining, None
            matched.append(
                (borrowed, match)
                    if sign == SIGN_SELL else 
                (match, borrowed) 
            )
        return matched, remaining

    @classmethod
    def headers_str(cls):
        return ' {} {}|  {} {} {} '.format(
            ' (ACQUIRED)'.rjust(16),
            ' (DISPOSED)'.rjust(16),
            ' (COST)'.rjust(10),
            ' (EARN)'.rjust(10), 
            ' (GAIN)'.rjust(10)
        )
    
    def summary(self):
        tracker = Tracker(self.symbol)
        total_buy = 0
        total_sell = 0
        total_cost = 0
        total_consideration = 0
        for buy, sell in self.matched:
            total_buy += buy.quantity
            total_sell += sell.quantity
            total_cost += buy.value_data
            total_consideration += sell.value_data
        buy = Asset(total_buy, self.symbol)
        sell = Asset(total_sell, self.symbol)
        buy.set_value(total_cost, ACQUIRE_VALUE)
        sell.set_value(total_consideration, DISPOSE_VALUE)
        tracker.matched.append((buy, sell))
        return tracker
    
    def format_match(self, match):
        buy, sell = match
        position = Asset(sell.quantity - buy.quantity, self.symbol)
        position.set_value(sell.value_data - buy.value_data, GAIN_VALUE)
        return '{:16} {:16} | {:10} {:10} {:10} '.format(
            display(buy.quantity), 
            display(sell.quantity), 
            buy.value_str.rjust(10), 
            sell.value_str.rjust(10), 
            position.value_str.rjust(10)
        )

    def __str__(self):
        return '\n'.join(map(self.format_match, self.matched))
    
    @property
    def last_transaction_str(self):
        return '\n'.join(map(self.format_match, self.matched[self.last_transaction_index:]))


class Trackers:
    """
    A set of trackers by traded pair

    When Isolated Margin trading, then same symbol exists in many traded pairs.
    Can be also used by symbol, then pair is symbol.
    """
    def __init__(self):
        self.trackers = {}

    def get(self, pair, symbol):
        return self.trackers.setdefault(
            pair, 
            Tracker(symbol))

    def get_subset(self, pairs):
        subset = Trackers()
        for pair in pairs:
            subset.trackers[pair] = self.trackers[pair]
        return subset
    
    def get_subset_rest(self, pairs):
        subset = Trackers()
        for pair in self.trackers:
            if pair in pairs:
                continue
            subset.trackers[pair] = self.trackers[pair]
        return subset
    
    def summary(self):
        summary = Trackers()
        for k,v in self.trackers.items():
           summary.trackers[k] = v.summary()
        return summary

    @classmethod
    def headers_str(cls):
        return '{:10} |{}'.format('', Tracker.headers_str())

    def __str__(self):
        return '\n'.join(
                '{:10} |{}'.format(k, v.format_match(m))
                for k,v in sorted_items(self.trackers)
                for m in v.matched)
    
    @property
    def last_transaction_str(self):
        return '\n'.join(
                '{:10} |{}'.format(k, v.format_match(m))
                for k,v in sorted_items(self.trackers)
                for m in v.matched[v.last_transaction_index:])

