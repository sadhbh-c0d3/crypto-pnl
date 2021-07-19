from .core import *
from .trade import load_trades
from .summary import Summary
from .wallet import Wallet
from .journal import Journal
from .position import Positions
from .tracker import Trackers


def print_trade_summary(index, trade, wallet, journal, fees):
    print '\n{}'.format(line_title('[ Trade #{:5}]'.format(index)))
    print trade
    print line_trade_summary()
    print '{} (ACCOUNT)'.format(Positions.headers_str())

    summary_journal_main = Summary()
    summary_journal_main.calculate(journal.main.get_subset([trade.pair]))
    summary_journal_main.calculate_total_value()
    print '{}  {}:Main'.format(summary_journal_main.total, trade.pair)

    summary_journal_traded = Summary()
    summary_journal_traded.calculate(journal.traded.get_subset([trade.pair]))
    summary_journal_traded.calculate_total_value()
    print '{}  {}:Traded'.format(summary_journal_traded.total, trade.pair)

    summary_fees = Summary()
    summary_fees.add_fees(fees.get_subset([trade.fee.symbol]))
    summary_fees.calculate_total_value()
    print '{}  {}:Fee'.format(summary_fees.total, trade.pair)
    print line_trade_summary()
    
    summary_journal_all = Summary()
    summary_journal_all.calculate(journal.all)
    summary_journal_all.add_fees(fees)
    summary_journal_all.calculate_total_value()
    print '{}  Portfolio'.format(summary_journal_all.total)
    
    #summary_wallet = Summary()
    #summary_wallet.add_ballances(wallet)
    #summary_wallet.add_fees(fees)
    # summary_wallet.add_ballances(wallet.get_subset([
    #     trade.executed.symbol, 
    #     trade.amount.symbol]))
    # summary_wallet.add_fees(fees.get_subset([
    #     trade.fee.symbol]))
    #summary_wallet.calculate_total_value()
    #print summary_wallet.total
    #print '{} ({}:Wallet)'.format(summary_wallet.total, trade.pair)
    print line_trade_summary()
    #print wallet
    print Trackers.headers_str()
    print journal.trackers
    # print '{}  Gains'.format(journal.trackers.get_subset([
    #     trade.executed.symbol, 
    #     trade.amount.symbol]))
    print
    

def print_final_summary(wallet, journal, fees):
    print '\n{}'.format(line_title('[ Balance ]'))
    summary_wallet = Summary()
    summary_wallet.calculate(journal.all)
    summary_wallet.add_fees(fees)
    summary_wallet.calculate_total_value()
    print summary_wallet

    print '\n{}'.format(line_title('[ Position (Main) ]'))
    summary_journal_main = Summary()
    summary_journal_main.calculate(journal.main)
    summary_journal_main.calculate_total_value()
    print summary_journal_main
    
    print '\n{}'.format(line_title('[ Position (Traded) ]'))
    summary_journal_traded = Summary()
    summary_journal_traded.calculate(journal.traded)
    summary_journal_traded.calculate_total_value()
    print summary_journal_traded

    print '\n{}'.format(line_title('[ Fees ]'))
    summary_fees = Summary()
    summary_fees.add_fees(fees)
    summary_fees.calculate_total_value()
    print summary_fees
    
    summary_main = Summary()
    summary_main.calculate(journal.main)
    summary_main.calculate_total_value()

    print '\n{}'.format(line_title('[ Summary (Main) ]'))
    print summary_main

    summary_traded = Summary()
    summary_traded.calculate(journal.traded)
    summary_traded.calculate_total_value()

    print '\n{}'.format(line_title('[ Summary (Traded) ]'))
    print summary_traded
    
    summary = Summary()
    summary.calculate(summary_main.total)
    summary.calculate(summary_traded.total)
    summary.calculate_total_value()
    
    print '\n{}'.format(line_title('[ Summary ]'))
    print summary
    
    print line_trade_summary()
    print wallet

    print '\n{}'.format(line_title('[ Gains ]'))
    print Trackers.headers_str()
    print journal.trackers.summary()

    print


def walk_trades(path):
    trades = load_trades(path)

    wallet = Wallet()
    fees = Wallet()
    journal = Journal(wallet, fees)

    command = None
    filter_pair = None
    filter_traded = None
    filter_main = None
    filter_asset = None

    command = raw_input('T> ')
    if command.startswith('pair'):
        filter_pair = command[len('pair '):]
    if command.startswith('traded'):
        filter_traded = command[len('traded '):]
    if command.startswith('main'):
        filter_main = command[len('main '):]
    if command.startswith('asset'):
        filter_asset = command[len('asset '):]

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
        print_trade_summary(index, trade, wallet, journal, fees)
        command = raw_input('T> ')
        if command == 'quit':
            return

    print '(No more trades.)'
    while True:
        command = raw_input('\nT> ')
        if command == 'quit':
            return
        if command == 'summary':
            print_final_summary(wallet, journal, fees)
            break


def export_trades(path):
    trades = load_trades(path)
    print ','.join((
            'date',
            'pair',
            'side',
            'executed.symbol',
            'executed.quantity',
            'executed.value',
            'price',
            'amount.symbol',
            'amount.quantity',
            'amount.value',
            'fee.symbol',
            'fee.quantity',
            'fee.value',
            'exchange_symbol',
            'exchange_rate'
    ))
    for trade in trades:
        print ','.join(map(str,(
            trade.date,
            trade.pair,
            trade.side,
            trade.executed.symbol,
            trade.executed.quantity,
            display(trade.executed.value),
            trade.price,
            trade.amount.symbol,
            trade.amount.quantity,
            display(trade.amount.value),
            trade.fee.symbol,
            trade.fee.quantity,
            display(trade.fee.value),
            trade.exchange_symbol,
            display(trade.exchange_rate)
        )))

