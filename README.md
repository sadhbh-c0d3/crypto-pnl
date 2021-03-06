# crypto-pnl
Crypto Trading Realized PnL Calculation (in EUR)

### Installation
```
pip install crypto-pnl
```

### Usage

Export as CSV matches of acquisitions with disposals (LIFO), and report gains in EUR
```
    crypto_pnl export-tracker-events your_data_folder > exported-tracker-events.csv
```
or if you prefer FIFO
```
    crypto_pnl export-tracker-events-fifo your_data_folder > exported-tracker-events-fifo.csv
```

Export as CSV by adding EUR value per transaction based on market data
```
    crypto_pnl export-ledger your_data_folder > exported-ledger.csv
    crypto_pnl export-trades your_data_folder > exported-trades.csv
```
Walk interactively through transactions
```
    crypto_pnl walk your_data_folder
```

**Please follow instructions below in section *Data Download* to learn about how to _correctly_ download data from Binance**

## Rationale
Jurisdictions require calculation of the PnL and CGT based off that as per transation basis.

This program performs gains calculations for Binance using Trade History and Transaction History.

Works with Spot, Cross Margin, and Isolated Margin accounts.
Handles all trades, including short-selling, small assets conversion, and large OTC trades.

> The reason I started writing this tool was that other tools were unable to correctly match my transactions, which involved plenty of tiny trades including shortselling.

## Matching Transactions & Gains Calculation
### Gains Calculation
The gains are calculated only for matched transactions, and they are calculated as:

> The Value of Disposal - The Value of Acquisition

1. *"The Value of"* is estimated using Maket Data that is matched against the disposal and acquisition transations.
2. *"Acquisition"* is transaction in which we acquired an asset
3. *"Disposal"* is:
 - Any transaction in which we disposed an asset
 - Any fee paid on acquisition and/or disposal

### Rules
According to defaults often found in commercial tools in Ireland we use FIFO, but I haven't found any such confirmation in official Revenue documentation.
[Revenue statement on taxation of cryptocurrencies](https://www.revenue.ie/en/companies-and-charities/financial-services/cryptocurrencies/index.aspx)

The rules for UK are described here [CGT share matching rules ??? a worked example](https://www.whitefieldtax.co.uk/cgt-share-matching-rules-worked-example/)
They can essetially be realized by LIFO, with the twist that for assets held longer than 30 days we would need to use average price instead. We don't support that yet.

This tool supports both LIFO and FIFO.

### Description
A matching engine uses multi-leg transaction trackers to match disposals against acquisitions.

A tracker remebers all acquisitions together with their prices in EUR estimated at the time of acquisition,
and then disposal with price in EUR estimated at the time of disposal.

Additionally tracker remembers the price in EUR of any fees at the time these fees arose. 

The short selling is supported, and covers matching of disposals of borrowed assets against following acquisitions. The EUR prices are estimated at the time of disposal and acquisition as previously. The fees may be covered by borrowed assets, since often fees are on traded asset, which we borrowed to sell it.

### License & Disclaimer
> MIT License
> 
> Copyright (c) 2021 Sadhbh Code
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.


## Status

COMPLETED:
 - Correct calculation of the gains in EUR
 - Export to CSV transactions and matched lots
 - FIFO and LIFO matching rules

TODO:
 - Unit tests
 - UK matching rules

BUGS:
 - Everything is possible :)

FUTURE WORK:
 - Conversion from other CSV file formats
 - Direct API data sourcing
 - Perhaps parse blockchain to get all data required


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

### Screenshots

Data exported to CSVs
![crypto-pnl-trackers](https://user-images.githubusercontent.com/80485211/160294421-cc91ecbe-6dbc-40c9-be0c-feb0b2aab9ae.png)
![crypto-pnl-trades](https://user-images.githubusercontent.com/80485211/160294424-7c439093-78a7-43cf-997e-109e97ad0935.png)
![crypto-pnl-ledger](https://user-images.githubusercontent.com/80485211/160294426-b74eb94b-49b8-4fa1-b061-a86573dc1ccb.png)

Walking the trades
![image](https://user-images.githubusercontent.com/80485211/159135476-0612a077-1773-4f5e-a20a-7434b1f00b53.png)
