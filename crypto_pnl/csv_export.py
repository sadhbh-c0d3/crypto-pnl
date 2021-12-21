from .core import *
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
    print ','.join((
            'transaction',
            'date',
            'market',
            'action',
            'asset',
            'amount',
            'cost ({})'.format(FIAT_SYMBOL),
    ))

    for number, trade in enumerate(trades):
        exchange_rate_calculator.will_execute(trade)
        journal.execute(trade)
        print ','.join(map(str,(
            number,
            trade.date,
            trade.pair,
            get_traded_action(trade.side),
            trade.executed.symbol,
            trade.executed.quantity * trade.side,
            display_fiat(trade.executed.value * trade.side),
        )))
        print ','.join(map(str,(
            number,
            trade.date,
            trade.pair,
            get_main_action(trade.side),
            trade.amount.symbol,
            trade.amount.quantity * -trade.side,
            display_fiat(trade.amount.value * -trade.side),
        )))
        print ','.join(map(str,(
            number,
            trade.date,
            trade.pair,
            FEE_ACTION,
            trade.fee.symbol,
            -trade.fee.quantity,
            display_fiat(-trade.fee.value),
        )))

