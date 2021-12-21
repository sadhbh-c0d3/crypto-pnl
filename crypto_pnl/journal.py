from .core import *
from .position import Positions
from .tracker import Trackers


class Journal:
    def __init__(self, wallet):
        self.main = Positions()
        self.traded = Positions()
        self.all = Positions()
        self.trackers = Trackers()
        self.wallet = wallet
    
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
        
        position_main = self.main.get(trade.pair, trade.amount.symbol)
        position_traded = self.traded.get(trade.pair, trade.executed.symbol)

        position_all_main = self.all.get(trade.amount.symbol, trade.amount.symbol)
        position_all_traded = self.all.get(trade.executed.symbol, trade.executed.symbol)
        position_all_fee = self.all.get(trade.fee.symbol, trade.fee.symbol)

        tracker_main = self.trackers.get(trade.amount.symbol, trade.amount.symbol)
        tracker_traded = self.trackers.get(trade.executed.symbol, trade.executed.symbol)
        tracker_fee = self.trackers.get(trade.fee.symbol, trade.fee.symbol)

        fee_in_pair = tracker_fee.symbol in [tracker_main.symbol, tracker_traded.symbol]
        tracker_main.begin_transaction()
        tracker_traded.begin_transaction()
        if not fee_in_pair:
            tracker_fee.begin_transaction()

        if trade.side == SIGN_SELL:
            position_main.acquire(trade.amount)
            position_all_main.acquire(trade.amount)
            tracker_main.acquire(trade.amount)
        else:
            position_traded.acquire(trade.executed)
            position_all_traded.acquire(trade.executed)
            tracker_traded.acquire(trade.executed)

        position_all_fee.pay_fee(trade.fee)
        tracker_fee.pay_fee(trade.fee)

        if trade.side == SIGN_SELL:
            position_traded.dispose(trade.executed)
            position_all_traded.dispose(trade.executed)
            tracker_traded.dispose(trade.executed)
        else:
            position_main.dispose(trade.amount)
            position_all_main.dispose(trade.amount)
            tracker_main.dispose(trade.amount)

        tracker_main.end_transaction()
        tracker_traded.end_transaction()
        if not fee_in_pair:
            tracker_fee.end_transaction()

