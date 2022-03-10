#    Hitsuki (A telegram bot project)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import List

import hitsuki.modules.sql.antispam_sql as sql
from hitsuki import STRICT_ANTISPAM, dispatcher, sw
from hitsuki.modules.helper_funcs.chat_status import is_user_admin, user_admin
from hitsuki.modules.tr_engine.strings import tld
from telegram import Bot, ParseMode, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, run_async

GBAN_ENFORCE_GROUP = 6


def check_and_ban(update, user_id, should_message=True):
    chat = update.effective_chat
    message = update.effective_message
    try:
        if sw is not None:
            if sw_ban := sw.get_ban(user_id):
                spamwatch_reason = sw_ban.reason
                chat.kick_member(user_id)
                if should_message:
                    message.reply_text(tld(
                        chat.id,
                        "antispam_spamwatch_banned").format(spamwatch_reason),
                        parse_mode=ParseMode.HTML)
                return
    except Exception:
        pass


@run_async
def enforce_gban(bot: Bot, update: Update):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    try:
        if sql.does_chat_gban(
                update.effective_chat.id) and update.effective_chat.get_member(
                    bot.id).can_restrict_members:
            user = update.effective_user
            chat = update.effective_chat
            msg = update.effective_message

            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id)
                return

            if msg.new_chat_members:
                new_members = update.effective_message.new_chat_members
                for mem in new_members:
                    check_and_ban(update, mem.id)
                    return

            if msg.reply_to_message:
                user = msg.reply_to_message.from_user
                if user and not is_user_admin(chat, user.id):
                    check_and_ban(update, user.id, should_message=False)
                    return
    except Exception as f:
        print(f"err {f}")


@run_async
@user_admin
def antispam(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat
    if args:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_antispam(chat.id)
            update.effective_message.reply_text(tld(chat.id, "antispam_on"))
        elif args[0].lower() in ["off", "no"]:
            sql.disable_antispam(chat.id)
            update.effective_message.reply_text(tld(chat.id, "antispam_off"))
    else:
        update.effective_message.reply_text(
            tld(chat.id,
                "antispam_err_wrong_arg").format(sql.does_chat_gban(chat.id)))


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = True

ANTISPAM_STATUS = CommandHandler("antispam",
                                 antispam,
                                 pass_args=True,
                                 filters=Filters.group)

GBAN_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gban)

dispatcher.add_handler(ANTISPAM_STATUS)

if STRICT_ANTISPAM:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
