#!/bin/sh

INPUT_DIR1=$1
INPUT_DIR2=$2

INPUT_MARKET_DATA_DIR1=$INPUT_DIR1/logs/market_data
INPUT_MARKET_DATA_DIR2=$INPUT_DIR2/logs/market_data

if [ ! -e $INPUT_DIR1 ]
then
    echo "No such directory $INPUT_DIR1"
    exit 1
fi

if [ ! -e $INPUT_DIR2 ]
then
    echo "No such directory $INPUT_DIR2"
    exit 1
fi

echo Comparing trade logs
diff $INPUT_DIR2/trades.csv $INPUT_DIR1/trades.csv | head -n5

echo Comparing ledgers
diff $INPUT_DIR2/ledger.csv $INPUT_DIR1/ledger.csv | head -n5

echo Comparing trackers
diff $INPUT_DIR2/pnl-matching.csv $INPUT_DIR1/pnl-matching.csv

echo Comparing prices
diff $INPUT_DIR2/prices.csv $INPUT_DIR1/prices.csv | head -n5

for f in $(ls $INPUT_MARKET_DATA_DIR1)
do
    echo Comparing market data for: $f
    diff $INPUT_MARKET_DATA_DIR2/$f $INPUT_MARKET_DATA_DIR1/$f | head -n5
done

echo "If no differences are present, then all is good"
