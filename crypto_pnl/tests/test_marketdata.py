from crypto_pnl.core import *
from crypto_pnl.market_data import MarketData


def test_market_data_parse():
    row = ["1654074300000", "1.25000000", "1.28000000",
           "1.20000000", "1.26000000", "", "", "", "", "", ""]

    market_data = MarketData("ETHBTC", "BTC", *row)
    assert market_data.symbol_traded == "ETH"
    assert market_data.symbol_main == "BTC"
    assert market_data.unix == "1654074300000"
    assert format_datetime(market_data.date) == "2022-06-01 09:05:00"
    assert market_data.open_price == Decimal("1.25")
    assert market_data.high_price == Decimal("1.28")
    assert market_data.low_price == Decimal("1.2")
    assert market_data.close_price == Decimal("1.26")
    assert market_data.value == Decimal("1.2475")
