from .core import *
from .asset import Asset, zero_asset
from .trade import load_trades
from .market_data import load_market_data
from .wallet import Wallet
from .journal import Journal
from .position import Positions, PositionTracker
from .transaction import TransactionEngine
from .tracker import Trackers
from .last_prices import LastPrices
from .exchange_rate_calculator import ExchangeRateCalculator
from .console_report import ConsoleReport


def render_tracker_event(e):
    etype, action, data = e
    if etype == MATCH_EVENT:
        buy, sell, fee = data
        data = buy
        if action in (BUY_MATCH_ACTION, SELL_MATCH_ACTION):
            acquired_value = buy.value_data
            disposed_value = sell.value_data
        else:
            acquired_value = buy.value_data
            disposed_value = fee.value_data
        gains = disposed_value - acquired_value

    elif etype == CARRY_EVENT:
        if action in (STACK_CARRY_ACTION, UNPAID_FEE_CARRY_ACTION):
            acquired_value = data.value_data
            disposed_value = 0
        else:
            acquired_value = 0
            disposed_value = data.value_data
        gains = 0
    
    return (
        etype,
        action,
        data.quantity,
        data.symbol,
        acquired_value,
        FIAT_SYMBOL,
        disposed_value,
        FIAT_SYMBOL,
        gains,
        FIAT_SYMBOL,
    )


def export_trades(trades_path, market_data_paths):
    last_prices = LastPrices()
    exchange_rate_calculator = ExchangeRateCalculator(last_prices)
    wallet = Wallet()
    position_tracker = PositionTracker()
    transaction_engine = TransactionEngine()
    journal = Journal(wallet, position_tracker, transaction_engine)

    last_prices.set_market_data_streams(
        map(load_market_data, market_data_paths))

    trades = load_trades(trades_path)
    print(','.join((
        'number',
        'date',
        'pair',
        'side',
        'main.quantity',
        'main.symbol',
        'traded.quantity',
        'traded.symbol',
        'fee.quantity',
        'fee.symbol',
        'price',
        'price.symbol',
        'exchange_via',
        'exchange_rate',
        'currency',
        'trade.value',
        'currency',
        'event.type',
        'event.action',
        'event.quantity',
        'event.symbol',
        'acquired.value',
        'currency',
        'disposed.value',
        'currency',
        'gains.value',
        'currency',
    )))

    for number, trade in enumerate(trades):
        exchange_rate_calculator.will_execute(trade)
        journal.execute(trade)
        for symbol, tracker in sorted_items(
                journal.last_transaction.trackers.trackers):
            for te in tracker.events:
                print(','.join(map(str, (
                    number,
                    trade.date,
                    trade.pair,
                    get_side(trade.side),
                    trade.amount.quantity,
                    trade.amount.symbol,
                    trade.executed.quantity,
                    trade.executed.symbol,
                    trade.fee.quantity,
                    trade.fee.symbol,
                    trade.price,
                    trade.amount.symbol,
                    trade.exchange_symbol,
                    trade.exchange_rate,
                    FIAT_SYMBOL,
                    trade.amount.value_data,
                    FIAT_SYMBOL,
                ) + render_tracker_event(te)
                )))
