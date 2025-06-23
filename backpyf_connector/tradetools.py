
from datetime import datetime, timedelta, timezone
import pandas as pd

from . import _commons

def get_balance() -> float:
    """
    Get balance

    This function requests the Binance API for the available balance in 'USDT'.

    Returns:
        float: availableBalance.
    """

    info_bl = _commons.__client.balance(recvWindow=_commons.__recvWindow)
    for i in range(len(info_bl)):
        if info_bl[i]['asset'].upper() == 'USDT': 
            return float(info_bl[i]['availableBalance'])
        
def get_commission(symbol) -> float:
    """
    Get commission

    This function requests the taker operation fees from the Binance API.

    Returns:
        float: takerCommissionRate.
    """

    commission_info = _commons.__client.commission_rate(symbol=symbol, recvWindow=_commons.__recvWindow)
    return float(commission_info['takerCommissionRate'])

def get_quantity_precision_symbol(symbol) -> float:
    """
    Get quantity precision of the symbol

    This function requests the Binance API for the accuracy of the amounts.

    Returns:
        float: quantityPrecision.
    """

    for i in _commons.__client.exchange_info()['symbols']:
        if i['symbol'] == symbol:
            return i['quantityPrecision']
    return 0

def fetch_data(symbol:str, interval:str, last:int = 50) -> pd.DataFrame:
    """
    Get data

    This function requests the Binance API for the 'last' number of candles.

    Args:
        symbol (str): Data symbol.
        interval (str): Data interval.
        last (int, optional): Number of steps to return starting from the present.
    
    Returns:
        pd.Dataframe: Dataframe containing the data for each step.
    """

    klines = pd.DataFrame(_commons.__client.klines(
        symbol=symbol, interval=interval, limit=last, recvWindow=_commons.__recvWindow), 
        columns=['timestamp', 
                 'Open', 
                 'High', 
                 'Low', 
                 'Close', 
                 'Volume', 
                 'Close_time', 
                 'Quote_asset_volume', 
                 'Number_of_trades', 
                 'Taker_buy_base', 
                 'Taker_buy_quote', 
                 'Ignore'])
    klines.index = klines['timestamp']

    return klines[[
        'Close',
        'Open',
        'High',
        'Low',
        'Volume'
    ]].astype(float)

def place_order(symbol:str, side:str, quantity:float, 
                stop_price:float=None, take_profit:float=None) -> tuple:
    """
    Place order

    This function set an order.

    Args:
        symbol (str): Symbol to which the order goes.
        side (str): 'BUY' or 'SELL'.
        quantity (float): Order quantity.
        stop_price (float, optional): If it is not None a 'STOP_MARKET' 
            order will be created at the value.
        take_profit (float, optional): If it is not None a 'TAKE_PROFIT_MARKET' 
            order will be created at the value.
    
    Returns:
        tuple: The values ​​of the orders are returned: 
            order, stop_loss_order, take_profit_order. 
            If it is equal to 0 it is because it was not executed correctly.
    """

    quantity =  float(str(quantity)[:str(quantity).find('.')+1+get_quantity_precision_symbol(symbol)])
    
    if quantity <= 0:
        if _commons.__logs: print('Place order error.')
        return 0, 0, 0

    order = _commons.__function(
        symbol=symbol,
        side=side,
        type='MARKET',
        quantity=quantity,
        recvWindow=_commons.__recvWindow,
    )

    stop_loss_order = 0
    take_profit_order = 0

    if stop_price != None: 
        stop_price = float(str(stop_price)[:str(stop_price).find('.')+get_quantity_precision_symbol(symbol)])

        stop_loss_order = create_order(
            symbol=symbol,
            side=side,
            type_='STOP_MARKET',
            price=stop_price,
            quantity=quantity
        )
        stop_loss_order 
    if take_profit != None:
        take_profit = float(str(take_profit)[:str(take_profit).find('.')+get_quantity_precision_symbol(symbol)])

        stop_loss_order = create_order(
            symbol=symbol,
            side=side,
            type_='TAKE_PROFIT_MARKET',
            price=take_profit,
            quantity=quantity,
        )

    if _commons.__logs: print('Place order successful.')
    return order, stop_loss_order, take_profit_order

def create_order(symbol:str, side:str, quantity:float, 
                 price:float, type_:str) -> dict:
    """
    Create a order 

    This function creates a 'type_' order.

    Args:
        symbol (str): Symbol to which the order goes.
        side (str): 'BUY' or 'SELL'.
        quantity (float): Order quantity.
        price (float): Price at which it will be executed.
        type_ (str, optional): Order type.
    
    Returns:
        dict: Order.
    """

    quantity =  float(str(quantity)[:str(quantity).find('.')+1+get_quantity_precision_symbol(symbol)])
    price = float(str(price)[:str(price).find('.')+get_quantity_precision_symbol(symbol)])

    order_ = _commons.__function(
                symbol=symbol,
                side='SELL' if side == 'BUY' else 'BUY',
                type=type_,
                stopPrice=price,
                quantity=quantity,
                # reduceOnly=True,
                closePosition=True,
                recvWindow=_commons.__recvWindow,
            )

    if _commons.__logs: print('Create order successful.')
    return order_

