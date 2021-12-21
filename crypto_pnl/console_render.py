from .core import *
from .asset import Asset


class RenderAsset:
    @classmethod
    def value_str(cls, asset):
        if asset.has_value:
            return '{:10}'.format(display_fiat(asset.value_data))
        else:
            return '{:10}'.format('(n/a)'.center(10))

    @classmethod
    def line_str(cls, asset):
        return '{:16} {:5}'.format( display(asset.quantity), asset.symbol)


class RenderTrade:
    @classmethod
    def info_str(cls, trade):
        return '\n'.join((
            'Date:        {}'.format(trade.date),
            'Pair:        {}'.format(trade.pair),
            'Transaction: {:4} {:16} {:5} ({} EUR)'.format(
                get_side(trade.side),
                display(trade.executed.quantity),
                trade.executed.symbol,
                RenderAsset.value_str(trade.executed)
            ),
            'Unit Price:           {:16} {:5}'.format(
                display(trade.price),
                trade.amount.symbol
            ),
            (
                'Consideration:    {:16}'.format(RenderAsset.line_str(trade.amount))
                    if trade.side == SIGN_SELL else
                'Cost:             {:16}'.format(RenderAsset.line_str(trade.amount))
            ),
            'Fee:              {:16}'.format(RenderAsset.line_str(trade.fee)),
            'Conversion Rate:         1.0 {:5} @ {:16} {}'.format(
                trade.exchange_symbol,
                display(trade.exchange_rate),
                FIAT_SYMBOL)
            ))


class RenderMarketData:
    @classmethod
    def info_str(cls, md):
        return '\n'.join([
            'Date:           {}'.format(md.date),
            'Symbol(Main):   {}'.format(md.symbol_main),
            'Symbol(Traded): {}'.format(md.symbol_traded),
            'Open:           {}'.format(md.open_price),
            'High:           {}'.format(md.high_price),
            'Low:            {}'.format(md.low_price),
            'Close:          {}'.format(md.close_price),
        ])

    @classmethod
    def line_str(cls, md):
        return '{} {} / {}  {} {} {} {}'.format(
            md.date,
            md.symbol_traded,
            md.symbol_main,
            md.open_price,
            md.high_price,
            md.low_price,
            md.close_price)

class RenderWallet:
    @classmethod
    def format_pocket(cls, wallet, pocket, exchange_rate_calculator):
        asset = Asset(wallet.pockets[pocket].quantity, wallet.pockets[pocket].symbol)
        if exchange_rate_calculator:
            exchange_rate_calculator.set_asset_value(asset)
        return '{:10} |{:16} {:10}'.format(
            asset.symbol,
            display(asset.quantity),
            RenderAsset.value_str(asset)
        )

    @classmethod
    def headers_str(cls):
        return '{:10} | {:16} {:10}'.format(
            '',
            '(QUANTITY)'.rjust(16),
            '(VALUE)'.rjust(10))

    @classmethod
    def valuated_str(cls, wallet, exchange_rate_calculator = None):
        return '\n'.join([cls.format_pocket(wallet, k, exchange_rate_calculator)
            for k,v in sorted_items(wallet.pockets)])


class RenderPosition:
    @classmethod
    def headers_str(cls):
        return ' {} {} {}|  {} {}'.format(
            '(ACQUIRED)'.rjust(16),
            '(DISPOSED)'.rjust(16),
            '(FEE)'.rjust(16),
            '(POSITION)'.rjust(16),
            '({})'.format(FIAT_SYMBOL).rjust(10)
        )

    @classmethod
    def valuated_str(cls, position, exchange_rate_calculator = None):
        total_position = Asset(position.total_acquire - position.total_dispose - position.total_fee, position.symbol)
        if exchange_rate_calculator:
            exchange_rate_calculator.set_asset_value(total_position)
        return '{:16} {:16} {:16} | {:16} {:10}'.format(
            display(position.total_acquire),
            display(position.total_dispose),
            display(position.total_fee),
            display(total_position.quantity),
            RenderAsset.value_str(total_position)
        )


class RenderPositions:
    @classmethod
    def headers_str(cls):
        return '{:10} |{}'.format('', RenderPosition.headers_str())

    @classmethod
    def valuated_str(cls, accounts, exchange_rate_calculator = None):
        return '\n'.join(
                '{:10} |{}'.format(k, RenderPosition.valuated_str(v, exchange_rate_calculator))
                for k,v in sorted_items(accounts.positions))


class RenderSummary:
    @classmethod
    def valuated_str(cls, summary, exchange_rate_calculator = None):
        return '{}\n{}'.format(
                RenderPositions.headers_str(),
                RenderPositions.valuated_str(summary.total, exchange_rate_calculator))


class RenderTracker:
    @classmethod
    def headers_str(cls):
        return ' {} {} {}|  {} {} {} '.format(
            ' (ACQUIRED)'.rjust(16),
            ' (DISPOSED)'.rjust(16),
            ' (FEE PAID)'.rjust(16),
            ' (COST)'.rjust(10),
            ' (EARN)'.rjust(10),
            ' (GAIN)'.rjust(10)
        )

    @classmethod
    def format_match(cls, tracker, match):
        buy, sell, fee = match
        position = Asset(sell.quantity - buy.quantity - fee.quantity, tracker.symbol)
        position.set_value(sell.value_data - buy.value_data, GAIN_VALUE)
        return '{:16} {:16} {:16} | {:10} {:10} {:10} '.format(
            display(buy.quantity),
            display(sell.quantity),
            display(fee.quantity),
            RenderAsset.value_str(buy).rjust(10),
            RenderAsset.value_str(sell).rjust(10),
            RenderAsset.value_str(position).rjust(10)
        )

    @classmethod
    def matched_str(cls, tracker):
        return '\n'.join(map(cls.format_match(tracker), tracker.matched))

    @classmethod
    def last_transaction_str(cls, tracker):
        return '\n'.join(map(cls.format_match(tracker), tracker.matched[tracker.last_transaction_index:]))


class RenderTrackers:
    @classmethod
    def headers_str(cls):
        return '{:10} |{}'.format('', RenderTracker.headers_str())

    @classmethod
    def matched_str(cls, trackers):
        return '\n'.join(
                '{:10} |{}'.format(k, RenderTracker.format_match(v, m))
                for k,v in sorted_items(trackers.trackers)
                for m in v.matched)

    @classmethod
    def last_transaction_str(cls, trackers):
        return '\n'.join(
                '{:10} |{}'.format(k, RenderTracker.format_match(v,m))
                for k,v in sorted_items(trackers.trackers)
                for m in v.matched[v.last_transaction_index:])

    @classmethod
    def list_stacks_str(cls, trackers, exchange_rate_calculator = None):
        return '\n'.join(
                '{:10} |{}'.format(s.symbol, RenderPosition.valuated_str(s, exchange_rate_calculator))
                for s in trackers.list_stacks())

