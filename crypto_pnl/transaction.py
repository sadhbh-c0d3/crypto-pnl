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
from .tracker import Tracker, Trackers
from .ledger import should_change_loan_balance


class TransactionLeg:
    def __init__(self, tracker):
        self.base_tracker = tracker
        self.tracker = tracker.branch()

    def commit(self):
        self.base_tracker.merge(self.tracker)


class Transaction:
    def __init__(self, entry):
        self.entry = entry
        self.legs = []

    def get_leg(self, tracker):
        try:
            return next(x for x in self.legs if x.base_tracker is tracker)
        except StopIteration:
            leg = TransactionLeg(tracker)
            self.legs.append(leg)
            return leg

    def commit(self):
        for leg in self.legs:
            leg.commit()

    @property
    def trackers(self):
        trackers = Trackers()
        trackers.trackers = {
            x.tracker.symbol: x.tracker for x in self.legs
        }
        return trackers


class TransactionEngine:
    def __init__(self):
        self.trackers = Trackers()

    def get_tracker(self, symbol):
        return self.trackers.get(symbol, symbol)

    def get_transaction_leg(self, transaction, symbol):
        tracker = self.get_tracker(symbol)
        return transaction.get_leg(tracker)

    def execute(self, trade):
        transaction = Transaction(trade)

        main_leg = self.get_transaction_leg(transaction, trade.amount.symbol)
        traded_leg = self.get_transaction_leg(transaction, trade.executed.symbol)
        fee_leg = self.get_transaction_leg(transaction, trade.fee.symbol)

        if trade.side == SIGN_SELL:
            main_leg.tracker.acquire(trade.amount)
        else:
            traded_leg.tracker.acquire(trade.executed)

        fee_leg.tracker.pay_fee(trade.fee)

        if trade.side == SIGN_SELL:
            traded_leg.tracker.dispose(trade.executed)
        else:
            main_leg.tracker.dispose(trade.amount)

        transaction.commit()
        return transaction

    def process_ledger_entry(self, entry):
        transaction = Transaction(entry)

        leg = self.get_transaction_leg(transaction, entry.change.symbol)

        if should_change_loan_balance(entry):
            leg.tracker.loan(entry.change)

        elif entry.change.quantity > 0:
            leg.tracker.acquire(entry.change)

        elif entry.change.quantity < 0:
            change = copy_asset(entry.change)
            change.quantity = -change.quantity
            change.value_data = -change.value_data
            leg.tracker.dispose(change)

        transaction.commit()
        return transaction
