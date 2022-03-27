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
from .asset import *


# And example of trade data
#
# - Ledger entries exported from Binance Transaction History
#
# User_ID,UTC_Time,Account,Operation,Coin,Change,Remark
# 174740576,2021-06-05 16:36:56,Spot,Buy,DOGE,500.00000000,""
# 174740576,2021-06-06 09:13:51,IsolatedMargin,IsolatedMargin repayment,USDT,-6.83500000,""
# 174740576,2021-06-06 10:31:17,CrossMargin,Margin Repayment,SOL,-0.00100021,""


class LedgerEntry:
    def __init__(self,
            userid, date, account, operation, coin, change, remark
        ):
        self.userid = userid
        self.date = get_datetime(date)
        self.account = account
        self.operation = operation
        self.change = Asset(change, coin)
        self.remark = remark


def shoud_ignore_ledger_entry(entry):
    return entry.account == 'Spot' and entry.operation in (
        'Transaction Related',
        'Buy',
        'Sell',
        'Fee')


def should_change_loan_balance(entry):
    return (
        entry.account == 'IsolatedMargin' and entry.operation in (
            'IsolatedMargin loan',
            'IsolatedMargin repayment')
        ) or (entry.account == 'CrossMargin' and entry.operation in (
            'Margin loan',
            'Margin Repayment'))


def load_ledger(path):
    ledger_csv = load_csv(path)
    header = next(ledger_csv)
    for row in ledger_csv:
        try:
            yield LedgerEntry(*row)
        except Exception as err:
            print err, row
            raise

def use_ledger_streams(ledger_streams):
    combined_ledgers = combine_data_streams(ledger_streams)
    for which_stream, next_ledger in combined_ledgers:
        yield next_ledger