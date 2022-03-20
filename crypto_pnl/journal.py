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

