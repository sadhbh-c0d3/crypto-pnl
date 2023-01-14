#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

# Step 1. Create output directories
mkdir -p $OUTPUT_DIR
mkdir -p $OUTPUT_DIR/logs/market_data

# Step 2. Generate reports
python3 -m crypto_pnl export-trades $INPUT_DIR > $OUTPUT_DIR/trades.csv
python3 -m crypto_pnl export-ledger $INPUT_DIR > $OUTPUT_DIR/ledger.csv
python3 -m crypto_pnl export-tracker-events-fifo $INPUT_DIR > $OUTPUT_DIR/pnl-matching.csv

# Step 3. Generate prices and sparse market data
python3 -m crypto_pnl export-prices $INPUT_DIR $OUTPUT_DIR/logs/market_data > $OUTPUT_DIR/prices.csv
