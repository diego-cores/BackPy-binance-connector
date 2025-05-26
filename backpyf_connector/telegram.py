
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from backpyf.utils import text_fix
from telegram import Update
from sys import exit
import asyncio

from . import tradetools as tools
from . import _commons as _cm
from . import main

def bot_init(api_key):
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    _cm.__loop.run_until_complete(on_startup(app))

    main.print_log("Bot started.")
    app.run_polling()

def inter_log(log, alert):
    if alert and not _cm.__bot is None and _cm.__alert:
        _cm.__loop.create_task(send_event(log))

async def on_startup(app):
    if not _cm.__chat_id: return
    
    _cm.__bot = app.bot
    await _cm.__bot.send_message(chat_id=_cm.__chat_id, 
                                 text="Hi! I'm your trading system 🤖\n/help to see more commands.")

    _cm.__inter_log = inter_log

async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(update.message.text)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Hi! I'm your trading system 🤖\n/help to see more commands.")
    
async def send_event(message):
    await _cm.__bot.send_message(chat_id=_cm.__chat_id, text=message)

async def help_command(update: Update, context: CallbackContext) -> None:
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
    await update.message.reply_text(text_fix(
        f"""
        This chat id is: '{update.effective_chat.id}'
        """, False))

async def sistem_command(update: Update, context: CallbackContext) -> None:
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
    logs = "".join(
        f"{i[0].strftime('%Y-%m-%d %H:%M:%S')}: '{i[1]}'\n" for i in _cm.__rec[::-1])
    
    await update.message.reply_text(text_fix(
        f"""
        Last logs:
        {logs}
        """, False))

async def ip_command(update: Update, context: CallbackContext) -> None:
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
    _cm.__main_loop = False
    _cm.__instances = None

    args = context.args
    if '--sistem' in args:
        await update.message.reply_text("Active sistems have been shut down.")
        main.print_log("Sistem turned off.")
        return

    _cm.__inter_log = None
    await update.message.reply_text("All systems have been shut down.")
    main.print_log("Bot turned off.")

    exit()
