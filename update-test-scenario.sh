#!/bin/sh

SCENARIO_DIR=$1
INPUT_DIR=$SCENARIO_DIR/input
EXPECTED_OUTPUT_DIR=$SCENARIO_DIR/expected

if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

mkdir -p $EXPECTED_OUTPUT_DIR/market_data

python3 -m crypto_pnl export-tracker-events-fifo $INPUT_DIR > $EXPECTED_OUTPUT_DIR/tracker-fifo.csv
python3 -m crypto_pnl export-trades $INPUT_DIR > $EXPECTED_OUTPUT_DIR/trades.csv
python3 -m crypto_pnl export-ledger $INPUT_DIR > $EXPECTED_OUTPUT_DIR/ledger.csv
python3 -m crypto_pnl export-prices $INPUT_DIR $EXPECTED_OUTPUT_DIR/market_data > $EXPECTED_OUTPUT_DIR/prices.csv

