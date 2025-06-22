
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
    Get the last candle data.

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

def place_order(symbol, side, quantity, stop_price=None, take_profit=None):
    """
    Set an order with proper precision.
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
            type='STOP_MARKET',
            price=stop_price,
            quantity=quantity
        )
        stop_loss_order 
    if take_profit != None:
        take_profit = float(str(take_profit)[:str(take_profit).find('.')+get_quantity_precision_symbol(symbol)])

        stop_loss_order = create_order(
            symbol=symbol,
            side=side,
            type='TAKE_PROFIT_MARKET',
            price=take_profit,
            quantity=quantity,
        )

    if _commons.__logs: print('Place order successful.')
    return order, stop_loss_order, take_profit_order

def create_order(symbol, side, quantity, price, type):
    """
    Create a order 
    """
    quantity =  float(str(quantity)[:str(quantity).find('.')+1+get_quantity_precision_symbol(symbol)])
    price = float(str(price)[:str(price).find('.')+get_quantity_precision_symbol(symbol)])

    order_ = _commons.__function(
                symbol=symbol,
                side='SELL' if side == 'BUY' else 'BUY',
                type=type,
                stopPrice=price,
                quantity=quantity,
                # reduceOnly=True,
                closePosition=True,
                recvWindow=_commons.__recvWindow,
            )

    if _commons.__logs: print('Create order successful.')
    return order_

def cancel_order(symbol, id):
    """
    Cancel a order
    """
    
    if _commons.__logs: print('Cancel order successful.')
    return _commons.__client.cancel_order(symbol=symbol,
                               orderId=str(int(id)),
                               recvWindow=_commons.__recvWindow)

def convert_to_float(data, include):
    """
    Convert to float
    """

    data[include] = data[include].astype(float)
    return data

def open_orders(symbol, id=None):
    """
    Open orders
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

def open_trades(symbol):
    """
    Open trades
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

def generate_more(function, days=30):
    """
    Generate more
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

def close_trades(symbol):
    """
    Close trades
    """

    data = generate_more(
        lambda end, start: _commons.__client.get_account_trades(symbol=symbol, 
                                                     startTime=start, 
                                                     endTime=end), days=30)

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
