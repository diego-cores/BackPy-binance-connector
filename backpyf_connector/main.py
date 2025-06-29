"""
Main module.

This module contains the main loop and the connection to the Binance client.

Functions:
    print_log: This function handles logs by sending them to the console and others.
    add_rec: This function adds the record to the '_commons.__rec' variable.
    set_client: Function that initializes the Binance client.
    set_data: This function set the symbol data and client configuration.
    set_search: Request symbol data to Binance API.
    calc_close: This function calculates when the next closing will be.
    get_public_ip: This function uses 'Ipify' to return the current IP.
    check_binance_connection_futures: This function verifies the connection to Binance Futures.
    check_binance_connection: This function verifies the connection to Binance.
    check_connection: This function verifies that all services remain connected.
    cls_instance: Create instance of 'cls', check exceptions.
    instance_execute: Executes the 'instance' strategy.
    generate_loop: This function generates the main loop.
    class_execute: Execute your trading strategy in REAL once.
    class_group: Execute your trading strategy in REAL by automating it.
    telegram_bot: Run the Telegram bot by starting a new thread.
"""

from binance.um_futures import UMFutures
from datetime import datetime, timedelta
from binance.api import ClientError
from threading import Thread
import backpyf as bk
import time as te
import requests

from . import tradetools as tools
from . import exception
from . import strategy
from . import _commons

def print_log(message:str, alert:bool=False) -> None:
    """
    Print log

    This function handles logs by sending them to the console and others.

    Note:
        If '_commons.__inter_log' is a 'callable' the log will be sent to it.

    Args:
        message (str): Log message.
        alert (bool, optional): True if you want it to be sent as an alert.
    """

    if (_commons.__logs and not alert) or (_commons.__alert and alert):
        if callable(message):
            message(); return
        
        if callable(_commons.__inter_log):
            _commons.__inter_log(message, alert)

        add_rec(message, alert)
        print(message)

def add_rec(log:str, alert:bool=False) -> None:
    """
    Add rec

    This function adds the record to the '_commons.__rec' variable.

    Args:
        message (str): Log message.
        alert (bool, optional): True if you want it to be sent as an alert.
    """

    _commons.__rec.append([datetime.now(), log, alert])
    if len(_commons.__rec) > _commons.__rec_limit:
        _commons.__rec.pop(0)

def set_client(api_key:str, secret_key:str, test:bool = True) -> None:
    """
    Set client

    Function that initializes the Binance client.

    Args:
        api_key (str): Binance API key.
        secret_key (str): Binance API secret key.
        test (bool, optional): If true, the test version will be run, 
            which instead of using the 'client.new_order' function uses 'client.new_order_test'.
    """

    # Init futures client
    client = UMFutures(api_key, secret_key,
                    base_url="https://fapi.binance.com/")
    
    _commons.__client = client
    _commons.__function = client.new_order_test if test else client.new_order

def set_data(symbol:str, interval:str, leverage:int, 
               ps_type:str, last:int) -> None:
    """
    Set data

    This function set the symbol data and client configuration.

    Args:
        symbol (str): Binance symbol.
        interval (str): Data interval.
        leverage (str): Leverage used in futures.
        ps_type (str): Binance Margin Type.
        last (int): Amount of data from today back that you want to request.
    """

    ## Set data
    _commons.__symbol = symbol
    _commons.__interval = interval
    _commons.__leverage = leverage
    _commons.__ps_type = ps_type

    while True:
        try: 
            _commons.__client.change_leverage(symbol=symbol, leverage=leverage, 
                                            recvWindow=_commons.__recvWindow)
        except ClientError as e:
            print_log(f"⚠️ Connection to Binance or Timestamp error.\nActual ip: {_commons.__ip_acc}.\n{e.message}", alert=True)
            te.sleep(30); continue
        break

    try: 
        _commons.__client.change_margin_type(symbol=symbol, marginType=ps_type, 
                                             recvWindow=_commons.__recvWindow)
    except ClientError: pass

    set_search(last)

def set_search(last:int) -> None:
    """
    Set search

    Request symbol data to Binance API.

    Args:
        last (int): Amount of data from today back that you want to request.
    """

    _commons.__data = tools.fetch_data(_commons.__symbol, _commons.__interval, 
                                       last=last)
    _commons.__width = bk.utils.calc_width(_commons.__data.index)

def calc_close(initial_close:datetime, time_close:int) -> datetime:
    """
    Calc close

    This function calculates when the next closing will be.

    Args:
        initial_close (datetime): First closing of the day.
        time_close (int): Interval duration 1 = day.

    Return:
        datetime: Return the next close datetime.
    """

    now = datetime.now()

    if now >= initial_close:
        intervals = ((abs((now-initial_close).total_seconds()))/86400)//time_close+1
        initial_close += timedelta(days=intervals*time_close)

    return initial_close

