"""
Strategy module.

This module contains the strategy you need to inherit to connect your strategy to real.

Classes:
    StrategyClassReal: Inherit this class to keep documentation and features up to date.
"""

import backpyf.exception as exception
import backpyf.utils as utils
import backpyf as bk

from backpyf.main import flx

import numpy as np
import pandas as pd

from . import tradetools as tools

class StrategyClassReal(bk.StrategyClass):
    """
    StrategyClassReal.

    This is the class you have to inherit to automate your strategy.

    To use the functions, use the `self` instance. Create your strategy 
    within the `StrategyClassReal.next()` structure.

    Attributes:
        open: Last 'Open' value from `data`.
        high: Last 'High' value from `data`.
        low: Last 'Low' value from `data`.
        close: Last 'Close' value from `data`.
        volume: Last 'Volume' value from `data`.
        date: Last index from `data`.
        interval: Data interval from `__interval`.
        width: Data width from `__width`.
        icon: Data icon from `__symbol`.

    Private Attributes:
        __data_icon: Data icon from `__symbol`.
        __data: DataFrame containing all data of steps.
        __commission: Commission by order.
        __init_funds: Account balance.
        __trades_ac: DataFrame for open trades.
        __trades_cl: DataFrame for closed trades.
        

    Methods:
        get_init_funds: Returns '__init_funds'.
        get_commission: Returns '__commission'.
        act_mod: Modifies an existing trade.
        act_close: Closes an existing trade.
        act_open: Opens a new trade.
        prev_trades_ac: Returns active trades.
        prev_trades_cl: Returns closed trades.
        prev_orders: This function returns open orders.
        prev: Recovers all step data.

    Private Methods:
        __act_close: Closes an existing trade.
        __before: This function is used to run trades and other operations.
        __trades_ac_get: This function sets the 
            variable '__trades_ac' if it is None.
        __trades_cl_get: This function sets the 
            variable '__trades_cl' if it is None.
        __get_funds: This function sets the
            variable '__init_funds' if it is None.
        __trades_updater: Updates the active and closed trades variables.
        __data_updater: Updates all data with the provided DataFrame.
    """

    def __init__(self, symbol:str, interval:str, 
                 width:float, commission:float) -> None: 
        """
        __init__

        Builder for initializing the class.

        Args:
            symbol (str): Data symbol.
            interval (str): Data interval.
            width (float): Width of each step.
            commission (float): Commission by order
        """
        
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None
        self.date = None

        self.__data_icon = symbol
        self._StrategyClass__data = pd.DataFrame()

        self._StrategyClass__commission = commission
        self._StrategyClass__init_funds = None

        self._StrategyClass__trades_ac = None
        self._StrategyClass__trades_cl = None

        self.interval =  interval
        self.width = width
        self.icon = symbol

    def get_init_funds(self) -> None:
        """{}""".format(self.__class__.__bases__[0].get_init_funds.__doc__)

        self.__get_funds()
        return super().get_init_funds()

    def __trades_ac_get(self) -> None:
        """
        Get active trades

        This function sets the variable '__trades_ac' if it is None.
        """

        if self._StrategyClass__trades_ac is None:
            self._StrategyClass__trades_ac = tools.open_trades(symbol=self.__data_icon)

    def __trades_cl_get(self) -> None:
        """
        Get closed trades

        This function sets the variable '__trades_cl' if it is None.
        """

        if self._StrategyClass__trades_cl is None:
            self._StrategyClass__trades_cl = tools.closed_trades(symbol=self.__data_icon)

    def __get_funds(self) -> None:
        """
        Get funds

        This function sets the variable '__init_funds' if it is None.
        """

        if self._StrategyClass__init_funds is None:
            self._StrategyClass__init_funds = tools.get_balance()

    def __trades_updater(self, commission:float = None) -> None:
        """
        Update trades variables

        Updates the active and closed trades variables.

        Args:
            commission (float): Current Commission.
        """

        self._StrategyClass__trades_ac = None
        self._StrategyClass__trades_cl = None

        self._StrategyClass__init_funds = None
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

    def __before(self, data = pd.DataFrame(), commission:float = None) -> None:
        """
        Before

        This function is used to run trades and other operations.

        Args:
            data (pd.DataFrame): Data from the current and previous steps.
            commission (float, optional): Commission by order.
        """

        if not data.empty:
            self.__data_updater(data=data)
            self.__trades_updater(commission=commission)

        self.next()

    def prev(self, label:str = None, last:int = None) -> flx.DataWrapper:
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

        Returns:
            DataWrapper: DataWrapper containing the data of previous steps.
        """

        return super().prev(label=label, last=last)

    def prev_orders(self, id:int = None, type_:str = None, 
                    label:str = None, last:int = None) -> flx.DataWrapper:
        """
        Prev orders

        This function returns open orders.

        Args:
            id (int, optional): Filter operations by ID.
            type_ (str, optional): Filter operations by 'type' value.
            label (str, optional): Data column to return. If None, all columns 
                are returned. If 'index', only indexes are returned, ignoring 
                the `last` parameter.
            last (int, optional): Number of steps to return starting from the 
                present. If None, data for all times is returned.

        Info:
            - orderId: Id of the order.
            - symbol: Symbol of the order.
            - status: Current status of the order.
            - avgPrice: Price at which the order was executed.
            - executedQty: Amount in 'symbol' of the position.
            - side: Order side.
            - positionSide: Position mode.
            - stopPrice: Execution price.
            - time: Order date.
            - type: Order type.
            - Type: Position type if 'executedQty' is positive it is 1 if it is negative 0.

        Returns:
            DataWrapper: DataWrapper containing the data of orders.
        """

        __orders = tools.open_orders(symbol=self.__data_icon, id=id)
        if label == 'index': 
            return flx.DataWrapper(__orders.index, columns='index')
        elif __orders.empty: 
            return flx.DataWrapper()

        if (last != None and 
              (last <= 0 or last > self.__data["Close"].shape[0])): 
            raise ValueError(utils.text_fix("""
                            Last has to be less than the length of 
                            'data' and greater than 0.
                            """, newline_exclude=True))

        if type_ != None:
            __orders = __orders[__orders['type'] == type_]

        data_columns = __orders.columns
        data = __orders.values[
            len(__orders) - last if last is not None and last < len(__orders) else 0:]

        if label != None: 
            _loc = __orders.columns.get_loc(label)

            data_columns = data_columns[_loc]
            data = data[:,_loc]

        return flx.DataWrapper(data, columns=data_columns)

    def prev_trades_cl(self, label:str = None, last:int = None) -> flx.DataWrapper:
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
            - orderId: Id of the order.
            - symbol: Symbol of the order.
            - price: Executed price.
            - qty: Amount in 'symbol' of the order.
            - realizedPnl: Pnl realized.
            - commission: Commission charged.
            - commissionAsset: Asset on which the commission was charged.
            - side: Order side.
            - positionSide: Position mode.
            - time: Executed time.

        Returns:
            DataWrapper: DataWrapper containing the data from closed trades.
        """

        self.__trades_cl_get()
        return super().prev_trades_cl(label=label, last=last)

    def prev_trades_ac(self, label:str = None, last:int = None) -> flx.DataWrapper:
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
            - symbol: Symbol of the position.
            - markPrice: Mark price.
            - entryPrice: Entry price.
            - positionAmt: Amount in 'symbol' of the position.
            - positionSide: Position mode.
            - unRealizedProfit: Pnl unrealized.
            - updateTime: Date of last position update.
            - time: Date of the opening order.
            - id: Id of the order.
            - side: Position side.
            - Type: Position type.

        Returns:
            DataWrapper: DataWrapper containing the data from active trades.
        """

        self.__trades_ac_get()
        return super().prev_trades_ac(label=label, last=last)

    def act_open(self, type:bool = 1, stop_loss:int = np.nan, 
                 take_profit:int = np.nan, amount:int = np.nan) -> tuple:
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

        Return:
            tuple: order, stop order, take profit order
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
            symbol=self.__data_icon, 
            side='BUY' if type else 'SELL', 
            quantity=amount, 
            stop_price=(stop_loss if not np.isnan(stop_loss) else None),
            take_profit=(take_profit if not np.isnan(take_profit) else None))

        if not order_:
            raise exception.ActionError("Position not active.")

        self.__trades_updater()
        return order_, order_stop, order_take
    
    def act_close(self, index:int = 0) -> tuple:
        """
        Close an active trade (REAL)

        Args:
            index (int): The index of the active trade you want to close.

        Return:
            tuple: order, stop order, take profit order
        """

        # Set __trades_ac.
        self.__trades_ac_get()

        # Check exceptions.
        if self._StrategyClass__trades_ac.empty: 
            raise exception.ActionError('There are no active trades.')
        elif not index in self._StrategyClass__trades_ac.index.to_list(): 
            raise exception.ActionError('Index does not exist.')
        # Close action.
        return self.__act_close(index=index)

    def __act_close(self, index:int = 0) -> tuple:
        """
        Close an active trade (REAL)

        Note:
            This is a hidden function intended to prevent user modification.
            It does not include exception handling.
        """

        # Set __trades_ac.
        self.__trades_ac_get()

        # Get trade to close.
        trade = self._StrategyClass__trades_ac.iloc[lambda x: x.index==index].copy()
        trade = trade.iloc[-1]

        # Close position.
        order_, order_stop, order_take = tools.place_order(
            symbol=self.__data_icon, 
            side='SELL' if trade['Type'] else 'BUY', 
            quantity=trade['positionAmt']
            )
        
        orders = tools.open_orders(symbol=self.__data_icon, id=trade['id'])

        if not orders['orderId'].empty:
            orders.apply(lambda x: tools.cancel_order(self.__data_icon,x['orderId']) 
                         if x['symbol'] == 'BTCUSDT' and 
                         x['type'] in ('STOP_MARKET','TAKE_PROFIT_MARKET') 
                         else None, axis=1)

        if not order_:
            raise exception.ActionError("Position not active.")

        self.__trades_updater()
        return order_, order_stop, order_take

    def act_mod(self, index:int = 0, new_stop:int = None, 
                new_take:int = None) -> tuple:
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

        Return:
            tuple: stop order, take profit order
        """

        # Set __trades_ac.
        self.__trades_ac_get()

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
            old_order = tools.open_orders(symbol=self.__data_icon, id=trade['id'])
            old_order = old_order[old_order['type'] == 'STOP_MARKET']

            if not old_order.empty:
                tools.cancel_order(symbol=self.__data_icon, id=old_order.iloc[-1]['orderId'])

            order_stop = tools.create_order(
                symbol=self.__data_icon,
                side='SELL' if trade['side'] == 'BUY' else 'BUY',
                quantity=trade['positionAmt'],
                price=new_stop,
                type_='STOP_MARKET'
            )

        # Set new take.
        if new_take and ((new_take > self._StrategyClass__data["Close"].iloc[-1] 
                          and trade['Type']) or (not trade['Type'] and 
                                                 new_take < self.close) or 
                                                 np.isnan(new_take)): 
            old_order = tools.open_orders(symbol=self.__data_icon, id=trade['id'])
            old_order = old_order[old_order['type'] == 'TAKE_PROFIT_MARKET']

            if not old_order.empty:
                tools.cancel_order(symbol=self.__data_icon, id=old_order.iloc[-1]['orderId'])

            order_take = tools.create_order(
                symbol=self.__data_icon,
                side='SELL' if trade['side'] == 'BUY' else 'BUY',
                quantity=trade['positionAmt'],
                price=new_take,
                type='TAKE_PROFIT_MARKET'
            )
        
        self.__trades_updater()
        return order_stop, order_take
