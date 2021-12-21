from setuptools import setup

setup(
    name="crypto_pnl",
    version="0.1.0",
    packages=["crypto_pnl"],
    test_suite="",
    entry_points={
        'console_scripts': [
            'crypto_pnl=crypto_pnl.__main__:main',
        ],
    },
)
