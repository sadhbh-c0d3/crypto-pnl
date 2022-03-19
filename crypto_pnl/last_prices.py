from .core import *

class LastPrices:
    def __init__(self):
        self._last_market_data = {}

    def set_market_data_streams(self, market_data_streams):
        combined_market_data = combine_data_streams(market_data_streams)
        self.market_data_iter = iter(combined_market_data)
        self.market_data_current = None
        self.market_data_next = None
    
    def play_market_data_until(self, date):
        while True:
            if self.market_data_next and date < self.market_data_next.date:
                break
            try:
                which_stream, self.market_data_next = next(self.market_data_iter)
                if date < self.market_data_next.date:
                    break
                key = (
                    self.market_data_next.symbol_traded,
                    self.market_data_next.symbol_main)
                self._last_market_data[key] = self.market_data_next
                self.market_data_current = self.market_data_next
            except StopIteration:
                break
    
    def get_last_price(self, traded_symbol, main_symbol):
        last_market_data = self._last_market_data.get((traded_symbol, main_symbol))
        if last_market_data:
            return last_market_data.value


