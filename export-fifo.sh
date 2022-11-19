#!/bin/sh

python3 -m crypto_pnl export-tracker-events-fifo ../data/raw_data > ../data/output/tracker-fifo.csv
python3 -m crypto_pnl export-trades ../data/raw_data > ../data/output/trades.csv
python3 -m crypto_pnl export-ledger ../data/raw_data > ../data/output/ledger.csv
python3 -m crypto_pnl export-prices ../data/raw_data > ../data/output/prices.csv
