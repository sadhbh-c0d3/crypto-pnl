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

from setuptools import setup


summary ="""Crypto Trading Realized PnL Calculation (in EUR)"""

long_description = """Crypto Trading Realized PnL Calculation (in EUR)

Jurisdictions require calculation of the PnL and CGT based off that as per transation basis.

This program performs gains calculations for Binance using Trade History and Transaction History.

Works with Spot, Cross Margin, and Isolated Margin accounts. Handles all trades,
including short-selling, interests, small assets conversion, and large OTC
trades."""

classifiers = """Development Status :: 4 - Beta
Intended Audience :: End Users/Desktop
License :: OSI Approved :: MIT License
Topic :: Office/Business :: Financial
Topic :: Office/Business :: Financial :: Accounting
Topic :: Office/Business :: Financial :: Spreadsheet"""


def main():
    setup(
        name="crypto_pnl",
        version="0.2.0",
        url="https://github.com/sadhbh-c0d3/crypto-pnl",
        author="Sonia Kolasinska",
        author_email="sonia.kolasinska.pro@gmail.com",
        maintainer="Sonia Kolasinska",
        maintainer_email="sonia.kolasinska.pro@gmail.com",
        license = "MIT",
        description = summary,
        long_description  = long_description,
        classifiers = classifiers.split("\n"),
        packages=["crypto_pnl"],
        entry_points={
            'console_scripts': [
                'crypto_pnl=crypto_pnl.__main__:main',
            ],
        },
    )


if __name__ == "__main__":
    main()