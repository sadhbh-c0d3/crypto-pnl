from .core import *
from .position import Positions
from .tracker import Trackers
from .exchange_rates import exchange_rates


class Journal:
    def __init__(self, wallet, fees):
        self.main = Positions()
        self.traded = Positions()
        self.all = Positions()
        self.trackers = Trackers()
        self.wallet = wallet
        self.fees = fees
    
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
        exchange_rates.will_execute(trade)
        
        self.wallet.add(trade.executed.symbol, trade.executed, trade.side)
        self.wallet.sub(trade.amount.symbol, trade.amount, trade.side)

        self.wallet.sub(trade.fee.symbol, trade.fee)
        self.fees.add(trade.fee.symbol, trade.fee)
        
        position_main = self.main.get(trade.pair, trade.amount.symbol)
        position_traded = self.traded.get(trade.pair, trade.executed.symbol)

        position_all_main = self.all.get(trade.amount.symbol, trade.amount.symbol)
        position_all_traded = self.all.get(trade.executed.symbol, trade.executed.symbol)

        tracker_main = self.trackers.get(trade.amount.symbol, trade.amount.symbol)
        tracker_traded = self.trackers.get(trade.executed.symbol, trade.executed.symbol)

        if trade.side == SIGN_SELL:
            position_traded.dispose(trade.executed)
            position_all_traded.dispose(trade.executed)
            tracker_traded.dispose(trade.executed)

            position_main.acquire(trade.amount)
            position_all_main.acquire(trade.amount)
            tracker_main.acquire(trade.amount)
        else:
            position_main.dispose(trade.amount)
            position_all_main.dispose(trade.amount)
            tracker_main.dispose(trade.amount)

            position_traded.acquire(trade.executed)
            position_all_traded.acquire(trade.executed)
            tracker_traded.acquire(trade.executed)
    

