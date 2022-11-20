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
        self.which_stream_next = None
        self.market_data_next = None
    
    def play_market_data_until(self, date):
        def is_next_after_date():
            return (date < self.market_data_next.date)
    
        def get_next_key():
            return (self.market_data_next.symbol_traded,
                    self.market_data_next.symbol_main)

        def set_last_market_data():
            self._last_market_data[get_next_key()] = self.market_data_next
            self.market_data_current = self.market_data_next
        
        if self.market_data_next:
            if is_next_after_date():
                return
            set_last_market_data()
        
        for (self.which_stream_next,
             self.market_data_next) in self.market_data_iter:
            if is_next_after_date():
                break
            set_last_market_data()

    
    def get_last_price(self, traded_symbol, main_symbol):
        last_market_data = self._last_market_data.get((traded_symbol, main_symbol))
        if last_market_data:
            return last_market_data.value

    def get_last_update_date(self, traded_symbol, main_symbol):
        last_market_data = self._last_market_data.get((traded_symbol, main_symbol))
        if last_market_data:
            return last_market_data.date