def get_public_ip() -> str:
    """
    Get public ip

    This function uses 'Ipify' to return the current IP.

    Return:
        str: Actual public ip.
    """

    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()

        return response.json().get("ip")
    except requests.RequestException as e:
        print_log(f"Error getting public IP", alert=True)
        return None

# Get the pubpublicicl ip
_commons.__ip_acc = get_public_ip()

def check_binance_connection_futures() -> bool:
    """
    Check binance futures connection

    This function verifies the connection to Binance Futures 
        by changing the symbol and leverage to the configured ones.

    Return:
        bool: 'True' if the connection is still active, 'False' otherwise.
    """

    try:
        _commons.__client.change_leverage(symbol=_commons.__symbol, leverage=_commons.__leverage, 
                                          recvWindow=_commons.__recvWindow)
        return True
    except Exception as e:
        print_log(f"Error in the connection to Binance futures", alert=True)
        return False

def check_binance_connection() -> bool:
    """
    Check binance connection

    This function verifies the connection to Binance.

    Return:
        bool: 'True' if the connection is still active, 'False' otherwise.
    """

    try:
        _commons.__client.time()
        return check_binance_connection_futures()
    except Exception as e:
        print_log(f"Error in the connection to Binance", alert=True)
        return False

def check_connection() -> bool:
    """
    Check connection

    This function verifies that all services remain connected.

    Return:
        bool: 'True' if the connection is still active, 'False' otherwise.
    """

    if not (result:=check_binance_connection()):
        print_log("⚠️ Connection to Binance lost", alert=True)

    if (new_ip:=get_public_ip()) and new_ip != _commons.__ip_acc:
        print_log(f"⚠️ Public IP has changed: {_commons.__ip_acc} -> {new_ip}", alert=True)
        _commons.__ip_acc = new_ip 

    return result

def cls_instance(cls:type) -> strategy.StrategyClassReal:
    """
    Cls instance

    Create instance of 'cls', check exceptions.

    Return:
        StrategyClassReal: The created instance.
    """

    if (not issubclass(cls, bk.strategy.StrategyClass) and 
        not issubclass(cls, strategy.StrategyClassReal)):
        raise exception.GenerateError(
            f"'{cls.__name__}' is not a subclass of 'strategy.StrategyClass'")
    elif cls.__abstractmethods__:
        raise exception.GenerateError(
            "The implementation of the 'next' abstract method is missing.")
    
    cls.__bases__ = (strategy.StrategyClassReal,)
    return cls(
        symbol = _commons.__symbol, 
        interval = _commons.__interval, 
        width = _commons.__width,
        commission=tools.get_commission(symbol=_commons.__symbol))

def instance_execute(instance:strategy.StrategyClassReal, name='') -> None:
    """
    Instance execute

    Executes the 'instance' strategy.

    Args:
        instance (StrategyClassReal): Instance of 'StrategyClassReal'.
        name (str, optional): Name of the strategy.
    """

    instance._StrategyClassReal__before(data=_commons.__data,
                                        commission=tools.get_commission(symbol=_commons.__symbol))
    if _commons.__logs: print_log('Executed strategy.'+('' if name == '' else f"'{name}'"))

def generate_loop(function:callable, time_offset:float = 0, time_less:int = -60, 
                  time_in:int = 30, time_close:float = 1) -> None:
    """
    Generate loop

    This function generates the main loop where 
        every so often the connections will be verified and the strategy executed.

    Args:
        function (callable): Function where the strategy is executed.
        time_offset (float, optional): Argument that indicates when the first close of the day is.
            Calculated in days where hour 0 is added plus 'time_offset' which gives the first close of the day.
        time_less (int, optional): Time the loop has to execute the strategy, 
            at the opening it will operate a positive number and at the closing 
            a negative number, value in seconds.
        time_in (int, optional): The value in seconds indicates how often the 
            loop will run to check whether the strategy needs to be executed. 
            A value less than 'time_less' is recommended to always execute the strategy.
        time_close (float, optional): Value indicating the interval in days. 
            Example of 1 hour interval: 1/24.
    """

    run = True
    history = {}
    time = datetime.now()
    last_cc_bc = time+timedelta(seconds=30)
    this_close = time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=time_offset)
    
    print_log('Started.')
    while _commons.__main_loop:
        time = datetime.now()
    
        if time >= last_cc_bc:
            run = check_connection()
            last_cc_bc = time + timedelta(seconds=30)

        this_close = calc_close(initial_close=this_close, time_close=time_close)
        this_less = this_close+timedelta(seconds=time_less)

        if (time >= min(this_close, this_less) and
            time <= max(this_close, this_less) and
            not this_close in history.keys() and run
            ):
            try:
                function()
                print_log(f"Executed: {this_close}", alert=True)
                history[this_close] = True
            except Exception as e:
                print_log(f"Error when executing the strategy: {e}", alert=True)
                
                run = check_connection()
                last_cc_bc = time + timedelta(seconds=30)

        te.sleep(time_in)

    _commons.__main_loop = True
    _commons.__instances = None

