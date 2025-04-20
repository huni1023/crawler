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
from utils.helper import load_config

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

# set dir
Project_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# load config
config = load_config(os.path.join(Project_PATH, 'utils', 'config.yaml'))
chat_id = config['chat_id']
teleBot_token = config['teleBot_token']

class TelegramBot:
    def __init__(self, chat_id = chat_id, token= teleBot_token, init_date=date.today(), init_time=datetime.now()):
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
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Displays info on how to trigger an error."""
        await update.effective_message.reply_html(
            "Telegram bot for Sung Jeehun\n"
            "v1. 23.05 잡코리아 크롤링 노티용\n"
            "<code>/start</code>: 소개\n"
        )
    async def send_crawler_status(self, inputTxt) -> None:
        r"""
        inputTxt: str
            text you want to send
        """
        await self.bot.send_message(chat_id=self.chat_id, text=inputTxt)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        self.logger.error("Exception while handling an update:", exc_info=context.error)
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

            # Finally, send the message
        await context.bot.send_message(
            chat_id=self.chat_id, text=message, parse_mode=ParseMode.HTML
        )
    
    def main(self) -> None:
        # commands
        self.bot.add_handler(CommandHandler("start", self.start))
        
        # error handler
        self.bot.add_error_handler(self.error_handler)

        # # message handler
        # self.bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.talk_with_GPT))

        # Run the bot until the user presses Ctrl-C
        self.bot.run_polling()


if __name__ == '__main__':
    
    autoBot = TelegramBot(chat_id= chat_id,
                          token = teleBot_token,
                          init_date = date.today(),
                          init_time= datetime.now())
    
    # commands
    autoBot.bot.add_handler(CommandHandler("start", autoBot.start))
    
    # error handler
    autoBot.bot.add_error_handler(autoBot.error_handler)

    # # message handler
    # autoBot.bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, autoBot.talk_with_GPT))

    # Run the bot until the user presses Ctrl-C
    autoBot.bot.run_polling()