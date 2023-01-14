from crypto_pnl.core import *
from crypto_pnl.trade import Trade


def test_trade_parse():
    row = ["2022-06-01 10:12:00", "ETHBTC", "BUY",
           "0.0800000000", "12.5ETH", "1BTC", "0.0001000000ETH"]
    trade = Trade(*row)
    assert format_datetime(trade.date) == "2022-06-01 11:12:00"
    assert trade.pair == "ETHBTC"
    assert trade.side == SIGN_BUY
    assert trade.price == Decimal("0.08")
    assert trade.executed.symbol == "ETH"
    assert trade.executed.quantity == Decimal("12.5")
    assert trade.amount.symbol == "BTC"
    assert trade.amount.quantity == Decimal("1")
    assert trade.fee.symbol == "ETH"
    assert trade.fee.quantity == Decimal("0.0001")
