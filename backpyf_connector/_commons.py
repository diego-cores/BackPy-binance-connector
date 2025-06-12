"""
Commons hidden module

This module contains all global variables for better manipulation.

Hidden Variables:
    __ip_acc: (hidden variable).
    __client: (hidden variable).
    __logs: If set to False, simple logs will not be saved or printed (hidden variable).
    __alert: If set to False alerts will not be sent (hidden variable).
    __rec: (hidden variable).
    __rec_limit: (hidden variable).
    __symbol: (hidden variable).
    __ps_type: (hidden variable).
    __interval: (hidden variable).
    __leverage: (hidden variable).
    __data: (hidden variable).
    __width: (hidden variable).
    __trades: (hidden variable).
    __function: (hidden variable).
    __recvWindow: (hidden variable).
    __inter_log: (hidden variable).
    __instances: (hidden variable).
    __main_loop: (hidden variable).
    __bot: (hidden variable).
    __loop: (hidden variable).
    __chat_id: (hidden variable).
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
__trades = None

__function = None
__recvWindow = 6000

__inter_log = None
__instances = None
__main_loop = True

__bot = None
__loop = None
__chat_id = ""
