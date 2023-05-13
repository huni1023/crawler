r"""
Todo. 다른 코드를 복붙해둔 것임
크롤러용 텔레그램 봇도 하나 만들어서 config 정보 수정하면 될듯
"""

import os
import sys
import logging
import asyncio
import traceback
import html
import json
from datetime import datetime
from datetime import date
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from read_save import load_config

# limit package version
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )


# load config
config = load_config('config.yaml')
chat_id = config['chat_id']
teleBot_token = config['teleBot_token']

class TelegramBot:
    def __init__(self, chat_id, token, init_date, init_time):
        r"""
        """
        self.telegram_token = token
        self.chat_id = chat_id
        self.bot = Application.builder().token(self.telegram_token).build()
        self.date = init_date
        self.time = init_time
        self.cur_time = str(self.date) + str(self.time)

        # Enable logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)

    @property
    def cur_time(self):
        return self._cur_time

    @cur_time.setter
    def cur_time(self, cur_time):
        today = date.today()
        now = f'{today.year}-{today.month}-{today.day}, ' + datetime.now().strftime("%H:%M:%S")
        self._cur_time = now
    
if __name__ == '__main__':
    
    autoBot = TelegramBot(chat_id= chat_id,
                          token = teleBot_token,
                          init_date = date.today(),
                          init_time= datetime.now())
    
    # # commands
    # autoBot.bot.add_handler(CommandHandler("start", autoBot.start))
    # autoBot.bot.add_handler(CommandHandler("help", autoBot.help))
    # autoBot.bot.add_handler(CommandHandler("manual", autoBot.manual))

    # # error handler
    # autoBot.bot.add_error_handler(autoBot.error_handler)

    # # message handler
    # autoBot.bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, autoBot.talk_with_GPT))

    # # Run the bot until the user presses Ctrl-C
    # autoBot.bot.run_polling()