
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from . import main
from main import client, __logs

recvWindow = 6000
function = client.new_order # client.new_order # client.new_order_test

def get_balance():
    """
    Get balance
    """
    info_bl = client.balance(recvWindow=recvWindow)
    for i in range(len(info_bl)):
        if info_bl[i]['asset'].upper() == 'USDT': 
            return float(info_bl[i]['availableBalance'])
        
def get_commission(symbol):
    """
    Get commission
    """
    commission_info = client.commission_rate(symbol=symbol, recvWindow=recvWindow)
    return float(commission_info['takerCommissionRate'])

def get_quantity_precision_symbol(symbol):
    """
    Get quantity precision of the symbol
    """
    for i in client.exchange_info()['symbols']:
        if i['symbol'] == symbol:
            return i['quantityPrecision']
    return 0

def fetch_data(symbol, interval, last=50):
    """
    Get the last candle data.
    """
    klines = pd.DataFrame(client.klines(
        symbol=symbol, interval=interval, limit=last, recvWindow=recvWindow), 
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
        if __logs: print('Place order error.')
        return 0, 0, 0

    order = function(
        symbol=symbol,
        side=side,
        type='MARKET',
        quantity=quantity,
        recvWindow=recvWindow,
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

    if __logs: print('Place order successful.')
    return order, stop_loss_order, take_profit_order

def create_order(symbol, side, quantity, price, type):
    """
    Create a order 
    """
    quantity =  float(str(quantity)[:str(quantity).find('.')+1+get_quantity_precision_symbol(symbol)])
    price = float(str(price)[:str(price).find('.')+get_quantity_precision_symbol(symbol)])

    order_ = function(
                symbol=symbol,
                side='SELL' if side == 'BUY' else 'BUY',
                type=type,
                stopPrice=price,
                quantity=quantity,
                # reduceOnly=True,
                closePosition=True,
                recvWindow=recvWindow,
            )

    if __logs: print('Create order successful.')
    return order_

def cancel_order(symbol, id):
    
    if __logs: print('Cancel order successful.')
    return client.cancel_order(symbol=symbol,
                               orderId=str(int(id)),
                               recvWindow=recvWindow)

def convert_to_float(data, include):
    data[include] = data[include].astype(float)
    return data

def open_orders(symbol, id):
    data = pd.DataFrame(client.get_all_orders(symbol=symbol, orderId=id, 
                                              recvWindow=recvWindow))[[
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
    data = client.get_position_risk(symbol=symbol, recvWindow=recvWindow)

    if not data == []:
        data = pd.DataFrame(data)[[
            'symbol',
            'markPrice',
            'entryPrice', 
            'positionAmt',
            'positionSide', 
            'unRealizedProfit'
        ]]
        extended_ = pd.DataFrame(client.get_account_trades(symbol=symbol), 
                                columns=['time','id','side'])

        data['time'] = extended_['time']
        data['id'] = extended_['id']
        data['side'] = extended_['side']

        data['Type'] = data['positionAmt'].apply(lambda x: 1 if float(x)>0 else 0)

        include = [
            'markPrice',
            'entryPrice', 
            'positionAmt',
            'unRealizedProfit'
        ]

        return convert_to_float(data, include)
    else:
        return pd.DataFrame()

def generate_more(function, days=30):
    data = []
    requests = 6

    now = datetime.now()
    for i in range(days//requests):
        next = now-timedelta(days=5)

        data.extend(function(end=int(now.timestamp() * 1000), 
                             start=int(next.timestamp() * 1000)))
        
        now = next

    days_f = days-days//requests*5
    if days_f > 0:
        data.extend(function(
            end=int(now.timestamp() * 1000),
            start=int((now-timedelta(days=days_f)).timestamp() * 1000)
            ))

    return data

def close_trades(symbol):
    data = generate_more(
        lambda end, start: client.get_account_trades(symbol=symbol, 
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
