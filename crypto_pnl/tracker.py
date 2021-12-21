from .core import *
from .asset import Asset, zero_asset
from .position import Position, Positions


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
        self.unpaid_fees = []
        self.last_transaction_index = -1

    def begin_transaction(self):
        print('BEGIN:    {}'.format(self.symbol))
        self.last_transaction_index = len(self.matched)

    def end_transaction(self):
        print('END:      {}'.format(self.symbol))

    def acquire(self, asset):
        print(' ACQUIRE: {}'.format(asset))
        matched, remaining = self.match(asset, self.dispose_stack, SIGN_BUY)
        self.matched.extend(matched)
        if remaining:
            self.acquire_stack.append(remaining)

    def dispose(self, asset):
        print(' DISPOSE: {}'.format(asset))
        matched, remaining = self.match(asset, self.acquire_stack, SIGN_SELL)
        self.matched.extend(matched)
        if remaining:
            self.dispose_stack.append(remaining)

    def pay_fee(self, asset):
        print(' PAY FEE: {}'.format(asset))
        # NOTE Fee is different than dispose as dispose is our earning while fee
        # is our cost. We have to do matching, because in order to pay fee we
        # had to acquire asset for it, and now we need to remove quantity from
        # that asset without creating gains. We don't need to track relationship
        # between fees and transactions, because when we pay fee we remove
        # quantity from acquired asset, and when we dispose of this asset the
        # gain will only include earning on what we disposed minus cost of the
        # asset with fee deducted.  Binance has Convert small amounts to BNB
        # option, and if that is not taken into account, then fees in BNB
        # currency may cause negative balance of BNB.  This is tracked by unpaid
        # fees.
        matched, remaining = self.match(asset, self.acquire_stack, 0)
        self.matched.extend(matched)
        if remaining:
            print('  UNPAID FEE: {}'.format(remaining))
            self.unpaid_fees.append(remaining)

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
            print('  MATCH:  {} ({} - {} = {} {})'.format(match,
                display_fiat(sell.value_data),
                display_fiat(buy.value_data),
                display_fiat(sell.value_data - buy.value_data), FIAT_SYMBOL)
            )
            matched.append((buy, sell, fee))
        if remaining:
            print('  CARRY:  {} ({} {})'.format(remaining,
            display_fiat(remaining.value_data), FIAT_SYMBOL))
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
