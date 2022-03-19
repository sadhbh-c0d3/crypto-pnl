from .core import *
from .asset import Asset, zero_asset, copy_asset
from .position import Position, Positions
from .tracker import Tracker, Trackers


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

        if entry.change.quantity > 0:
            leg.tracker.acquire(entry.change)

        elif entry.change.quantity < 0:
            change = copy_asset(entry.change)
            change.quantity = -change.quantity
            change.value_data = -change.value_data
            leg.tracker.dispose(change)

        transaction.commit()
        return transaction
