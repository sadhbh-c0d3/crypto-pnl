from setuptools import setup

setup(
    name="crypto_pnl",
    version="0.1.0",
    py_modules=["crypto_pnl"],
    test_suite="",
    entry_points="""
        [console_scripts]
        crypto_pnl=cypto_pnl.__main__:main
    """,
)
