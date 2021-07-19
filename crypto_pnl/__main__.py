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

from .aux import (
    walk_trades, 
    export_trades
)


def main():
    cmd, path = sys.argv[1:]
    if cmd == 'walk':
        walk_trades(path)
    elif cmd == 'export':
        export_trades(path)


if __name__ == '__main__':
    main()