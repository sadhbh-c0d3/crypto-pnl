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
    def __init__(self, exchange_rate_calculator):
        self.exchange_rate_calculator = exchange_rate_calculator

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

        print '\n\n{}\n'.format(line_title('[ Transaction Events ]'))
        print render.trackers.render_events(trackers)

        print '\n'*4


    def print_final_summary(self, journal):
        render = Render(self.exchange_rate_calculator)

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
        trackers_unpaid_fees = journal.transaction_engine.trackers.unpaid_fees_balance()
        print render.positions.render(trackers_balance)

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
