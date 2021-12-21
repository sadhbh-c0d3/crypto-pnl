from .core import *
from .position import Positions
from .tracker import Trackers
from .transaction import Transaction


class Journal:
    def __init__(self, wallet):
        self.main = Positions()
        self.traded = Positions()
        self.all = Positions()
        self.trackers = Trackers()
        self.wallet = wallet
        self.transactions = []
    
    def execute(self, trade):
        """
        Execute trade

        Perform exchange of assets:
            - Acquire/Dispose of Traded Asset
            - Dispose/Acquire of Main Asset
        
        TODO:
            - Asset value needs to be remembered when acquired, and 
            - Gains need to be calculated as value at disposal 
                less value at aqcuisition, and
            - Value is estimated at best effort, using Fiat currency (EUR)
            - Fiat value of Fees need to be remembered for each transaction
        
        See Also:
            Share Matching Rules:
                https://www.whitefieldtax.co.uk/cgt-share-matching-rules-worked-example/
        """
        self.wallet.add(trade.executed.symbol, trade.executed, trade.side)
        self.wallet.sub(trade.amount.symbol, trade.amount, trade.side)

        self.wallet.sub(trade.fee.symbol, trade.fee)
        
        main_pair_position = self.main.get(trade.pair, trade.amount.symbol)
        traded_pair_position = self.traded.get(trade.pair, trade.executed.symbol)

        main_total_position = self.all.get(trade.amount.symbol, trade.amount.symbol)
        main_tracker = self.trackers.get(trade.amount.symbol, trade.amount.symbol)

        traded_total_position = self.all.get(trade.executed.symbol, trade.executed.symbol)
        traded_tracker = self.trackers.get(trade.executed.symbol, trade.executed.symbol)

        fee_total_position = self.all.get(trade.fee.symbol, trade.fee.symbol)
        fee_tracker = self.trackers.get(trade.fee.symbol, trade.fee.symbol)

        transaction = Transaction(trade)

        main_tracker.begin(transaction)
        traded_tracker.begin(transaction)

        if fee_tracker not in (main_tracker, traded_tracker):
            fee_tracker.begin(transaction)

        if trade.side == SIGN_SELL:
            main_pair_position.acquire(trade.amount)
            main_total_position.acquire(trade.amount)
            main_tracker.acquire(trade.amount)
        else:
            traded_pair_position.acquire(trade.executed)
            traded_total_position.acquire(trade.executed)
            traded_tracker.acquire(trade.executed)

        fee_total_position.pay_fee(trade.fee)
        fee_tracker.pay_fee(trade.fee)

        if trade.side == SIGN_SELL:
            traded_pair_position.dispose(trade.executed)
            traded_total_position.dispose(trade.executed)
            traded_tracker.dispose(trade.executed)
        else:
            main_pair_position.dispose(trade.amount)
            main_total_position.dispose(trade.amount)
            main_tracker.dispose(trade.amount)

        main_tracker.commit()
        traded_tracker.commit()

        if fee_tracker not in (main_tracker, traded_tracker):
            fee_tracker.commit()

        self.transactions.append(transaction)

