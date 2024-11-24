
from binance.um_futures import UMFutures
from datetime import datetime, timedelta
import backpyf.exception as exception
from binance.api import ClientError
import backpyf as bk
import pandas as pd
import numpy as np
import time as te
import requests
import os

from . import tradetools as tools
from . import utils
from . import strategy

# Api keys
utils.load_env() # load eviroment variables

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

# Init futures client
client = UMFutures(api_key, secret_key,
                   base_url="https://fapi.binance.com/")  # dapi for UM

__logs = True

__symbol = None
__leverage = None
__ps_type = None
__interval = None

__data = None
__width = None
__trades = None

def set_data(symbol:str, interval:str, leverage:int, 
             ps_type:str, last:int):
    """
    Set data.
    
    This function set the data of symbol.
    """
    global __symbol, __leverage, __ps_type, __interval, __width, __data
    
    ## Set data
    __symbol = symbol
    __interval = interval
    __leverage = leverage
    __ps_type = ps_type

    client.change_leverage(symbol=symbol, leverage=leverage, 
                           recvWindow=tools.recvWindow)
    try: 
        client.change_margin_type(symbol=symbol, marginType=ps_type, 
                                   recvWindow=tools.recvWindow)
    except ClientError: pass

    __data = tools.fetch_data(symbol, interval, last=last)
    __width = bk.utils.calc_width(__data.index)

def calc_close(initial_close, time_close):
    now = datetime.now()

    if now >= initial_close:
        intervals = ((abs((now-initial_close).total_seconds()))/86400)//time_close+1
        initial_close += timedelta(days=intervals*time_close)

    return initial_close

def get_public_ip():
    """
    Get the public ip.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()

        return response.json().get("ip")
    except requests.RequestException as e:
        if __logs: 
            print(f"Error getting public IP: {e}")
        return None
    
__ip_acc = get_public_ip()
if __logs: 
    print(f"Public IP: {__ip_acc}")

def check_binance_connection_futures():
    """
    Check binance futures connection.
    """
    try:
        client.change_leverage(symbol=__symbol, leverage=__leverage, 
                               recvWindow=tools.recvWindow)
        return True
    except Exception as e:
        if __logs: 
            print(f"Error in the connection to Binance futures: {e}")
        return False

def check_binance_connection():
    """
    Check binance connection.
    """
    try:
        client.time()
        return check_binance_connection_futures()
    except Exception as e:
        if __logs: 
            print(f"Error in the connection to Binance: {e}")
        return False

def generate_class(cls:type, symbol:str, interval:str, 
                   leverage:int, ps_type:str, last:int) -> None:
    """
    Run Your Strategy.

    Executes your trading strategy in REAL Binance.

    Args:
        cls (type): A class inherited from `StrategyClass` where the strategy is 
                    implemented.
    """
    if not issubclass(cls, bk.strategy.StrategyClass):
        raise exception.RunError(
            f"'{cls.__name__}' is not a subclass of 'strategy.StrategyClass'")
    elif cls.__abstractmethods__:
        raise exception.RunError(
            "The implementation of the 'next' abstract method is missing.")
    global __symbol, __trades, __data

    set_data(symbol=symbol, interval=interval, leverage=leverage,
             ps_type=ps_type, last=last)

    cls.__bases__ = (strategy.ModStrateyClass,)

    instance = cls(
        symbol = __symbol, 
        interval = __interval, 
        width = __width,
        commission=tools.get_commission(symbol=__symbol))
    
    instance._ModStrateyClass__before(data=__data)
    if __logs: print('Executed strategy.')

    act_trades = tools.open_trades(symbol=__symbol)
    __trades = tools.close_trades(symbol=__symbol)

    if not act_trades.empty: __trades = pd.concat([
        __trades, act_trades.dropna(axis=1, how='all')
        ], ignore_index=True)

def generate_loop(cls:type, symbol:str, interval:str, 
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
    if not issubclass(cls, bk.strategy.StrategyClass):
        raise exception.RunError(
            f"'{cls.__name__}' is not a subclass of 'strategy.StrategyClass'")
    elif cls.__abstractmethods__:
        raise exception.RunError(
            "The implementation of the 'next' abstract method is missing.")
    global __symbol, __trades, __data, __ip_acc

    set_data(symbol=symbol, interval=interval, leverage=leverage,
             ps_type=ps_type, last=last)

    cls.__bases__ = (strategy.ModStrateyClass,)

    instance = cls(
        symbol = __symbol, 
        interval = __interval, 
        width = __width,
        )

    if wrun:
        instance._ModStrateyClass__before(data=__data,
                                          commission=tools.get_commission(symbol=__symbol))
        if __logs: 
            print('Executed strategy.')

    time = datetime.now()
    this_close = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=time_offset)

    last_cc_bc = datetime.now()+timedelta(seconds=30)
    last_cc_ip = datetime.now()+timedelta(minutes=5)

    alert = False

    history = {}
    
    if __logs: 
        print('Started.')
    while True:
        time = datetime.now()
    
        if time >= last_cc_bc:
            if not check_binance_connection():
                print("⚠️ Connection to Binance lost.")
                alert = True
            else:
                alert = False
            last_cc_bc = time + timedelta(seconds=30)
        
        if time >= last_cc_ip:
            new_ip = get_public_ip()
            if new_ip and new_ip != __ip_acc:
                print(f"⚠️ Public IP has changed: {__ip_acc} -> {new_ip}")
                __ip_acc = new_ip
            last_cc_ip = time + timedelta(minutes=5)

        if not alert:
            this_close = calc_close(initial_close=this_close,
                                    time_close=time_close)
            this_less = this_close+timedelta(seconds=time_less)

            if (time >= min(this_close, this_less) and
                time <= max(this_close, this_less) and
                not this_close in history.keys()):
                
                try:
                    set_data(symbol=symbol, interval=interval, leverage=leverage,
                            ps_type=ps_type, last=last)
                    instance._ModStrateyClass__before(data=__data,
                                                    commission=tools.get_commission(symbol=__symbol))

                    if __logs: 
                        print('Strategy executed.')
                    history[this_close] = True
                except Exception as e:
                    if __logs: 
                        print(f"Error when executing the strategy: {e}")

                    if not check_binance_connection():
                        print("⚠️ Connection to Binance lost.")
                        alert = True
                    else:
                        alert = False
                    last_cc_bc = time + timedelta(seconds=30)

        te.sleep(time_in)

def _data_info():
    return __interval, __width, __symbol
