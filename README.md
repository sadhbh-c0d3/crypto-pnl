# crypto-pnl
Crypto Trading Realized PnL Calculation (in EUR)

## Rationale
Jurisdictions require calculation of the PnL and CGT based off that as per transation basis.

This simple program is trying to do calculations based off Binance Isolated Margin Trading Data.

In order to use it correctly all other trades need to be converted into Isolated Margin Trading Data CSV file format.

## Status
UNDER DEVELOPMENT

There is lots of things to be done here:
 - Correct calculation of the gains in EUR
 - Conversion from other CSV file formats
 - Direct API data sourcing
 - Perhaps parse blockchain to get all data required

## Current Goal
CGT calculation MUST work correctly before end of October 2021.

## Commands

### Walk interactively through transactions
```
    python -m crypto_pnl walk ../crypto/trades_all.csv
```

### Export as CSV with valuation per transaction in Fiat currency
```
    python -m crypto_pnl export ../crypto/trades_all.csv
``` 
