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
python3 -m crypto_pnl export-tracker-events-fifo $OUTPUT_LOGS_DIR > $OUTPUT_DIR/tracker-fifo.csv


# Step 3. Validate results (optional)

OUTPUT_TEMP_DIR=$OUTPUT_DIR/temp
OUTPUT_MARKET_DATA_TEMP_DIR=$OUTPUT_TEMP_DIR/$MARKET_DATA_DIR

mkdir -p $OUTPUT_TEMP_DIR
mkdir -p $OUTPUT_MARKET_DATA_TEMP_DIR

# Step 3a. Generate reports from original data
python3 -m crypto_pnl export-trades $INPUT_DIR > $OUTPUT_TEMP_DIR/trades.csv
python3 -m crypto_pnl export-ledger $INPUT_DIR > $OUTPUT_TEMP_DIR/ledger.csv
python3 -m crypto_pnl export-tracker-events-fifo $INPUT_DIR > $OUTPUT_TEMP_DIR/tracker-fifo.csv

# Step 3b. Generate market data from sparse market data (should not be any different)
python3 -m crypto_pnl export-prices $OUTPUT_LOGS_DIR $OUTPUT_MARKET_DATA_TEMP_DIR > $OUTPUT_TEMP_DIR/prices.csv

# Step 3c. Compare results

echo Comparing trade logs
diff $OUTPUT_TEMP_DIR/trades.csv $OUTPUT_DIR/trades.csv | head -n5

echo Comparing ledgers
diff $OUTPUT_TEMP_DIR/ledger.csv $OUTPUT_DIR/ledger.csv | head -n5

echo Comparing trackers
diff $OUTPUT_TEMP_DIR/tracker-info.csv $OUTPUT_DIR/tracker-info.csv

echo Comparing prices
diff $OUTPUT_TEMP_DIR/prices.csv $OUTPUT_DIR/prices.csv | head -n5

for f in $(ls $OUTPUT_MARKET_DATA_DIR)
do
    echo Comparing market data for: $f
    diff $OUTPUT_MARKET_DATA_TEMP_DIR/$f $OUTPUT_MARKET_DATA_DIR/$f | head -n5
done

echo "If no differences are present, then all is good"
