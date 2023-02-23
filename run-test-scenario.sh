#!/bin/sh

SCENARIO_DIR=$1
INPUT_DIR=$SCENARIO_DIR/input
OUTPUT_DIR=$SCENARIO_DIR/output
EXPECTED_OUTPUT_DIR=$SCENARIO_DIR/expected

if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

mkdir -p $OUTPUT_DIR/market_data

python3 -m crypto_pnl export-tracker-events-fifo $INPUT_DIR > $OUTPUT_DIR/tracker-fifo.csv
python3 -m crypto_pnl export-trades $INPUT_DIR > $OUTPUT_DIR/trades.csv
python3 -m crypto_pnl export-ledger $INPUT_DIR > $OUTPUT_DIR/ledger.csv
python3 -m crypto_pnl export-prices $INPUT_DIR $OUTPUT_DIR/market_data > $OUTPUT_DIR/prices.csv

diff -u $OUTPUT_DIR/tracker-fifo.csv $EXPECTED_OUTPUT_DIR/tracker-fifo.csv
diff -u $OUTPUT_DIR/trades.csv $EXPECTED_OUTPUT_DIR/trades.csv
diff -u $OUTPUT_DIR/ledger.csv $EXPECTED_OUTPUT_DIR/ledger.csv
diff -u $OUTPUT_DIR/prices.csv $EXPECTED_OUTPUT_DIR/prices.csv

for f in $(ls $OUTPUT_DIR/market_data)
do
    diff $OUTPUT_DIR/market_data/$f $EXPECTED_OUTPUT_DIR/market_data/$f | head -n5
done