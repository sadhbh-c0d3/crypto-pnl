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
from .trade import load_trades, use_trade_streams
from .ledger import load_ledger, use_ledger_streams, shoud_ignore_ledger_entry
from .market_data import load_market_data
from .wallet import Wallet
from .journal import Journal
from .position import Positions, PositionTracker
from .transaction import TransactionEngine
from .tracker import Trackers
from .last_prices import LastPrices
from .exchange_rate_calculator import ExchangeRateCalculator
from .console_report import ConsoleReport


def walk_trades(trades_paths, ledger_paths, market_data_paths):
    last_prices = LastPrices()
    exchange_rate_calculator = ExchangeRateCalculator(last_prices)
    wallet = Wallet()
    position_tracker = PositionTracker()
    transaction_engine = TransactionEngine()
    journal = Journal(wallet, position_tracker, transaction_engine)

    last_prices.set_market_data_streams(
        map(load_market_data, market_data_paths))

    ledgers = use_ledger_streams(
        map(load_ledger, ledger_paths))

    trades = use_trade_streams(
        map(load_trades, trades_paths))

    command = None
    filter_pair = None
    filter_traded = None
    filter_main = None
    filter_asset = None

    print('Transaction listing tool')
    print('''
    Available filter commands with example argument:
        pair DOGEBTC
        traded DOGE
        main BTC
        asset DOGE

    Press Enter to continue without filter...
    ''')
    command = raw_input('T> ')
    if command.startswith('pair'):
        filter_pair = command[len('pair '):]
        print('Listing transactions for pair {}'.format(filter_pair))
    if command.startswith('traded'):
        filter_traded = command[len('traded '):]
        print('Listing transactions for traded {}'.format(filter_traded))
    if command.startswith('main'):
        filter_main = command[len('main '):]
        print('Listing transactions for main {}'.format(filter_main))
    if command.startswith('asset'):
        filter_asset = command[len('asset '):]
        print('Listing transactions for asset {}'.format(filter_asset))

    print('''
    Available commands during listing:
        run
        quit

    Press Enter to walk transactions step by step...
    ''')
    command = raw_input('T> ')

    options = {}
    report = ConsoleReport(exchange_rate_calculator, options)

    number = 0
    for which, entry in combine_data_streams([trades, ledgers]):
        if not which:
            number += 1
            trade = entry
            exchange_rate_calculator.will_execute(trade)
            journal.execute(trade)
            if filter_pair and trade.pair != filter_pair:
                continue
            if filter_traded and trade.executed.symbol != filter_traded:
                continue
            if filter_main and trade.amount.symbol != filter_main:
                continue
            if filter_asset and filter_asset not in (
                    trade.amount.symbol, trade.executed.symbol):
                continue
            if command == 'run':
                continue
            report.print_trade_summary(number, trade, journal)
            command = raw_input('T> ')
            if command == 'quit':
                return

        else:
            if shoud_ignore_ledger_entry(entry):
                continue

            exchange_rate_calculator.will_process_ledger_entry(entry)
            journal.process_ledger_entry(entry)


    print '(No more trades.)'
    print('''
    Available commands:
        quit

    Press Enter to continue to summary...
    ''')
    command = raw_input('\nT> ')
    if command == 'quit':
        return
    report.print_final_summary(journal)


