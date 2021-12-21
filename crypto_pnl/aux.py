from .core import *
from .trade import load_trades
from .market_data import load_market_data
from .summary import Summary
from .wallet import Wallet
from .journal import Journal
from .position import Positions
from .tracker import Trackers
from .last_prices import LastPrices
from .exchange_rate_calculator import ExchangeRateCalculator
from .console_render import (
    RenderPositions,
    RenderSummary,
    RenderTrackers,
    RenderTrade,
    RenderWallet,
)


def print_trade_summary(index, trade, wallet, journal, exchange_rate_calculator):
    print '\n{}'.format(line_title('[ Trade #{:5}]'.format(index)))
    print RenderTrade.info_str(trade)

    print '\n{}'.format(line_title('[ Total Account Balance ]'))
    print '{} (ACCOUNT)'.format(RenderPositions.headers_str())

    summary_journal_all = Summary()
    summary_journal_all.calculate(journal.all)
    print RenderPositions.valuated_str(summary_journal_all.total, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ Total Main/Traded Account Balance ]'))
    summary_journal_main = Summary()
    summary_journal_main.calculate(journal.main.get_subset([trade.pair]))
    print '{}   {}:Main'.format(
        RenderPositions.valuated_str(summary_journal_main.total, exchange_rate_calculator),
        trade.pair)

    summary_journal_traded = Summary()
    summary_journal_traded.calculate(journal.traded.get_subset([trade.pair]))
    print '{}   {}:Traded'.format(
        RenderPositions.valuated_str(summary_journal_traded.total, exchange_rate_calculator),
        trade.pair)

    print '\n{}'.format(line_title('[ Individual Assets (fees deducted) ]'))
    trackers = journal.trackers.get_subset([
       trade.executed.symbol,
       trade.amount.symbol,
       trade.fee.symbol
    ])
    print RenderTrackers.list_stacks_str(trackers, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ Asset Balance (post-trade) ]'))
    print RenderPositions.valuated_str(trackers.balance(), exchange_rate_calculator)
    if trackers.has_unpaid_fees():
        print '\n{}'.format(line_title('[ Unpaid Fees (post-trade) ]'))
        print RenderPositions.valuated_str(trackers.unpaid_fees_balance(), exchange_rate_calculator)

    print '\n{}'.format(line_title('[ Transaction Gains (matched individual assets) ]'))
    print RenderTrackers.headers_str()
    print RenderTrackers.last_transaction_str(trackers)

    print
    

def print_final_summary(wallet, journal, exchange_rate_calculator):
    print '\n{}'.format(line_title('[ Total Main Account Balance ]'))
    summary_main = Summary()
    summary_main.calculate(journal.main)
    print RenderSummary.valuated_str(summary_main, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ Total Traded Account Balance ]'))
    summary_traded = Summary()
    summary_traded.calculate(journal.traded)
    print RenderSummary.valuated_str(summary_traded, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ Total Account Balance ]'))
    summary_wallet = Summary()
    summary_wallet.calculate(journal.all)
    print RenderSummary.valuated_str(summary_wallet, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ All Individual Assets (fees deducted) ]'))
    print RenderPositions.headers_str()
    print RenderTrackers.list_stacks_str(journal.trackers, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ All Asset Balance ]'))
    print RenderPositions.headers_str()
    trackers_balance = journal.trackers.balance()
    trackers_unpaid_fees = journal.trackers.unpaid_fees_balance()
    print RenderPositions.valuated_str(trackers_balance, exchange_rate_calculator)
    print '\n{}'.format(line_title('[ All Unpaid Fees ]'))
    print RenderPositions.valuated_str(trackers_unpaid_fees, exchange_rate_calculator)
    summary_trackers = Summary()
    summary_trackers.calculate(trackers_balance)
    summary_trackers.calculate(trackers_unpaid_fees)
    print '\n{}'.format(line_title('[ Remaining Asset Balance (after fees are paid) ]'))
    print RenderSummary.valuated_str(summary_trackers, exchange_rate_calculator)

    print '\n{}'.format(line_title('[ Total Transaction Gains (summary of all individual matched assets) ]'))
    print RenderTrackers.headers_str()
    print RenderTrackers.matched_str(journal.trackers.summary())

    print '\n{}'.format(line_title('[ Wallet (remaining total amounts of assets) ]'))
    print RenderWallet.headers_str()
    print RenderWallet.valuated_str(wallet, exchange_rate_calculator)

    print


def walk_trades(trades_path, market_data_paths):
    last_prices = LastPrices()
    exchange_rate_calculator = ExchangeRateCalculator(last_prices)
    wallet = Wallet()
    journal = Journal(wallet)

    last_prices.set_market_data_streams(
        map(load_market_data, market_data_paths))

    trades = load_trades(trades_path)

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

    for index, trade in enumerate(trades):
        if filter_pair and trade.pair != filter_pair:
            continue
        if filter_traded and trade.executed.symbol != filter_traded:
            continue
        if filter_main and trade.amount.symbol != filter_main:
            continue
        if filter_asset and filter_asset not in (
                trade.amount.symbol, trade.executed.symbol):
            continue
        exchange_rate_calculator.will_execute(trade)
        journal.execute(trade)
        if command == 'run':
            continue
        print_trade_summary(index, trade, wallet, journal, exchange_rate_calculator)
        command = raw_input('T> ')
        if command == 'quit':
            return

    print '(No more trades.)'
    print('''
    Available commands:
        quit
    
    Press Enter to continue to summary...
    ''')
    command = raw_input('\nT> ')
    if command == 'quit':
        return
    print_final_summary(wallet, journal, exchange_rate_calculator)


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

