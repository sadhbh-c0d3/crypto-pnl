#!/bin/sh

python3 -m crypto_pnl export-tracker-events-fifo ../data/raw_data > ../data/tracker-fifo.csv
python3 -m crypto_pnl export-trades ../data/raw_data > ../data/trades.csv
python3 -m crypto_pnl export-ledger ../data/raw_data > ../data/ledger.csv
python3 -m crypto_pnl export-prices ../data/raw_data > ../data/prices.csv
