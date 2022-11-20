#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

if [ ! -e $OUTPUT_DIR ]
then
    mkdir -p $OUTPUT_DIR
fi

python3 -m crypto_pnl export-tracker-events-fifo $INPUT_DIR > $OUTPUT_DIR/tracker-fifo.csv
python3 -m crypto_pnl export-trades $INPUT_DIR > $OUTPUT_DIR/trades.csv
python3 -m crypto_pnl export-ledger $INPUT_DIR > $OUTPUT_DIR/ledger.csv
python3 -m crypto_pnl export-prices $INPUT_DIR > $OUTPUT_DIR/prices.csv
