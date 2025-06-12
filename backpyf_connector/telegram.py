"""
Telegram module.

This module contains everything needed to run the Telegram bot.

Functions:
    bot_init: Run the Telegram bot.
    inter_log: Send the log to the Telegram bot.
    on_startup: Configuration before starting the bot.
    start: Strart command sends a test text.
    send_event: Send the logs to the chat.
    help_command: Send a text with documentation of the commands.
    chatid_command: Send the telegram chat id.
    sistem_command: Send account balance and open trades data.
    last_command: Send all logs that were sent.
    ip_command: Send the public IP of the machine.
    off_command: Command to shut down the system.
"""

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from backpyf.utils import text_fix
from telegram import Update
from sys import exit
import asyncio

from . import tradetools as tools
from . import _commons as _cm
from . import main

def bot_init(api_key:str) -> None:
    """
    Bot init

    Run the Telegram bot.

    Args:
        api_key (str): Telegram bot api key.
    """

    _cm.__loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_cm.__loop)

    app = Application.builder().token(api_key).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatid", chatid_command))
    app.add_handler(CommandHandler("sistem",sistem_command))
    app.add_handler(CommandHandler("last", last_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("off", off_command))
    
    _cm.__loop.run_until_complete(on_startup(app))

    main.print_log("Bot started.")
    app.run_polling()

def inter_log(log:str, alert:bool) -> None:
    """
    Inter log

    Send the log to the Telegram bot.

    Args:
        log (str): Log message.
        alert (bool): True if you want it to be sent as an alert.
    """

    if alert and not _cm.__bot is None and _cm.__alert:
        _cm.__loop.create_task(send_event(log))

async def on_startup(app) -> None:
    """
    On startup

    It runs just before starting the bot.
        Configure the log broker to send logs correctly to the Telegram bot.

    Args:
        app: Bot application.
    """

    if not _cm.__chat_id: return
    
    _cm.__bot = app.bot
    await _cm.__bot.send_message(chat_id=_cm.__chat_id, 
                                 text="Hi! I'm your trading system 🤖\n/help to see more commands.")

    _cm.__inter_log = inter_log

async def start(update: Update, context: CallbackContext) -> None:
    """
    Start

    Strart command sends a test text.
    """

    await update.message.reply_text(
        "Hi! I'm your trading system 🤖\n/help to see more commands.")
    
async def send_event(message:str):
    """
    Send event

    Send the logs to the chat.

    Args:
        str: Message to send.
    """

    await _cm.__bot.send_message(chat_id=_cm.__chat_id, text=message)

async def help_command(update: Update, context: CallbackContext) -> None:
    """
    Help command

    Send a text with documentation of the commands.
    """

    await update.message.reply_text(text_fix(
        """
        Available commands:
        /start - Start the bot.
        /help - Get help.
        /sistem - Get active trading systems.
        /last - Get the latest system logs.
        /ip - Get the system's current IP address.
        /chatid - Get your id to config.
        /off - Turn off the systems and the bot.
        """, False))

async def chatid_command(update: Update, context: CallbackContext) -> None:
    """
    Chat id command

    Send the telegram chat id.
    """

    await update.message.reply_text(text_fix(
        f"""
        This chat id is: '{update.effective_chat.id}'
        """, False))

async def sistem_command(update: Update, context: CallbackContext) -> None:
    """
    Sistem command

    Send account balance and open trades data.
    """

    if _cm.__client is None:
        main.print_log("Client not found.", alert=True)
        await update.message.reply_text("System not executed.")
        return
    elif _cm.__instances is None:
        await update.message.reply_text("System not executed.")
        return

    open_trades = tools.open_trades(_cm.__symbol)
    trades = "".join(
        f"\nTrade: {i+1} [\nentryPrice: {open_trades.iloc[i]['entryPrice']}\npositionAmt: {open_trades.iloc[i]['positionAmt']}\ntype: {open_trades.iloc[i]['Type']}]" for i in open_trades.index)

    instances_names = "\n".join(_cm.__instances)
    await update.message.reply_text(text_fix(
        f"""
        Active trading systems:
        {instances_names}
        System Statistics:
        Balance: {round(tools.get_balance(), 2)}
        Commission: {tools.get_commission(_cm.__symbol)}
        Trades: {trades}
        """, False))

async def last_command(update: Update, context: CallbackContext) -> None:
    """
    Last command

    Send all logs that were sent.
    """

    logs = "".join(
        f"{i[0].strftime('%Y-%m-%d %H:%M:%S')}: '{i[1]}'\n" for i in _cm.__rec[::-1])
    
    await update.message.reply_text(text_fix(
        f"""
        Last logs:
        {logs}
        """, False))

async def ip_command(update: Update, context: CallbackContext) -> None:
    """
    Ip command

    Send the public IP of the machine only 
        if the chatid is the same as '_cm.__chat_id'.
    """

    if str(update.effective_chat.id) != str(_cm.__chat_id):
        main.print_log("Ip request, chat id does not match.", alert=True)
        await update.message.reply_text("Chat id does not match.")
        return
    
    await update.message.reply_text(text_fix(
        f"""
        Current IP: {_cm.__ip_acc}
        Do not share this information with anyone.
        """, False))

async def off_command(update: Update, context: CallbackContext) -> None:
    """
    Off command

    Command to shut down the system.
    """

    _cm.__main_loop = False
    _cm.__instances = None

    _cm.__inter_log = None
    await update.message.reply_text("All systems have been shut down.")
    main.print_log("Bot turned off.")

    exit()
