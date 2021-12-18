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

from .aux import (
    walk_trades, 
    export_trades
)


def get_paths(path):
    trades_path, = glob.glob(os.path.join(path, 'trades.csv'))
    market_data_path = glob.glob(os.path.join(path, 'market_data/*.csv'))
    return trades_path, market_data_path


def main():
    cmd, path = sys.argv[1:]
    paths = get_paths(path)
    if cmd == 'walk':
        walk_trades(*paths)
    elif cmd == 'export':
        export_trades(*paths)


if __name__ == '__main__':
    main()
