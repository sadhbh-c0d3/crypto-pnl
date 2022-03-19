from .core import *


class Journal:
    def __init__(self, wallet, position_tracker, transaction_engine):
        self.wallet = wallet
        self.position_tracker = position_tracker
        self.transaction_engine = transaction_engine
        self.transactions = []
    
    @property
    def last_transaction(self):
        return self.transactions[-1]

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
        self.wallet.execute(trade)
        self.position_tracker.execute(trade)
        self.transactions.append(self.transaction_engine.execute(trade))

    def process_ledger_entry(self, entry):
        self.wallet.process_ledger_entry(entry)
        self.position_tracker.process_ledger_entry(entry)
        self.transactions.append(self.transaction_engine.process_ledger_entry(entry))

