# crypto-pnl
Crypto Trading Realized PnL Calculation (in EUR)

## Rationale
Jurisdictions require calculation of the PnL and CGT based off that as per transation basis.

This simple program is trying to do calculations based off Binance Isolated Margin Trading Data.

In order to use it correctly all other trades need to be converted into Isolated Margin Trading Data CSV file format.

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

TODO
 - unit tests

## Status
UNDER DEVELOPMENT

There is lots of things to be done here:
 - Correct calculation of the gains in EUR (WIP)
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
    python -m crypto_pnl export your_data_folder
``` 

### Screenshot

![image](https://user-images.githubusercontent.com/80485211/146946307-bd7f9fad-78c1-49c5-acb2-11633f6198a5.png)
