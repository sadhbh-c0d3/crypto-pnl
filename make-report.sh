#!/bin/sh

INPUT_DIR=$1

if [ ! -e $INPUT_DIR ]
then
    echo "No such directory $INPUT_DIR"
    exit 1
fi

python3 ./join_csv.py $INPUT_DIR/report.xlsx \
    ./cgt-summary.csv \
    $INPUT_DIR/pnl-matching.csv \
    $INPUT_DIR/ledger.csv \
    $INPUT_DIR/trades.csv \
    $INPUT_DIR/prices.csv
