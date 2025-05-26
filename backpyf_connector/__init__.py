"""
Back Test Py Binance Connector.

BackPy-binance-connector is a library for creating strategies and automating them in real life using the Binance API.

Version:
    0.0.4a1

Repository:
    https://github.com/Diego-Cores/BackPy-binance-connector

License:
    MIT License

    Copyright (c) 2024 Diego

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from .strategy import StrategyClassReal
from ._commons import (
    __recvWindow,
    __rec_limit,
    __chat_id,
    __alert,
    __logs,
)
from .main import (
    class_execute,
    telegram_bot,
    class_group,
    print_log,
    )

from . import tradetools as tools

__doc__ = """
BackPy-binance-connector documentation.

BackPy-binance-connector is a library that seeks to expand the functionalities of BackPy by 
providing the possibility of carrying out real trading using the Binance API.

Important Notice:
    Understanding the Risks of Trading and Financial Data Analysis.

    Trading financial instruments and using financial data for analysis 
    involves significant risks, including the possibility of loss of 
    capital. Markets can be volatile and data may contain errors. Before 
    engaging in trading activities or using financial data, it is important 
    to understand and carefully consider these risks and seek independent 
    financial advice if necessary.
"""

__all__ = [
    'StrategyClassReal',
    'class_execute',
    'telegram_bot',
    'class_group',
    'print_log',
    'tools',
    '__recvWindow',
    '__rec_limit',
    '__chat_id',
    '__alert',
    '__logs',
]
