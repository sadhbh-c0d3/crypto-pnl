from .core import *
from .asset import copy_asset
from .trade import load_trades, use_trade_streams
from .ledger import load_ledger, use_ledger_streams
from .market_data import load_market_data
from .wallet import Wallet
from .journal import Journal
from .position import Positions, PositionTracker
from .transaction import TransactionEngine
from .tracker import Trackers
from .last_prices import LastPrices
from .exchange_rate_calculator import ExchangeRateCalculator
from .console_report import ConsoleReport


def walk_trades(trades_paths, ledger_paths, market_data_paths):
    last_prices = LastPrices()
    exchange_rate_calculator = ExchangeRateCalculator(last_prices)
    wallet = Wallet()
    position_tracker = PositionTracker()
    transaction_engine = TransactionEngine()
    journal = Journal(wallet, position_tracker, transaction_engine)

    last_prices.set_market_data_streams(
        map(load_market_data, market_data_paths))

    ledgers = use_ledger_streams(
        map(load_ledger, ledger_paths))

    trades = use_trade_streams(
        map(load_trades, trades_paths))

    command = None
    filter_pair = None
    filter_traded = None
    filter_main = None
    filter_asset = None

    print('Transaction listing tool')
    print('''
    Available filter commands with example argument:
        pair DOGEBTC
        traded DOGE
        main BTC
        asset DOGE

    Press Enter to continue without filter...
    ''')
    command = raw_input('T> ')
    if command.startswith('pair'):
        filter_pair = command[len('pair '):]
        print('Listing transactions for pair {}'.format(filter_pair))
    if command.startswith('traded'):
        filter_traded = command[len('traded '):]
        print('Listing transactions for traded {}'.format(filter_traded))
    if command.startswith('main'):
        filter_main = command[len('main '):]
        print('Listing transactions for main {}'.format(filter_main))
    if command.startswith('asset'):
        filter_asset = command[len('asset '):]
        print('Listing transactions for asset {}'.format(filter_asset))

    print('''
    Available commands during listing:
        run
        quit

    Press Enter to walk transactions step by step...
    ''')
    command = raw_input('T> ')

    options = {}
    report = ConsoleReport(exchange_rate_calculator, options)

    number = 0
    ledger_number = 0
    for which, entry in combine_data_streams([trades, ledgers]):
        if not which:
            number += 1
            trade = entry
            exchange_rate_calculator.will_execute(trade)
            journal.execute(trade)
            if filter_pair and trade.pair != filter_pair:
                continue
            if filter_traded and trade.executed.symbol != filter_traded:
                continue
            if filter_main and trade.amount.symbol != filter_main:
                continue
            if filter_asset and filter_asset not in (
                    trade.amount.symbol, trade.executed.symbol):
                continue
            if command == 'run':
                continue
            report.print_trade_summary(number, trade, journal)
            command = raw_input('T> ')
            if command == 'quit':
                return
        else:
            ledger_number += 1
            if entry.account == 'Spot' and entry.operation in (
                'Transaction Related',
                'Buy',
                'Sell',
                'Fee'):
                continue
            exchange_rate_calculator.set_asset_value(entry.change)
            if not entry.change.has_value:
                raise ValueError('Please, download market data for {}/{} on {} from {}'.format(
                    entry.change.symbol,
                    FIAT_EXCHANGE_SYMBOL,
                    entry.date,
                    'https://www.binance.com/en/landing/data'))
            base_tracker = transaction_engine.get_tracker(entry.change.symbol)
            tracker = base_tracker.branch()
            if entry.change.quantity > 0:
                tracker.acquire(entry.change)
            elif entry.change.quantity < 0:
                change = copy_asset(entry.change)
                change.quantity = -change.quantity
                change.value_data = -change.value_data
                tracker.dispose(change)
            base_tracker.merge(tracker)


    print '(No more trades.)'
    print('''
    Available commands:
        quit

    Press Enter to continue to summary...
    ''')
    command = raw_input('\nT> ')
    if command == 'quit':
        return
    report.print_final_summary(journal)