def class_execute(api_key:str, secret_key:str,
                  cls:type, symbol:str, interval:str, 
                  leverage:int, ps_type:str, last:int, test:bool = True) -> None:
    """
    Class execute

    Execute your trading strategy in REAL once.

    Note:
        This will be executed in the real market using the Binance API. 
        Before executing this insurance, please refer to 'Risk_notice.txt'.
        Test can still close orders.

    Args:
        api_key (str): Binance API key.
        secret_key (str): Binance API secret key.
        cls (type): A class inherited from `StrategyClass` or `StrategyClassReal` 
            where the strategy is implemented.
        symbol (str): Binance Futures symbol to trade.
        interval (str): Binance Futures interval.
        leverage (int): Binance Futures leverage.
        ps_type (str): Binance Futures margin type.
        last (int): The number of candles from today that you want 
            to be loaded into your strategy to calculate it.
        test (bool, optional): If true, the test version will be run, 
            which instead of using the 'client.new_order' function uses 'client.new_order_test'.
            Test can still close orders.
    """

    set_client(api_key=api_key, secret_key=secret_key, test=test)
    set_data(symbol=symbol, interval=interval, leverage=leverage,
             ps_type=ps_type, last=last)
    
    instance = cls_instance(cls=cls)
    
    instance_execute(instance)

def class_group(api_key:str, secret_key:str,
                cls:list, symbol:str, interval:str, 
                leverage:int, ps_type:str, last:int,
                wrun:bool = False, time_offset:float = 0,
                time_less:int = -60, time_in:int = 30, 
                time_close:float = 1, test:bool = True) -> None:
    """
    Class group

    Execute your trading strategy in REAL by automating it.

    Note:
        This will be executed in the real market using the Binance API. 
        Before executing this insurance, please refer to 'Risk_notice.txt'.
        Test can still close orders.

    Args:
        api_key (str): Binance API key.
        secret_key (str): Binance API secret key.
        cls (type): A class inherited from `StrategyClass` or `StrategyClassReal` 
            where the strategy is implemented.
        symbol (str): Binance Futures symbol to trade.
        interval (str): Binance Futures interval.
        leverage (int): Binance Futures leverage.
        ps_type (str): Binance Futures margin type.
        last (int): The number of candles from today that you want 
            to be loaded into your strategy to calculate it.
        wrun (bool, optional): Executes the strategy at the start.
        time_offset (float, optional): Argument that indicates when the first close of the day is.
            Calculated in days where hour 0 is added plus 'time_offset' which gives the first close of the day.
        time_less (int, optional): Time the loop has to execute the strategy, 
            at the opening it will operate a positive number and at the closing 
            a negative number, value in seconds.
        time_in (int, optional): The value in seconds indicates how often the 
            loop will run to check whether the strategy needs to be executed. 
            A value less than 'time_less' is recommended to always execute the strategy.
        time_close (float, optional): Value indicating the interval in days. 
            Example of 1 hour interval: 1/24.
        test (bool, optional): If true, the test version will be run, 
            which instead of using the 'client.new_order' function uses 'client.new_order_test'.
            Test can still close orders.
    """

    set_client(api_key=api_key, secret_key=secret_key, test=test)
    set_data(symbol=symbol, interval=interval, leverage=leverage,
             ps_type=ps_type, last=last)
    
    instances = []
    _commons.__instances = []
    for i in cls:
        instances.append(cls_instance(cls=i))
        _commons.__instances.append(instances[-1].__class__.__name__)

    num_at = 0 if not tools.open_trades(symbol=_commons.__symbol).empty else None

    def loop():
        nonlocal num_at

        set_search(last=last)
        if num_at != None:
            instance_execute(instances[num_at], num_at)

            num_at = num_at if not tools.open_trades(symbol=_commons.__symbol).empty else None
            return

        for n, i in enumerate(instances):
            instance_execute(i, n+1)

            if not tools.open_trades(symbol=_commons.__symbol).empty:
                num_at = n; break

    if wrun: loop()

    generate_loop(loop, time_offset=time_offset, time_less=time_less,
                  time_in=time_in, time_close=time_close)

def telegram_bot(api_key:str, chatid:str = ""):
    """
    Telegram bot

    Run the Telegram bot by starting a new thread.

    Args:
        api_key (str): Telegram bot api key.
        chatid (str): It is used to receive logs and 
            request the bot for the machine's public IP.
            Use the '/chatid' command in your chat to get yours.
    """

    from . import telegram

    _commons.__chat_id = chatid
    Thread(target=telegram.bot_init, args=(api_key,), daemon=True).start()
