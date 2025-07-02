"""
Commons hidden module

This module contains all global variables for better manipulation.

Hidden Variables:
    __ip_acc: Current public IP of the machine (hidden variable).
    __client: Binance client (hidden variable).
    __logs: If set to False, simple logs will not be 
        saved or printed (hidden variable).
    __alert: If set to False alerts will not be sent (hidden variable).
    __rec: Log history (hidden variable).
    __rec_limit: Log history limit (hidden variable).
    __symbol: Symbol currently configured (hidden variable).
    __ps_type: Binance Margin Type currently configured (hidden variable).
    __interval: Data interval (hidden variable).
    __leverage: Leverage currently configured (hidden variable).
    __data: Market data (hidden variable).
    __width: Value of the width of each candle (hidden variable).
    __function: Function used to create a new order, it is saved so 
        that it can be changed to a test order (hidden variable).
    __recvWindow: Maximum time in ms that a request to the 
        Binance API can take (hidden variable).
    __inter_log: Intermediary function for logs, used to send 
        logs to the Telegram bot (hidden variable).
    __instances: Name of the instances of open strategies (hidden variable).
    __main_loop: Main loop in 'generate_loop' if it returns 
        'False' it will stop (hidden variable).
    __bot: Telegram bot (hidden variable).
    __loop: Telegram bot event loop (hidden variable).
    __chat_id: Telegram chat ID to be able to send logs and 
        things automatically. (hidden variable).
"""

__ip_acc = None
__client = None

__logs = True
__alert = True

__rec = []
__rec_limit = 10

__symbol = None
__ps_type = None
__interval = None
__leverage = None

__data = None
__width = None

__function = None
__recvWindow = 6000

__inter_log = None
__instances = None
__main_loop = True

__bot = None
__loop = None
__chat_id = ""
