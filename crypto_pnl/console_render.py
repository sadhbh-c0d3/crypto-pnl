from .core import *
from .asset import Asset


class RenderAsset:
    @classmethod
    def render_value(cls, asset):
        if asset.has_value:
            return '{:10}'.format(display_fiat(asset.value_data))
        else:
            return '{:10}'.format('(n/a)'.center(10))

    @classmethod
    def render(cls, asset):
        return '{:16} {:5}'.format( display(asset.quantity), asset.symbol)


class RenderTrade:
    @classmethod
    def render_info(cls, trade):
        return '\n'.join((
            'Date:        {}'.format(trade.date),
            'Pair:        {}'.format(trade.pair),
            'Transaction: {:4} {:16} {:5} ({} EUR)'.format(
                get_side(trade.side),
                display(trade.executed.quantity),
                trade.executed.symbol,
                RenderAsset.render_value(trade.executed)
            ),
            'Unit Price:           {:16} {:5}'.format(
                display(trade.price),
                trade.amount.symbol
            ),
            (
                'Consideration:    {:16}'.format(RenderAsset.render(trade.amount))
                    if trade.side == SIGN_SELL else
                'Cost:             {:16}'.format(RenderAsset.render(trade.amount))
            ),
            'Fee:              {:16}'.format(RenderAsset.render(trade.fee)),
            'Conversion Rate:         1.0 {:5} @ {:16} {}'.format(
                trade.exchange_symbol,
                display(trade.exchange_rate),
                FIAT_SYMBOL)
            ))


class RenderMarketData:
    @classmethod
    def render_info(cls, md):
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
    def render(cls, md):
        return '{} {} / {}  {} {} {} {}'.format(
            md.date,
            md.symbol_traded,
            md.symbol_main,
            md.open_price,
            md.high_price,
            md.low_price,
            md.close_price)


class RenderWallet:
    def __init__(self, exchange_rate_calculator):
        self.exchange_rate_calculator = exchange_rate_calculator

    def render_pocket(self, wallet, pocket):
        asset = Asset(wallet.pockets[pocket].quantity, wallet.pockets[pocket].symbol)
        if self.exchange_rate_calculator:
            self.exchange_rate_calculator.set_asset_value(asset)
        return '{:10} |{:16} {:10}'.format(
            asset.symbol,
            display(asset.quantity),
            RenderAsset.render_value(asset)
        )

    @classmethod
    def render_headers(cls):
        return '{:10} | {:16} {:10}'.format(
            '',
            '(QUANTITY)'.rjust(16),
            '(VALUE)'.rjust(10))

    def render(self, wallet):
        return '\n'.join([self.render_pocket(wallet, k)
            for k,v in sorted_items(wallet.pockets)])


class RenderPosition:
    def __init__(self, exchange_rate_calculator):
        self.exchange_rate_calculator = exchange_rate_calculator

    @classmethod
    def render_headers(cls):
        return ' {} {} {}|  {} {}'.format(
            '(ACQUIRED)'.rjust(16),
            '(DISPOSED)'.rjust(16),
            '(FEE)'.rjust(16),
            '(POSITION)'.rjust(16),
            '({})'.format(FIAT_SYMBOL).rjust(10)
        )

    def render(self, position):
        total_position = Asset(position.total_acquire - position.total_dispose - position.total_fee, position.symbol)
        if self.exchange_rate_calculator:
            self.exchange_rate_calculator.set_asset_value(total_position)
        return '{:16} {:16} {:16} | {:16} {:10}'.format(
            display(position.total_acquire),
            display(position.total_dispose),
            display(position.total_fee),
            display(total_position.quantity),
            RenderAsset.render_value(total_position)
        )


class RenderPositions:
    def __init__(self, render_position):
        self.render_position = render_position

    @classmethod
    def render_headers(cls):
        return '{:10} |{}'.format('', RenderPosition.render_headers())

    def render(self, accounts):
        return '\n'.join(
                '{:10} |{}'.format(k, self.render_position.render(v))
                for k,v in sorted_items(accounts.positions))


class RenderSummary:
    def __init__(self, render_positions):
        self.render_positions = render_positions

    def render(self, summary):
        return '{}\n{}'.format(
                RenderPositions.render_headers(),
                self.render_positions.render(summary.total))


class RenderTracker:
    @classmethod
    def render_headers(cls):
        return ' {} {} {}|  {} {} {} '.format(
            ' (ACQUIRED)'.rjust(16),
            ' (DISPOSED)'.rjust(16),
            ' (FEE PAID)'.rjust(16),
            ' (COST)'.rjust(10),
            ' (EARN)'.rjust(10),
            ' (GAIN)'.rjust(10)
        )

    @classmethod
    def render_match(cls, tracker, match):
        buy, sell, fee = match
        position = Asset(sell.quantity - buy.quantity + fee.quantity, tracker.symbol)
        position.set_value(sell.value_data - buy.value_data + fee.value_data, GAIN_VALUE)
        return '{:16} {:16} {:16} | {:10} {:10} {:10} '.format(
            display(buy.quantity),
            display(sell.quantity),
            display(fee.quantity),
            RenderAsset.render_value(buy).rjust(10),
            RenderAsset.render_value(sell).rjust(10),
            RenderAsset.render_value(position).rjust(10)
        )

    @classmethod
    def render_matches(cls, tracker):
        return '\n'.join(map(cls.render_match(tracker), tracker.matched))


    @classmethod
    def render_event(cls, tracker, e):
        etype, action, data = e
        if etype == MATCH_EVENT:
            return '{:5} | {:5} | {:10} | {:16} {:16} {:16}'.format(action[2], action[3], action[1], *(display(x.quantity) for x in data))
        elif etype == CARRY_EVENT:
            return '{:5} | {:5} | {:10} | {:16}'.format(action[2], action[3], action[1], display(data.quantity))


class RenderTrackers:
    def __init__(self, render_position):
        self.render_position = render_position

    @classmethod
    def render_headers(cls):
        return '{:10} |{}'.format('', RenderTracker.render_headers())

    @classmethod
    def render_matches(cls, trackers):
        return '\n'.join(
                '{:10} |{}'.format(k, RenderTracker.render_match(v, m))
                for k,v in sorted_items(trackers.trackers)
                for m in v.matched)

    def render_stacks(self, trackers):
        return '\n'.join(
                '{:10} |{}'.format(s.symbol, self.render_position.render(s))
                for s in trackers.list_stacks())

    def render_events(self, trackers):
        return '\n'.join(
                '{:10} |{}'.format(k, RenderTracker.render_event(v, e))
                for k,v in sorted_items(trackers.trackers)
                for e in v.events)


class RenderTransaction:
    def __init__(self, render_trackers):
        self.render_trackers = render_trackers

    @classmethod
    def render_headers(cls):
        return '{:10} |{}'.format('', RenderTracker.render_headers())

    @classmethod
    def render_matches(cls, transaction):
        return '\n'.join(
                '{:10} |{}'.format(v.tracker.symbol, RenderTracker.render_match(v.tracker,m))
                for v in transaction.legs
                for m in v.tracker.matched)

    def render_stacks(self, transaction):
        return self.render_trackers.render_stacks(transaction.trackers)


class Render:
    def __init__(self, exchange_rate_calculator):
        self.wallet = RenderWallet(exchange_rate_calculator)
        self.position = RenderPosition(exchange_rate_calculator)
        self.positions = RenderPositions(self.position)
        self.trackers = RenderTrackers(self.position)
        self.transaction = RenderTransaction(self.trackers)
        self.summary = RenderSummary(self.positions)

