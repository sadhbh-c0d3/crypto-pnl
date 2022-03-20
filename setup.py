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
        version="0.1.1",
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