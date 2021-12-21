from .core import *
from .trade import load_trades
from .market_data import load_market_data
from .wallet import Wallet
from .journal import Journal
from .position import Positions
from .tracker import Trackers
from .last_prices import LastPrices
from .exchange_rate_calculator import ExchangeRateCalculator
from .console_report import ConsoleReport


def export_trades(trades_path, market_data_paths):
    last_prices = LastPrices()
    exchange_rate_calculator = ExchangeRateCalculator(last_prices)
    wallet = Wallet()
    journal = Journal(wallet)

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

    def action_main(side):
        return 'DISPOSE' if side != SIGN_SELL else 'ACQUIRE'

    def action_executed(side):
        return 'DISPOSE' if side == SIGN_SELL else 'ACQUIRE'

    action_fee = 'FEE'

    for number, trade in enumerate(trades):
        exchange_rate_calculator.will_execute(trade)
        journal.execute(trade)
        print ','.join(map(str,(
            number,
            trade.date,
            trade.pair,
            action_executed(trade.side),
            trade.executed.symbol,
            trade.executed.quantity * trade.side,
            display_fiat(trade.executed.value * trade.side),
        )))
        print ','.join(map(str,(
            number,
            trade.date,
            trade.pair,
            action_main(trade.side),
            trade.amount.symbol,
            trade.amount.quantity * -trade.side,
            display_fiat(trade.amount.value * -trade.side),
        )))
        print ','.join(map(str,(
            number,
            trade.date,
            trade.pair,
            action_fee,
            trade.fee.symbol,
            -trade.fee.quantity,
            display_fiat(-trade.fee.value),
        )))

