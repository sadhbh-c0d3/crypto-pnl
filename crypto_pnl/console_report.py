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
from .summary import Summary
from .console_render import (
    Render,
    RenderPositions,
    RenderTrackers,
    RenderTransaction,
    RenderTrade,
    RenderWallet,
)

class ConsoleReport:
    def __init__(self, exchange_rate_calculator, options):
        self.exchange_rate_calculator = exchange_rate_calculator
        self.options = options

    def print_trade_summary(self, index, trade, journal):
        render = Render(self.exchange_rate_calculator)

        print '\n{}'.format(line_title('[ Trade #{:5}]'.format(index)))
        print RenderTrade.render_info(trade)

        print '\n\n{}\n'.format(line_title('[ Total Account Balance ]'))
        print RenderPositions.render_headers()
        print line_trade_summary()

        summary_journal_all = Summary()
        summary_journal_all.calculate(journal.position_tracker.all)
        print render.positions.render(summary_journal_all.total)

        if 'show_traded_pair' in self.options:
            print '\n{}\n'.format(line_section('[ Traded Pair Account Balance ]'))
            summary_journal_main = Summary()
            summary_journal_main.calculate(journal.position_tracker.main.get_subset([trade.pair]))
            print '{}   {}:Main'.format(
                render.positions.render(summary_journal_main.total),
                trade.pair)

            summary_journal_traded = Summary()
            summary_journal_traded.calculate(journal.position_tracker.traded.get_subset([trade.pair]))
            print '{}   {}:Traded'.format(
                render.positions.render(summary_journal_traded.total),
                trade.pair)

        print '\n\n{}\n'.format(line_title('[ Asset Portfolio ]'))
        print RenderPositions.render_headers()
        print line_trade_summary()

        trackers = journal.last_transaction.trackers
        print render.positions.render(trackers.balance())

        if trackers.has_unpaid_fees():
            print '\n{}\n'.format(line_section('[ Unpaid Fees ]'))
            print render.positions.render(trackers.unpaid_fees_balance())

        print '\n{}\n'.format(line_section('[ Individual Assets ]'))
        print render.trackers.render_stacks(trackers)

        print '\n\n{}\n'.format(line_title('[ Transaction Gains ]'))
        print RenderTransaction.render_headers()
        print line_trade_summary()
        print RenderTransaction.render_matches(journal.last_transaction)

        print '\n\n{}\n'.format(line_section('[ Individial Events ]'))
        print RenderTrackers.render_event_headers()
        print render.trackers.render_events(trackers)

        print '\n'*4


    def print_final_summary(self, journal):
        render = Render(self.exchange_rate_calculator)

        if 'show_traded_pair' in self.options:
            print '\n{}'.format(line_title('[ Total Main Account Balance ]'))
            summary_main = Summary()
            summary_main.calculate(journal.position_tracker.main)
            print render.summary.render(summary_main)

            print '\n{}'.format(line_title('[ Total Traded Account Balance ]'))
            summary_traded = Summary()
            summary_traded.calculate(journal.position_tracker.traded)
            print render.summary.render(summary_traded)

        print '\n{}'.format(line_title('[ Total Account Balance ]'))
        summary_wallet = Summary()
        summary_wallet.calculate(journal.position_tracker.all)
        print render.summary.render(summary_wallet)

        print '\n{}'.format(line_title('[ All Individual Assets (fees deducted) ]'))
        print RenderPositions.render_headers()
        print render.trackers.render_stacks(journal.transaction_engine.trackers)

        print '\n{}'.format(line_title('[ All Asset Balance ]'))
        print RenderPositions.render_headers()
        trackers_balance = journal.transaction_engine.trackers.balance()
        print render.positions.render(trackers_balance)

        if journal.transaction_engine.trackers.has_unpaid_fees():
            trackers_unpaid_fees = journal.transaction_engine.trackers.unpaid_fees_balance()
            print '\n{}'.format(line_title('[ All Unpaid Fees ]'))
            print render.positions.render(trackers_unpaid_fees)
            summary_trackers = Summary()
            summary_trackers.calculate(trackers_balance)
            summary_trackers.calculate(trackers_unpaid_fees)
            print '\n{}'.format(line_title('[ Remaining Asset Balance (after fees are paid) ]'))
            print render.summary.render(summary_trackers)

        print '\n{}'.format(line_title('[ Total Transaction Gains (summary of all individual matched assets) ]'))
        print RenderTrackers.render_headers()
        print render.trackers.render_matches(journal.transaction_engine.trackers.summary())

        print '\n{}'.format(line_title('[ Wallet (remaining total amounts of assets) ]'))
        print RenderWallet.render_headers()
        print render.wallet.render(journal.wallet)

        print
