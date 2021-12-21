from .core import *
from .asset import Asset, zero_asset
from .position import Position, Positions


class Tracker:
    """
    Asset acquisition & disposal tracker

    Tracks asset disposals matching with acquisitions.
    Also matches acquisitions with loans.
    """
    def __init__(self, symbol):
        self.symbol = symbol
        self.acquire_stack = []
        self.dispose_stack = []
        self.matched = []
        self.unpaid_fees = []
        self.events = []

    def branch(self):
        tracker = Tracker(self.symbol)
        tracker.acquire_stack = self.acquire_stack[:]
        tracker.dispose_stack = self.dispose_stack[:]
        return tracker

    def merge(self, tracker):
        self.acquire_stack = tracker.acquire_stack[:]
        self.dispose_stack = tracker.dispose_stack[:]
        self.matched += tracker.matched
        self.unpaid_fees += tracker.unpaid_fees
        self.events += tracker.events

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

    def pay_fee(self, asset):
        matched, remaining = self.match(asset, self.acquire_stack, 0)
        self.matched.extend(matched)
        if remaining:
            self.unpaid_fees.append(remaining)

    def match(self, asset, stack, sign):
        matched = []
        zero_acquire = zero_asset(asset.symbol, ACQUIRE_VALUE)
        zero_fee = zero_asset(asset.symbol, FEE_VALUE)
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
            buy, sell, fee = (
                (borrowed, match, zero_fee) if sign == SIGN_SELL else (
                (match, borrowed, zero_fee) if sign == SIGN_BUY else
                (borrowed, zero_acquire, match))
            )
            matched.append((buy, sell, fee))
            self.events.append((MATCH_EVENT, get_match_action(sign), matched[-1]))
        if remaining:
            self.events.append((CARRY_EVENT, get_carry_action(sign), remaining))
        return matched, remaining

    def summary(self):
        tracker = Tracker(self.symbol)
        total_buy = 0
        total_sell = 0
        total_fee = 0
        total_acquire_cost = 0
        total_fee_cost = 0
        total_consideration = 0
        for buy, sell, fee in self.matched:
            total_buy += buy.quantity
            total_sell += sell.quantity
            total_fee += fee.quantity
            total_acquire_cost += buy.value_data
            total_consideration += sell.value_data
            total_fee_cost += fee.value_data
        buy = Asset(total_buy, self.symbol)
        sell = Asset(total_sell, self.symbol)
        fee = Asset(total_fee, self.symbol)
        buy.set_value(total_acquire_cost, ACQUIRE_VALUE)
        sell.set_value(total_consideration, DISPOSE_VALUE)
        fee.set_value(total_fee_cost, FEE_VALUE)
        tracker.matched.append((buy, sell, fee))
        return tracker

    def list_stacks(self):
        positions = []
        for asset in self.acquire_stack:
            position = Position(asset.symbol)
            position.total_acquire = asset.quantity
            positions.append(position)
        for asset in self.dispose_stack:
            position = Position(asset.symbol)
            position.total_dispose = asset.quantity
            positions.append(position)
        return positions

    def balance(self):
        position = Position(self.symbol)
        position.total_acquire = sum(asset.quantity for asset in self.acquire_stack)
        position.total_dispose = sum(asset.quantity for asset in self.dispose_stack)
        return position

    def unpaid_fees_balance(self):
        position = Position(self.symbol)
        position.total_dispose = sum(asset.quantity for asset in self.unpaid_fees)
        return position

    def has_unpaid_fees(self):
        return not not self.unpaid_fees


class Trackers:
    """
    A set of trackers by traded pair, account, or symbol

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

    def list_stacks(self):
        stacks = []
        for (pair, tracker) in self.trackers.items():
            stacks += tracker.list_stacks()
        return stacks

    def balance(self):
        balance = Positions()
        for (pair, tracker) in self.trackers.items():
            balance.positions[pair] = tracker.balance()
        return balance

    def unpaid_fees_balance(self):
        balance = Positions()
        for (pair, tracker) in self.trackers.items():
            unpaid_fees = tracker.unpaid_fees_balance()
            balance.positions[pair] = unpaid_fees
        return balance

    def has_unpaid_fees(self):
        return any(tracker.has_unpaid_fees()
            for tracker in self.trackers.values())

    def summary(self):
        summary = Trackers()
        for k,v in self.trackers.items():
           summary.trackers[k] = v.summary()
        return summary
