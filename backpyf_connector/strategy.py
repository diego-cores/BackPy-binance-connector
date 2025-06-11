
import backpyf.exception as exception
import backpyf.utils as utils
import backpyf as bk

import numpy as np
import pandas as pd

from . import tradetools as tools

class StrategyClassReal(bk.StrategyClass):
    def __init__(self, symbol, interval, width, commission:float = 0) -> None: 
        """
        __init__

        Builder for initializing the class.

        Args:
            data (pd.DataFrame): All data from the step and previous ones.
            commission (float): Commission per trade.
        """
        
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None
        self.date = None

        self._StrategyClass__data = pd.DataFrame()

        self._StrategyClass__commission = commission
        self._StrategyClass__init_funds = None

        self._StrategyClass__trades_ac = None
        self._StrategyClass__trades_cl = None

        self.interval =  interval
        self.width = width
        self.icon = symbol

    def __trades_updater(self, commission:float = None):
        """
        Update trades variables
        """
        self._StrategyClass__trades_ac = tools.open_trades(symbol=self.icon)
        self._StrategyClass__trades_cl = tools.close_trades(symbol=self.icon)

        self._StrategyClass__init_funds = tools.get_balance()
        if not commission is None: 
            self._StrategyClass__commission = commission

    def __data_updater(self, data:pd.DataFrame) -> None:
        """
        Data updater

        Updates all data with the provided DataFrame.

        Args:
            data (pd.DataFrame): All data from the step and previous ones.
        """

        if data.empty:
            raise exception.StyClassError('Data is empty.')

        self.open = data["Open"].iloc[-1]
        self.high = data["High"].iloc[-1]
        self.low = data["Low"].iloc[-1]
        self.close = data["Close"].iloc[-1]
        self.volume = data["Volume"].iloc[-1]
        self.date = data.index[-1]+self.width

        self._StrategyClass__data = data

    def __before(self, data = pd.DataFrame(), commission:float = None):
        """
        Before

        This function is used to run trades and other operations.

        Args:
            data (pd.DataFrame): Data from the current and previous steps.
        """
        if not data.empty:
            self.__data_updater(data=data)
            self.__trades_updater(commission=commission)

        self.next()
        self.__trades_updater()

        return self._StrategyClass__trades_ac, self._StrategyClass__trades_cl
    
    def prev(self, label:str = None, last:int = None) -> pd.DataFrame:
        """
        Prev

        This function returns the values of `data`.
        
        Args:
            label (str, optional): Data column to return. If None, all columns 
                are returned. If 'index', only indexes are returned, ignoring 
                the `last` parameter.
            last (int, optional): Number of steps to return starting from the 
                present. If None, data for all times is returned.

        Info:
            `data` columns.

            - Open: The 'Open' price of the step.
            - High: The 'High' price of the step.
            - Low: The 'Low' price of the step.
            - Close: The 'Close' price of the step.
            - Volume: The 'Volume' of the step.
            - index: The 'Index' of the step.

        Returns:
            pd.Dataframe: Dataframe containing the data of previous steps.
        """

        return super().prev(label=label, last=last)
    
    def prev_trades_cl(self, label:str = None, last:int = None) -> pd.DataFrame:
        """
        Prev of trades closed

        This function returns the values of `trades_cl`.

        Args:
            label (str, optional): Data column to return. If None, all columns 
                are returned. If 'index', only indexes are returned, ignoring 
                the `last` parameter.
            last (int, optional): Number of steps to return starting from the 
                present. If None, data for all times is returned.

        Info:
            `__trades_cl` columns, the same columns you can access with 
            `prev_trades_ac`.

            - Date: The step date when the trade began.
            - Close: The 'Close' price at the trade's start.
            - Low: The lowest price at the trade's start.
            - High: The highest price at the trade's start.
            - StopLoss: The stop loss position.
            - TakeProfit: The take profit position.
            - PositionClose: The 'Close' price when the trade ends.
            - PositionDate: The step date when the trade ends.
            - Amount: Chosen amount.
            - ProfitPer: Trade profit in percentage.
            - Profit: Trade profit based on amount.
            - Type: Type of trade.

        Returns:
            pd.Dataframe: Dataframe containing the data from closed trades.
        """

        return super().prev_trades_cl(label=label, last=last)
    
    def prev_trades_ac(self, label:str = None, last:int = None) -> pd.DataFrame:
        """
        Prev of trades active

        This function returns the values of `trades_ac`.

        Args:
            label (str, optional): Data column to return. If None, all columns 
                are returned. If 'index', only indexes are returned, ignoring 
                the `last` parameter.
            last (int, optional): Number of steps to return starting from the 
                present. If None, data for all times is returned.

        Info:
            `__trades_ac` columns, the same columns you can access with 
            `prev_trades_cl`.

            - Date: The step date when the trade began.
            - Close: The 'Close' price at the trade's start.
            - Low: The lowest price at the trade's start.
            - High: The highest price at the trade's start.
            - StopLoss: The stop loss position.
            - TakeProfit: The take profit position.
            - Amount: Chosen amount.
            - Type: Type of trade.
        
        Returns:
            pd.Dataframe: Dataframe containing the data from active trades.
        """

        return super().prev_trades_ac(label=label, last=last)
    
    def act_open(self, type:bool = 1, stop_loss:int = np.nan, 
                 take_profit:int = np.nan, amount:int = np.nan) -> None:
        """
        Opens an action for trading (REAL)

        This function opens a long or short position. 

        Note:
            If you leave your position without 'stop loss' and 'takeprofit', 
            your trade will be counted as closed, and you can't modify or close it.

        Args:
            type (bool): 0 for sell, 1 for buy. Other values Python evaluates 
                as booleans are supported.
            stop_loss (int): Price for stop loss. If np.nan or None, no stop loss 
                will be set.
            take_profit (int): Price for take profit. If np.nan or None, no take 
                profit will be set.
            amount (int): Amount of points for the trade.
        """

        # Convert to boolean.
        type = int(bool(type))

        # Check if 'stop_loss' or 'take_profit' is None.
        stop_loss = stop_loss or np.nan
        take_profit = take_profit or np.nan

        # Check exceptions.
        if not type in {1,0}: 
            raise exception.ActionError("'type' only 1 or 0.")
        elif amount < 0: 
            raise exception.ActionError(
                "'amount' can only be a positive number.")
        elif ((type and (self._StrategyClass__data["Close"].iloc[-1] <= stop_loss or 
                       self._StrategyClass__data["Close"].iloc[-1] >= take_profit)) or 
            (not type and (self._StrategyClass__data["Close"].iloc[-1] >= stop_loss or 
                           self._StrategyClass__data["Close"].iloc[-1] <= take_profit))): 

            raise exception.ActionError(
                utils.text_fix("""
                               'stop_loss' or 'take_profit' 
                               incorrectly configured for the position type.
                               """, newline_exclude=True))
        # Create new trade.
        order_, order_stop, order_take = tools.place_order(
            symbol=self.icon, 
            side='BUY' if type else 'SELL', 
            quantity=amount, 
            stop_price=(stop_loss if not np.isnan(stop_loss) else None),
            take_profit=(take_profit if not np.isnan(take_profit) else None))

        if not order_:
            raise exception.ActionError("Position not active.")

        self.__trades_updater()
        return order_, order_stop, order_take
    
    def act_close(self, index:int = 0) -> None:
        """
        Close an active trade

        Args:
            index (int): The index of the active trade you want to close.
        """

        # Check exceptions.
        if self._StrategyClass__trades_ac.empty: 
            raise exception.ActionError('There are no active trades.')
        elif not index in self._StrategyClass__trades_ac.index.to_list(): 
            raise exception.ActionError('Index does not exist.')
        # Close action.
        return self.__act_close(index=index)

    def __act_close(self, index:int = 0) -> None:
        """
        Close an active trade (REAL)

        Note:
            This is a hidden function intended to prevent user modification.
            It does not include exception handling.
        """

        # Get trade to close.
        trade = self._StrategyClass__trades_ac.iloc[lambda x: x.index==index].copy()
        trade = trade.iloc[-1]

        # Close position.
        order_, order_stop, order_take = tools.place_order(
            symbol=self.icon, 
            side='SELL' if trade['Type'] else 'BUY', 
            quantity=trade['positionAmt']
            )
        
        orders = tools.open_orders(symbol=self.icon, id=trade['id'])

        if not orders['orderId'].empty:
            orders.apply(lambda x: tools.cancel_order(self.icon,x['orderId']) 
                         if x['symbol'] == 'BTCUSDT' and 
                         x['type'] in ('STOP_MARKET','TAKE_PROFIT_MARKET') 
                         else None, axis=1)

        if not order_:
            raise exception.ActionError("Position not active.")

        self.__trades_updater()
        return order_, order_stop, order_take

    def act_mod(self, index:int = 0, new_stop:int = None, 
                new_take:int = None) -> None:
        """
        Modify an active trade (REAL)

        Note:
            If an invalid stop loss or take profit is provided, the program will
            return None and will not execute any changes.

        Args:
            index (int): The index of the active trade to modify.
            new_stop (int or None): New stop loss price. If None, stop loss will
                not be modified. If np.nan, stop loss will be removed.
            new_take (int or None): New take profit price. If None, take profit 
                will not be modified. If np.nan, take profit will be removed.
        """
        
        # Check exceptions.
        if self._StrategyClass__trades_ac.empty: 
            raise exception.ActionError('There are no active trades.')
        elif not (new_stop or new_take): 
            raise exception.ActionError('Nothing was changed.')
        # Get trade to modify.
        trade = self._StrategyClass__trades_ac.loc[index]
        # Set new stop.
        if new_stop and ((new_stop < self._StrategyClass__data["Close"].iloc[-1] and 
                          trade['Type']) or (not trade['Type'] and 
                                             new_stop > self.close) or 
                                             np.isnan(new_stop)): 
            old_order = tools.open_orders(symbol=self.icon, id=trade['id'])
            old_order = old_order[old_order['type'] == 'STOP_MARKET']

            if not old_order.empty:
                tools.cancel_order(symbol=self.icon, id=old_order.iloc[-1]['orderId'])

            order_ = tools.create_order(
                symbol=self.icon,
                side='SELL' if trade['side'] == 'BUY' else 'BUY',
                quantity=trade['positionAmt'],
                price=new_stop,
                type='STOP_MARKET'
            )

        # Set new take.
        if new_take and ((new_take > self._StrategyClass__data["Close"].iloc[-1] 
                          and trade['Type']) or (not trade['Type'] and 
                                                 new_take < self.close) or 
                                                 np.isnan(new_take)): 
            old_order = tools.open_orders(symbol=self.icon, id=trade['id'])
            old_order = old_order[old_order['type'] == 'TAKE_PROFIT_MARKET']

            if not old_order.empty:
                tools.cancel_order(symbol=self.icon, id=old_order.iloc[-1]['orderId'])

            order_ = tools.create_order(
                symbol=self.icon,
                side='SELL' if trade['side'] == 'BUY' else 'BUY',
                quantity=trade['positionAmt'],
                price=new_take,
                type='TAKE_PROFIT_MARKET'
            )
        
        self.__trades_updater()
        return order_