def cancel_order(symbol:str, id:int) -> dict:
    """
    Cancel a order

    This function cancel a order.

    Args:
        symbol (str): Symbol where the order is.
        id (int): ID of the order you want to close.
    
    Returns:
        dict: Closed order.
    """
    
    if _commons.__logs: print('Cancel order successful.')
    return _commons.__client.cancel_order(symbol=symbol,
                               orderId=str(int(id)),
                               recvWindow=_commons.__recvWindow)

def convert_to_float(data:pd.DataFrame, include:list) -> pd.DataFrame:
    """
    Convert to float

    This function converts 'data' columns to 'float'.

    Args:
        data (pd.DataFrame): The dataframe that contains those columns.
        include (list): List of column names to convert.
    
    Returns:
        pd.DataFrame: Dataframe with converted columns.
    """

    data[include] = data[include].astype(float)
    return data

def open_orders(symbol:str, id:int=None) -> pd.DataFrame:
    """
    Open orders

    This function requests open orders from the Binance API.

    Args:
        symbol (str): Symbol of orders.
        id (int, optional): All orders with this id.

    Returns:
        pd.DataFrame: The orders.
    """

    data = pd.DataFrame(_commons.__client.get_all_orders(symbol=symbol, orderId=id, 
                                              recvWindow=_commons.__recvWindow))[[
        'orderId',
        'symbol',
        'status',
        'avgPrice',
        'executedQty',
        'side',
        'positionSide',
        'stopPrice',
        'time',
        'type'
    ]]
    data = data[data['status'] == 'NEW']
    data['Type'] = data['executedQty'].apply(lambda x: 1 if float(x)>0 else 0)

    include = [
        'orderId',
        'avgPrice',
        'executedQty',
        'stopPrice',
        'time',
    ]

    return convert_to_float(data, include)

def open_trades(symbol:str) -> pd.DataFrame:
    """
    Open trades

    This function asks the Binance API for open trades on 'symbol'.

    Args:
        symbol (str): Symbol of trades.

    Returns:
        pd.DataFrame: Open trades.
    """

    data = _commons.__client.get_position_risk(symbol=symbol, recvWindow=_commons.__recvWindow)

    if not data == []:
        data = pd.DataFrame(data)[[
            'symbol',
            'markPrice',
            'entryPrice', 
            'positionAmt',
            'positionSide', 
            'unRealizedProfit',
            'updateTime',
        ]]
        extended_ = pd.DataFrame(_commons.__client.get_account_trades(symbol=symbol), 
                                columns=['time','id','side']).iloc[::-1].reset_index(drop=True)

        data['time'] = extended_['time']
        data['id'] = extended_['id']
        data['side'] = extended_['side']

        data['Type'] = data['positionAmt'].apply(lambda x: 1 if float(x)>0 else 0)

        include = [
            'time',
            'updateTime',
            'markPrice',
            'entryPrice', 
            'positionAmt',
            'unRealizedProfit',
        ]

        return convert_to_float(data, include)
    else:
        return pd.DataFrame()

def generate_more(function:callable, days:int=30) -> list:
    """
    Generate more

    This function is designed to execute the same 
        request to the API several times and obtain more data.

    Args:
        function (callable): Function where the request to the API is executed.
        days (int, optional): Number of days to request.

    Returns:
        list: Result.
    """

    data = []
    requests_days = 6

    now = datetime.now(timezone.utc)
    for i in range(days//requests_days):
        next = now-timedelta(days=requests_days)

        data.extend(function(end=int(now.timestamp() * 1000), 
                             start=int(next.timestamp() * 1000))[::-1])
        
        now = next

    days_f = days-days//requests_days*requests_days
    if days_f > 0:
        data.extend(function(
            end=int(now.timestamp() * 1000),
            start=int((now-timedelta(days=days_f)).timestamp() * 1000)
            )[::-1])

    return data

def closed_trades(symbol:str) -> pd.DataFrame:
    """
    Closed trades

    This function asks the Binance API for closed trades on 'symbol'.

    Args:
        symbol (str): Symbol of trades.

    Returns:
        pd.DataFrame: Close trades.
    """

    data = generate_more(
        lambda end, start: _commons.__client.get_account_trades(symbol=symbol, 
                                                     startTime=start, 
                                                     endTime=end))

    if not data == []:
        data =  pd.DataFrame(data)[[
            'orderId',
            'symbol',  
            'price', 
            'qty', 
            'realizedPnl',
            'commission',
            'commissionAsset',
            'side', 
            'positionSide', 
            'time'
        ]] 
        include = [        
            'orderId',
            'price', 
            'qty', 
            'realizedPnl',
            'commission',
            'time'
            ]
        
        return convert_to_float(data, include)
    else:
        return pd.DataFrame()
