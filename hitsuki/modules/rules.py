#    Hitsuki (A telegram bot project)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import hitsuki.modules.sql.rules_sql as sql
from hitsuki import dispatcher
from hitsuki.modules.connection import connected
from hitsuki.modules.helper_funcs.chat_status import user_admin
from hitsuki.modules.helper_funcs.string_handling import markdown_parser
from hitsuki.modules.tr_engine.strings import tld
from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, Update)
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async
from telegram.utils.helpers import escape_markdown


@run_async
def get_rules(bot: Bot, update: Update):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    from_pm = False

    if conn := connected(bot, update, chat, user.id):
        chat_id = conn
        from_pm = True
    else:
        if chat.type == 'private':
            msg.reply_text(tld(chat.id, 'common_cmd_group_only'))
            return
        chat_id = chat.id

    send_rules(update, chat_id, from_pm)


# Do not async - not from a handler
def send_rules(update, chat_id, from_pm=False):
    bot = dispatcher.bot
    chat = update.effective_chat
    user = update.effective_user
    try:
        chat = bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message != "Chat not found" or not from_pm:
            raise

        bot.send_message(user.id,
                         tld(chat.id, "rules_shortcut_not_setup_properly"))
        return
    rules = sql.get_rules(chat_id)
    text = tld(chat.id, "rules_display").format(escape_markdown(chat.title),
                                                rules)

    if from_pm and rules:
        bot.send_message(user.id, text, parse_mode=ParseMode.MARKDOWN)
    elif from_pm:
        bot.send_message(user.id, tld(chat.id, "rules_not_found"))
    elif rules:
        rules_text = tld(chat.id, "rules")
        update.effective_message.reply_text(
            tld(chat.id, "rules_button_click"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text=rules_text,
                                     url="t.me/{}?start={}".format(
                                         bot.username, chat_id))
            ]]))
    else:
        update.effective_message.reply_text(tld(chat.id, "rules_not_found"))


@run_async
@user_admin
def set_rules(bot: Bot, update: Update):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if conn := connected(bot, update, chat, user.id):
        chat_id = conn
    else:
        if chat.type == 'private':
            msg.reply_text(tld(chat.id, 'common_cmd_group_only'))
            return
        chat_id = chat.id

    raw_text = msg.text
    args = raw_text.split(None,
                          1)  # use python's maxsplit to separate cmd and args
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(
            raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(txt,
                                         entities=msg.parse_entities(),
                                         offset=offset)

        sql.set_rules(chat_id, markdown_rules)
        msg.reply_text(tld(chat.id, "rules_success"))

    elif msg.reply_to_message and len(args) == 1:
        txt = msg.reply_to_message.text
        # set correct offset relative to command
        offset = len(txt) - len(raw_text)
        markdown_rules = markdown_parser(
            txt, entities=msg.parse_entities(), offset=offset)

        sql.set_rules(chat_id, markdown_rules)
        msg.reply_text(tld(chat.id, "rules_success"))


@run_async
@user_admin
def clear_rules(bot: Bot, update: Update):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if conn := connected(bot, update, chat, user.id):
        chat_id = conn
    else:
        if chat.type == 'private':
            msg.reply_text(tld(chat.id, 'common_cmd_group_only'))
            return
        chat_id = chat.id

    sql.set_rules(chat_id, "")
    update.effective_message.reply_text(tld(chat.id, 'rules_clean_success'))


def __stats__():
    return "• <code>{}</code> chats have rules set.".format(sql.num_chats())


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = True

GET_RULES_HANDLER = CommandHandler("rules", get_rules)
SET_RULES_HANDLER = CommandHandler("setrules", set_rules)
RESET_RULES_HANDLER = CommandHandler("clearrules", clear_rules)

dispatcher.add_handler(GET_RULES_HANDLER)
dispatcher.add_handler(SET_RULES_HANDLER)
dispatcher.add_handler(RESET_RULES_HANDLER)
