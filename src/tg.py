from datetime import datetime
from zoneinfo import ZoneInfo
import telegram

def parse_markdown_v2(msg, exclude=None):
    reserved_words = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    if exclude:
        for exclude_word in exclude:
            reserved_words.remove(exclude_word)
    for reserved_word in reserved_words:
        msg = str(msg).replace(reserved_word, "\{}".format(reserved_word))
    return msg

class Tg:
    def __init__(self, token, chat_id, topic_id=None):
        self.tg_bot = telegram.Bot(token = token)
        self.chat_id = chat_id
        self.topic_id = int(topic_id) if topic_id else None

    async def send_message(self, res_msg):
        await self.tg_bot.send_message(chat_id=self.chat_id, message_thread_id=self.topic_id, text=res_msg, parse_mode='markdownv2')

    async def send_notification(self, res_type, res_from, res_msg):
        tg_msg = f"__*🔔{res_type} notification from {res_from}🔔*__\n{res_msg}\n{parse_markdown_v2(datetime.strftime(datetime.now(tz=ZoneInfo('Asia/Seoul')), format='%Y/%m/%d %H:%M:%S'))}"

        await self.tg_bot.send_message(chat_id=self.chat_id, message_thread_id=self.topic_id, text=tg_msg, parse_mode='markdownv2')
    async def send_trade_notification(self, res_from, res_func, res_coin, res_msg):
        tg_msg = f"__*💸Result of {parse_markdown_v2(res_coin)} {parse_markdown_v2(res_func)} on {parse_markdown_v2(res_from)}💸*__\n"
        for (key, item) in res_msg.items():
            tg_msg = tg_msg + f"*{parse_markdown_v2(key.capitalize())}:* {parse_markdown_v2(item)}\n"

        await self.tg_bot.send_message(chat_id=self.chat_id, message_thread_id=self.topic_id, text=tg_msg, parse_mode='markdownv2')
    async def send_error_notification(self, res_from, res_msg):
        tg_msg = f"__*🚫Error occurred from {res_from}\!🚫*__\n{res_msg}"
        await self.tg_bot.send_message(chat_id=self.chat_id, message_thread_id=self.topic_id, text=tg_msg, parse_mode='markdownv2')