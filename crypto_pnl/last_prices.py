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


