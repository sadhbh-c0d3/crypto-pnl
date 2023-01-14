#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

LEDGER_DIR=ledger
TRADES_DIR=trades
MARKET_DATA_DIR=market_data

OUTPUT_LOGS_DIR=$OUTPUT_DIR/logs

INPUT_LEDGER_DIR=$INPUT_DIR/$LEDGER_DIR
INPUT_TRADES_DIR=$INPUT_DIR/$TRADES_DIR
INPUT_MARKET_DATA_DIR=$INPUT_DIR/$MARKET_DATA_DIR

OUTPUT_LEDGER_DIR=$OUTPUT_LOGS_DIR/$LEDGER_DIR
OUTPUT_TRADES_DIR=$OUTPUT_LOGS_DIR/$TRADES_DIR
OUTPUT_MARKET_DATA_DIR=$OUTPUT_LOGS_DIR/$MARKET_DATA_DIR


if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

# Step 1. Create output directories
mkdir -p $OUTPUT_DIR
mkdir -p $OUTPUT_LEDGER_DIR
mkdir -p $OUTPUT_TRADES_DIR
mkdir -p $OUTPUT_MARKET_DATA_DIR

# Step 2. Copy ledger and trading logs, and filter makret data
cp $INPUT_LEDGER_DIR/* $OUTPUT_LEDGER_DIR/
cp $INPUT_TRADES_DIR/* $OUTPUT_TRADES_DIR/
python3 -m crypto_pnl export-prices $INPUT_DIR $OUTPUT_MARKET_DATA_DIR > $OUTPUT_DIR/prices.csv

# Step 3. Generate reports using sparse market data from Step 2.
python3 -m crypto_pnl export-trades $OUTPUT_LOGS_DIR > $OUTPUT_DIR/trades.csv
python3 -m crypto_pnl export-ledger $OUTPUT_LOGS_DIR > $OUTPUT_DIR/ledger.csv
python3 -m crypto_pnl export-tracker-events-fifo $OUTPUT_LOGS_DIR > $OUTPUT_DIR/pnl-matching.csv
