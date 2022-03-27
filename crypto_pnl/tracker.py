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
from .asset import Asset, zero_asset, copy_asset
from .position import Position, Positions


class Tracker:
    """
    Asset acquisition & disposal tracker

    Tracks asset disposals matching with acquisitions.
    Also matches acquisitions with loans.
    """
    TRACKER_DIR=TRACKER_LIFO

    def __init__(self, symbol):
        self.symbol = symbol
        self.acquire_stack = []
        self.dispose_stack = []
        self.loan_balance = Decimal('0.0')
        self.matched = []
        self.unpaid_fees = []
        self.events = []

    def branch(self):
        tracker = Tracker(self.symbol)
        tracker.acquire_stack = self.acquire_stack[:]
        tracker.dispose_stack = self.dispose_stack[:]
        tracker.unpaid_fees = self.unpaid_fees[:]
        tracker.loan_balance = self.loan_balance
        return tracker

    def merge(self, tracker):
        self.acquire_stack = tracker.acquire_stack[:]
        self.dispose_stack = tracker.dispose_stack[:]
        self.unpaid_fees = tracker.unpaid_fees[:]
        self.loan_balance = tracker.loan_balance
        self.matched += tracker.matched
        self.events += tracker.events

    def acquire(self, asset):
        if self.unpaid_fees:
            matched, asset = self.match(asset, self.unpaid_fees, REPAY_FEE_MATCH_ACTION)
            self.matched.extend(matched)
        if asset:
            matched, remaining = self.match(asset, self.dispose_stack, BUY_MATCH_ACTION)
            self.matched.extend(matched)
            if remaining:
                self.acquire_stack.append(remaining)

    def dispose(self, asset):
        matched, remaining = self.match(asset, self.acquire_stack, SELL_MATCH_ACTION)
        self.matched.extend(matched)
        if remaining:
            self.dispose_stack.append(remaining)

    def pay_fee(self, asset):
        matched, remaining = self.match(asset, self.acquire_stack, PAY_FEE_MATCH_ACTION)
        self.matched.extend(matched)
        if remaining:
            self.unpaid_fees.append(remaining)

    def loan(self, asset):
        loan_balance = self.loan_balance + asset.quantity
        if (self.loan_balance > 0) and (loan_balance < 0):
            # repayment
            released = asset.split(-loan_balance)
            self.loan_balance = Decimal(0.0)
            self.pay_fee(released)
        elif (self.loan_balance >= 0) and (loan_balance >= 0):
            # accumulated loan
            # NOTE: We cannot be accumulating repayments, because when we cross
            # zero we must release difference between the repayment and loan.
            # In cases when loans were exteded and then repayed in multiple
            # ledger entries, eventually we will cross 0, and at that point we
            # will release difference.
            self.loan_balance = loan_balance
        else:
            # We know that reordering ledger is less than optimal, especially if
            # loans are taken and repayed not instantly and not in full, but
            # this problem is too complex to solve it automatically, and human
            # input is necessary to avoid ambigouous situations. When loan entry
            # appears followed by more than one repayment entries, as a rule of
            # thumb make sure to put the biggest entry last. The released
            # diference is the interests we paid, so needs to be deducted as any
            # other fee (we call pay_fee() for that in the condition above).
            raise ValueError('Please, reorder ledger entries around {} {:.7f} {:.7f} {:.7f}'.format(
                asset.xid if asset.has_id else 'n/a', loan_balance, self.loan_balance, asset.quantity))


    def match(self, asset, stack, action):
        matched = []
        zero_acquire = zero_asset(asset.symbol, ACQUIRE_VALUE)
        zero_fee = zero_asset(asset.symbol, FEE_VALUE)
        remaining = copy_asset(asset)
        while stack and remaining:
            borrowed = stack[self.TRACKER_DIR]
            if borrowed.quantity <= remaining.quantity:
                match = remaining.split(borrowed.quantity)
                if not remaining.quantity:
                    remaining = None
                stack.pop(self.TRACKER_DIR)
            else:
                borrowed = borrowed.split(remaining.quantity)
                match, remaining = remaining, None
            buy, sell, fee = (
                (borrowed, match, zero_fee) if action == SELL_MATCH_ACTION else (
                (match, borrowed, zero_fee) if action == BUY_MATCH_ACTION else (
                (borrowed, zero_acquire, match) if action == PAY_FEE_MATCH_ACTION else
                (match, zero_acquire, borrowed)))
            )
            matched.append((copy_asset(buy), copy_asset(sell), copy_asset(fee)))
            self.events.append((MATCH_EVENT, action, matched[-1]))
        if remaining and (action != REPAY_FEE_MATCH_ACTION):
            self.events.append((CARRY_EVENT, get_carry_action(action), copy_asset(remaining)))
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
        position.total_fee = sum(asset.quantity for asset in self.unpaid_fees)
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
