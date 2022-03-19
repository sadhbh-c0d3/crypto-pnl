# crypto-pnl
Crypto Trading Realized PnL Calculation (in EUR)

## Rationale
Jurisdictions require calculation of the PnL and CGT based off that as per transation basis.

This simple program is trying to do calculations based off Binance Isolated Margin Trading Data.

In order to use it correctly all other trades need to be converted into Isolated Margin Trading Data CSV file format.

**Please follow instructions below in section *Data Download* to learn about how to _correctly_ download data from Binance**

### Matching Tansactions
The legal rules are described here [CGT share matching rules – a worked example](https://www.whitefieldtax.co.uk/cgt-share-matching-rules-worked-example/)

A matching engine uses multi-leg transaction trackers to match disposals against acquisitions.

A tracker remebers all acquisitions together with their prices in EUR estimated at the time of acquisition,
and then disposal with price in EUR estimated at the time of disposal.

Additionally tracker remembers the price in EUR of any fees at the time these fees arose. 

The short selling is supported, and covers matching of disposals of borrowed assets against following acquisitions. The EUR prices are estimated at the time of disposal and acquisition as previously. The fees may be covered by borrowed assets, since often fees are on traded asset, which we borrowed to sell it.

In all cases the gains are calculated only for matched transactions, and
they are calculated as the value of disposal less the value of acquisition less fees of disposal less fees of acquisition.

### Correctness
We know that transaction trackers are giving same final result as position trackers, which are giving same results as wallet.

Transaction trackers are very complex beings, which are used for transaction matching. Every time there is a match against held asset, that asset needs to be split and there is a portion of that asset that was matched and another portion that remains unmatched. This works symmetrically for short selling.
Note that fees are disposals, and the gain can arise when paying a delayed fee.

Position trackers accumulate each two sums one of all acquired and another of all disposed quantity. 
At the end we obtain summary and final position for each asset by calculating difference between total disposed quantity less total acquired quantity.

Wallet is the simplest tool to see the final balance. It accumulates sum of all acquired and disposed quantity as one number per each asset.

Additionally exported data can be put into a pivot table, and summary can be compared with Account Statement *(Wallet --> Account Statement)*.
I have worked with my trades, which included short selling on isolated and cross margin markets, as well as large OTC or small amount conversions.
Before EOY I have closed all positions, and converted to EUR. The values in *Changed Quantity* for all assets sum up to zero, and for EUR they sum up to my EOY Account Balance.

The pivot table will show summary of *Gains Value in EUR* and for assets the positions of which were closed it is same as *Sell value in EUR* - *Buy value in EUR*, however for assets the position of which wasn't closed that value will be different.



## Status

COMPLETED:
 - Correct calculation of the gains in EUR
 - Export to CSV transactions and matched lots

TODO:
 - Unit tests

FUTURE WORK:
 - Conversion from other CSV file formats
 - Direct API data sourcing
 - Perhaps parse blockchain to get all data required

## Commands

### Walk interactively through transactions
```
    python -m crypto_pnl walk your_data_folder
```

### Export as CSV with valuation per transaction in Fiat currency
```
    python -m crypto_pnl export-ledger your_data_folder
    python -m crypto_pnl export-trades your_data_folder
    python -m crypto_pnl export-tracker-events your_data_folder
``` 

## Data Download
This is where you put your Binanace logs. It's easy, please follow these instructions.

Create your data folder somewhere, e.g. `~/mydata` and then winthin that folder create following structure:
```
    mydata --+
             |
             +-- ledger
             |
             +-- market_data
             |
             +-- trades
```

### Step 1. Download Trade History
Login to Binance on your laptop and click Orders dropdown (it is located next to Wallet dropdown at the top bar), and select Spot Order.
Now, on the left side you have a sidebar, and there is Trade History. Click that, and next screen that appears will have a grey Export button at the top right corner.
Use that button to download the trade history for Spot account.


You need to download all of your trade history and not only Spot Orders. Here is
the tabs you need to visit on the sidebar, and there is always an Export button
at the top right corner to download the history. Use that button, and then
select the date range you need to export. Note though that CryptoPnL tool (this
tool) needs to work from beginning in order to match lots correctly, so you need
to have all your trade history downloaded from the beginning of time.

These are the sidebar tabs you need to visit and download Trade History from:

 - Spot Order
    - Trade History
 - Margin
    - Trade History
        - Cross
        - Isolated

Place all those CSV files (Trade History) inside `~/mydata/trades/`.
Make sure files are `.csv` and not zipped, and not `.xlsx`. Unpack any zipped files, and convert any `.xlsx` files to `.csv`.

### Step 2. Download Transactions History
Login to Binance on your laptop and click Wallet dropdown (it is located at the top bar, left to login), and select Transactions History.
Page that loads have *Generate all statements* button/link at the top right corner. Click that and you will be able to export transaction history.
Note that transaction history contains mainly loan interests, commisions, small amount conversions, large OTC trades. These aren't found in trade history.
However it also contains some sporadic entries from trade history, but you need to not worry, CryptoPnL tool (this tool) will ignore those duplicates.

Place all those CSV files (Transaction History) inside `~/mydata/ledger/`.
Make sure files are `.csv` and not zipped, and not `.xlsx`. Unpack any zipped files, and convert any `.xlsx` files to `.csv`.

Note that it is important to you download all trade history and transaction history, because CryptoPnL tool (this tool) needs to match correctly lots.

### Step 3. Downlaod Public Market Data
Visit https://www.binance.com/en/landing/data and click Download Now button just under Spot section. It will take you to file server, and you will see:
```
    futures
    spot
```

You probably want to choose `spot`, and then choose `daily` and then choose `klines` (i.e. `spot/daily/klines`).
Now, in that folder you have lots of markets. You only need to download market data for main asset vs `USDT` of the markets where you traded.
So for example if I traded `AR/BTC` I need to download `BTC/USDT`.
Additionally you also need to download `EUR/USDT`.

You need to download market data only for days when you have trades, and if there are days you didn't trade, and there was no ledger events, then no market data for those days is required.

It is also advised to download market data for 31st December, simply because if you didn't close your positions, then you will need to valuate what was not closed using the price from 31st December.

Place all those CSV files (Market Data) inside `~/mydata/market_data/`.
Make sure files are `.csv` and not zipped, and not `.xlsx`. Unpack any zipped files, and convert any `.xlsx` files to `.csv`.

### Screenshot

![Screenshot from 2022-03-19 19-17-56](https://user-images.githubusercontent.com/80485211/159135413-208effda-c08e-480d-b5eb-619cf9972c4c.png)
