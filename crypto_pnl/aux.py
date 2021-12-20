from .core import *
from .trade import load_trades
from .market_data import load_market_data
from .summary import Summary
from .wallet import Wallet
from .journal import Journal
from .position import Positions
from .tracker import Trackers
from .exchange_rates import exchange_rates


def print_trade_summary(index, trade, wallet, journal):
    print '\n{}'.format(line_title('[ Trade #{:5}]'.format(index)))
    print trade

    print '\n{}'.format(line_title('[ Position ]'))
    print '{} (ACCOUNT)'.format(Positions.headers_str())

    summary_journal_main = Summary()
    summary_journal_main.calculate(journal.main.get_subset([trade.pair]))
    print '{}   {}:Main'.format(summary_journal_main.total, trade.pair)

    summary_journal_traded = Summary()
    summary_journal_traded.calculate(journal.traded.get_subset([trade.pair]))
    print '{}   {}:Traded'.format(summary_journal_traded.total, trade.pair)

    print '\n{}'.format(line_trade_summary())
    summary_journal_all = Summary()
    summary_journal_all.calculate(journal.all)
    print '{}   Balance'.format(summary_journal_all.total)

    print '\n{}'.format(line_title('[ Transaction Gains ]'))
    print Trackers.headers_str()
    print journal.trackers.get_subset([
       trade.executed.symbol,
       trade.amount.symbol,
       trade.fee.symbol ]).last_transaction_str

    print
    

def print_final_summary(wallet, journal):
    print '\n{}'.format(line_title('[ Main ]'))
    summary_main = Summary()
    summary_main.calculate(journal.main)
    print summary_main

    print '\n{}'.format(line_title('[ Traded ]'))
    summary_traded = Summary()
    summary_traded.calculate(journal.traded)
    print summary_traded
    
    print '\n{}'.format(line_title('[ Balance ]'))
    summary_wallet = Summary()
    summary_wallet.calculate(journal.all)
    print summary_wallet

    print '\n{}'.format(line_title('[ Gains ]'))
    print Trackers.headers_str()
    print journal.trackers.summary()

    print '\n{}'.format(line_title('[ Wallet ]'))
    print Wallet.headers_str()
    print wallet

    print


def walk_trades(trades_path, market_data_paths):
    exchange_rates.set_market_data_streams(
        map(load_market_data, market_data_paths))

    trades = load_trades(trades_path)

    wallet = Wallet()
    journal = Journal(wallet)

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
        journal.execute(trade)
        if command == 'run':
            continue
        print_trade_summary(index, trade, wallet, journal)
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
    print_final_summary(wallet, journal)


def export_trades(trades_path, market_data_paths):
    exchange_rates.set_market_data_streams(
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
    
    wallet = Wallet()
    journal = Journal(wallet)
    
    for number, trade in enumerate(trades):
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

