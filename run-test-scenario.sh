#!/bin/sh

SCENARIO_DIR=$1
INPUT_DIR=$SCENARIO_DIR/input
OUTPUT_DIR=$SCENARIO_DIR/output

if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

python3 -m crypto_pnl export-tracker-events-fifo $INPUT_DIR > $OUTPUT_DIR/tracker-fifo.csv
python3 -m crypto_pnl export-trades $INPUT_DIR > $OUTPUT_DIR/trades.csv
python3 -m crypto_pnl export-ledger $INPUT_DIR > $OUTPUT_DIR/ledger.csv
python3 -m crypto_pnl export-prices $INPUT_DIR > $OUTPUT_DIR/prices.csv
