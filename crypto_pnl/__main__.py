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

"""
A simple tool that loads Binance CSV file in Isolated Margin format
and produces human friendly walk-through or csv with fiat valuation.

TODO:
Lots of things!
- Correct per-transaction gain in Fiat currency 
    (correct EUR values for CGT calculation)
- Conversion from other than Isolated Margin CSV file formats
- Access data directly via Binance API
    (instead of multiple CSV files)
- Process data directly from the blockchain
    (all transactions should appear on blockchain)
"""

import sys
import os
import glob

from .console_walk import walk_trades
from .csv_export import export_trades, export_tracker_events, export_ledger


def get_paths(path):
    trades_path = glob.glob(os.path.join(path, 'trades/*.csv'))
    ledger_path = glob.glob(os.path.join(path, 'ledger/*.csv'))
    market_data_path = glob.glob(os.path.join(path, 'market_data/*.csv'))
    return trades_path, ledger_path, market_data_path


def print_usage():
    print('''Crypto PnL Calculator (c) 2021, Sonia Sadhbh Kolasinska

usage: crypto_pnl <walk|export-trades|export-tracker-events|export-ledger> <path>
''')

def print_commands():
    print('''commands:
    walk    Walk through transaction log printing for each transaction
            the details of transaction, exchange rates, account balance,
            transaction gains, and transaction match and carry actions.
    
    export-trades
            Export into CSV file a preprocessed trading log, where
            trades are valuated in EUR using exchange rates driven by market data.

    export-tracker-events
            Export into CSV file a preprocessed trading log, where
            buys are matched against sells by matching engine
            and EUR gains are calculated using exchange rates driven by market data.

    export-tracker-events-fifo
            Same as export-tracker-events, but use FIFO matching instead of default LIFO.

    export-ledger
            Export into CSV file a preprocessed transactions log, where
            transactions are valuated in EUR using exchange rates driven by market data.

    ''')

def print_help():
    print_usage()
    print_commands()

def print_error(msg):
    print_usage()
    print('error: {}\n'.format(msg))
    print_commands()


def main():
    args = sys.argv[1:]
    if not args:
        print_usage()
        return

    cmd = args[0]
    if cmd in ('walk', 'export-trades', 'export-ledger',
            'export-tracker-events',
            'export-tracker-events-fifo'):
        path = args[1]
        paths = get_paths(path)
        if cmd == 'walk':
            walk_trades(*paths)
        elif cmd == 'export-trades':
            export_trades(*paths)
        elif cmd == 'export-tracker-events':
            export_tracker_events(*paths)
        elif cmd == 'export-tracker-events-fifo':
            export_tracker_events(*paths, use_fifo=True)
        elif cmd == 'export-ledger':
            export_ledger(*paths)
    elif cmd in ('help','-h'):
        print_help()
    else:
        print_error('Unknown command {}'.format(cmd))


if __name__ == '__main__':
    main()
