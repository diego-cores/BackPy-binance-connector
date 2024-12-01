
from binance.um_futures import UMFutures
from datetime import datetime, timedelta
from binance.api import ClientError
import backpyf as bk
import pandas as pd
import time as te
import requests

from . import tradetools as tools
from . import exception
from . import strategy
from . import _commons

def set_client(api_key:str, secret_key:str, test:bool = True) -> None:
    # Init futures client
    client = UMFutures(api_key, secret_key,
                       base_url="https://fapi.binance.com/")
    
    _commons.__client = client
    _commons.__function = client.new_order_test if test else client.new_order

def set_data(symbol:str, interval:str, leverage:int, 
               ps_type:str, last:int) -> None:
    """
    Set data.
    
    This function set the data of symbol.
    """

    ## Set data
    _commons.__symbol = symbol
    _commons.__interval = interval
    _commons.__leverage = leverage
    _commons.__ps_type = ps_type

    _commons.__client.change_leverage(symbol=symbol, leverage=leverage, 
                                      recvWindow=_commons.__recvWindow)
    try: 
        _commons.__client.change_margin_type(symbol=symbol, marginType=ps_type, 
                                             recvWindow=_commons.__recvWindow)
    except ClientError: pass

    _commons.__data = tools.fetch_data(symbol, interval, last=last)
    _commons.__width = bk.utils.calc_width(_commons.__data.index)

def calc_close(initial_close, time_close) -> datetime:
    now = datetime.now()

    if now >= initial_close:
        intervals = ((abs((now-initial_close).total_seconds()))/86400)//time_close+1
        initial_close += timedelta(days=intervals*time_close)

    return initial_close

def get_public_ip() -> str:
    """
    Get the public ip.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()

        return response.json().get("ip")
    except requests.RequestException as e:
        if _commons.__alert: 
            print(f"Error getting public IP: {e}")
        return None
    
_commons.__ip_acc = get_public_ip()

def check_binance_connection_futures() -> bool:
    """
    Check binance futures connection.
    """
    try:
        _commons.__client.change_leverage(symbol=_commons.__symbol, leverage=_commons.__leverage, 
                                          recvWindow=_commons.__recvWindow)
        return True
    except Exception as e:
        if _commons.__alert: 
            print(f"Error in the connection to Binance futures: {e}")
        return False

def check_binance_connection() -> bool:
    """
    Check binance connection.
    """
    try:
        _commons.__client.time()
        return check_binance_connection_futures()
    except Exception as e:
        if _commons.__alert: 
            print(f"Error in the connection to Binance: {e}")
        return False

def generate_class(api_key:str, secret_key:str,
                   cls:type, symbol:str, interval:str, 
                   leverage:int, ps_type:str, last:int) -> None:
    """
    Run Your Strategy.

    Executes your trading strategy in REAL Binance.

    Args:
        cls (type): A class inherited from `StrategyClass` where the strategy is 
                    implemented.
    """
    if (not issubclass(cls, bk.strategy.StrategyClass) and 
        not issubclass(cls, strategy.StrategyClassReal)):
        raise exception.GenerateError(
            f"'{cls.__name__}' is not a subclass of 'strategy.StrategyClass'")
    elif cls.__abstractmethods__:
        raise exception.GenerateError(
            "The implementation of the 'next' abstract method is missing.")

    set_client(api_key=api_key, secret_key=secret_key)
    set_data(symbol=symbol, interval=interval, leverage=leverage,
             ps_type=ps_type, last=last)

    cls.__bases__ = (strategy.StrategyClassReal,)

    instance = cls(
        symbol = _commons.__symbol, 
        interval = _commons.__interval, 
        width = _commons.__width,
        commission=tools.get_commission(symbol=_commons.__symbol))
    
    instance._StrategyClassReal__before(data=_commons.__data)
    if _commons.__logs: print('Executed strategy.')

    act_trades = tools.open_trades(symbol=_commons.__symbol)
    __trades = tools.close_trades(symbol=_commons.__symbol)

    if not act_trades.empty: __trades = pd.concat([
        __trades, act_trades.dropna(axis=1, how='all')
        ], ignore_index=True)

def generate_loop(api_key:str, secret_key:str,
                  cls:type, symbol:str, interval:str, 
                  leverage:int, ps_type:str, last:int,
                  wrun:bool = False, time_offset = 0,
                  time_less:int = -60, time_in:int = 30, 
                  time_close:float = 1) -> None:
    """
    Run Your Strategy.

    Executes your trading strategy in REAL Binance.

    Args:
        cls (type): A class inherited from `StrategyClass` where the strategy is 
                    implemented.
    """
    if (not issubclass(cls, bk.strategy.StrategyClass) and 
        not issubclass(cls, strategy.StrategyClassReal)):
        raise exception.GenerateError(
            f"'{cls.__name__}' is not a subclass of 'strategy.StrategyClass'")
    elif cls.__abstractmethods__:
        raise exception.GenerateError(
            "The implementation of the 'next' abstract method is missing.")

    set_client(api_key=api_key, secret_key=secret_key)
    set_data(symbol=symbol, interval=interval, leverage=leverage,
             ps_type=ps_type, last=last)

    cls.__bases__ = (strategy.StrategyClassReal,)

    instance = cls(
        symbol = _commons.__symbol, 
        interval = _commons.__interval, 
        width = _commons.__width,
        )

    if wrun:
        instance._StrategyClassReal__before(data=_commons.__data,
                                            commission=tools.get_commission(symbol=_commons.__symbol))
        if _commons.__logs: 
            print('Executed strategy.')

    time = datetime.now()
    this_close = time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=time_offset)

    last_cc_bc = time+timedelta(seconds=30)
    last_cc_ip = time+timedelta(minutes=0.2)

    run = True

    history = {}
    
    if _commons.__logs: 
        print('Started.')
    while True:
        time = datetime.now()
    
        if time >= last_cc_bc and _commons.__logs:
            if not check_binance_connection():
                print("⚠️ Connection to Binance lost.")
                run = False
            else:
                run = True
            last_cc_bc = time + timedelta(seconds=30)
        
        if time >= last_cc_ip and _commons.__logs:
            new_ip = get_public_ip()
            if new_ip and new_ip != _commons.__ip_acc:
                print(f"⚠️ Public IP has changed: {_commons.__ip_acc} -> {new_ip}")
                _commons.__ip_acc = new_ip
            last_cc_ip = time + timedelta(minutes=0.2)

        this_close = calc_close(initial_close=this_close,
                                time_close=time_close)
        this_less = this_close+timedelta(seconds=time_less)

        if (time >= min(this_close, this_less) and
            time <= max(this_close, this_less) and
            not this_close in history.keys() and run
            ):
            
            try:
                set_data(symbol=symbol, interval=interval, leverage=leverage,
                        ps_type=ps_type, last=last)
                instance._StrategyClassReal__before(data=_commons.__data,
                                                    commission=tools.get_commission(symbol=_commons.__symbol))

                if _commons.__logs: 
                    print('Strategy executed.')
                history[this_close] = True
            except Exception as e:
                if _commons.__alert: 
                    print(f"Error when executing the strategy: {e}")

                if _commons.__logs:
                    if not check_binance_connection():
                        print("⚠️ Connection to Binance lost.")
                        run = False
                    else:
                        run = True
                    last_cc_bc = time + timedelta(seconds=30)

        te.sleep(time_in)
