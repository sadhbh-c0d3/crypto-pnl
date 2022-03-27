# MIT License
#
# Copyright (c) 2021 Sadhbh Code
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .core import *
from .asset import Asset, zero_asset, copy_asset
from .trade import load_trades, use_trade_streams
from .ledger import load_ledger, use_ledger_streams, shoud_ignore_ledger_entry, should_change_loan_balance
from .market_data import load_market_data
from .wallet import Wallet
from .journal import Journal
from .position import Positions, PositionTracker
from .transaction import TransactionEngine
from .tracker import Trackers, Tracker
from .last_prices import LastPrices
from .exchange_rate_calculator import ExchangeRateCalculator
from .console_report import ConsoleReport


TRACKER_EVENT_HEADERS = (
    'ID',
    'Date',
    'Type',
    'Event',
    'Symbol',
    'Action',
    'Side',
    'Match ID',
    'Buy Quantity',
    'Sell Quantity',
    'Changed Quantity',
    'Buy value in {}'.format(FIAT_SYMBOL),
    'Sell value in {}'.format(FIAT_SYMBOL),
    'Gains value in {}'.format(FIAT_SYMBOL),
)

TRADE_HEADERS = (
    'ID',
    'Date',
    'Traded Pair',
    'Side',
    'Main Quantity',
    'Main Symbol',
    'Traded Quantity',
    'Traded Symbol',
    'Fee Quantity',
    'Fee Symbol',
    'Price',
    'Price.Symbol',
    'Exchange Rate in {}'.format(FIAT_SYMBOL),
    'Trade value in {}'.format(FIAT_SYMBOL),
)

LEDGER_HEADERS = (
    'ID',
    'Date',
    'Account',
    'Operation',
    'Coin',
    'Change',
    'Value in {}'.format(FIAT_SYMBOL),
    'Remark',
)

def render_tracker_event(e):
    etype, action, data = e
    if etype == MATCH_EVENT:
        buy, sell, fee = data
        data = buy
        if action in (BUY_MATCH_ACTION, SELL_MATCH_ACTION):
            acquired_id = buy.xid
            disposed_id = sell.xid
            acquired_value = buy.value_data
            disposed_value = sell.value_data
        else:
            acquired_id = buy.xid
            disposed_id = fee.xid
            acquired_value = buy.value_data
            disposed_value = fee.value_data

        gains = disposed_value - acquired_value

        if action in (BUY_MATCH_ACTION, REPAY_FEE_MATCH_ACTION):
            acquired_qty = data.quantity
            disposed_qty = 0
            disposed_value = 0
            changed_qty = data.quantity
            match_id = disposed_id
        else:
            acquired_qty = 0
            acquired_value = 0
            disposed_qty = data.quantity
            changed_qty = -data.quantity
            match_id = acquired_id

    elif etype == CARRY_EVENT:
        if action in (STACK_CARRY_ACTION,):
            acquired_qty = data.quantity
            disposed_qty = 0
            changed_qty = data.quantity
            acquired_value = data.value_data
            disposed_value = 0
        else:
            acquired_qty = 0
            disposed_qty = data.quantity
            changed_qty = -data.quantity
            acquired_value = 0
            disposed_value = data.value_data

        match_id = ''
        gains = 0
    
    type_, event_, action_, side_ = action

    return (type_, event_, data.symbol, action_, side_, match_id,
        '%.7f' % acquired_qty,
        '%.7f' % disposed_qty,
        '%.7f' % changed_qty,
        '%.7f' % acquired_value,
        '%.7f' % disposed_value,
        '%.7f' % gains,
    )


def render_trade(trade):
    return (
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
        '%.7f' % trade.exchange_rate,
        '%.7f' % trade.amount.value_data,
    )


def render_ledger_entry(entry):
    if shoud_ignore_ledger_entry(entry):
        entry_remark = 'Entry should be ignored as it duplicates an entry from trading log.' + entry.remark
    elif should_change_loan_balance(entry):
        entry_remark = 'Entry is used to calculate loan interests.' + entry.remark
    else:
        entry_remark = entry.remark

    return (
        entry.date,
        entry.account,
        entry.operation,
        entry.change.symbol,
        entry.change.quantity,
        ('%.7f' % entry.change.value_data) if entry.change.has_value else '',
        entry_remark,
    )



def export_tracker_events(trades_paths, ledger_paths, market_data_paths, use_fifo = False):
    if use_fifo:
        Tracker.TRACKER_DIR = TRACKER_FIFO

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

    print(','.join(TRACKER_EVENT_HEADERS))

    number = 0
    ledger_number = 0
    for which, entry in combine_data_streams([trades, ledgers]):
        if not which:
            number += 1
            xid = 'T/{}'.format(number)
            trade = entry
            trade.amount.set_id(xid)
            trade.executed.set_id(xid)
            trade.fee.set_id(xid)
            exchange_rate_calculator.will_execute(trade)
            journal.execute(trade)

        else:
            ledger_number += 1
            xid = 'L/{}'.format(ledger_number)
            if shoud_ignore_ledger_entry(entry):
                continue

            exchange_rate_calculator.will_process_ledger_entry(entry)
            entry.change.set_id(xid)
            journal.process_ledger_entry(entry)

        for symbol, tracker in sorted_items(
                journal.last_transaction.trackers.trackers):
            for te in tracker.events:
                print(','.join(map(str, (xid, entry.date) + render_tracker_event(te)
                )))


def export_trades(trades_paths, ledger_paths, market_data_paths):
    last_prices = LastPrices()
    exchange_rate_calculator = ExchangeRateCalculator(last_prices)
    wallet = Wallet()
    position_tracker = PositionTracker()
    transaction_engine = TransactionEngine()
    journal = Journal(wallet, position_tracker, transaction_engine)

    last_prices.set_market_data_streams(
        map(load_market_data, market_data_paths))

    trades = use_trade_streams(
        map(load_trades, trades_paths))

    print(','.join(TRADE_HEADERS))

    for number, trade in enumerate(trades):
        xid = 'T/{}'.format(number+1)
        exchange_rate_calculator.will_execute(trade)
        journal.execute(trade)
        print(','.join(map(str, (xid,) + render_trade(trade))))


def export_ledger(trades_paths, ledger_paths, market_data_paths):
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

    print(','.join(LEDGER_HEADERS))

    ledger_number = 0
    for which, entry in combine_data_streams([trades, ledgers]):
        if not which:
            exchange_rate_calculator.will_execute(entry)
            journal.execute(entry)

        else:
            ledger_number += 1
            xid = 'L/{}'.format(ledger_number)
            exchange_rate_calculator.set_asset_value(entry.change)
            print(','.join(map(str, (xid,) + render_ledger_entry(entry))))
