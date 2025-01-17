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

from asyncio import sleep

from hitsuki.events import register
from hitsuki.modules.helper_funcs.telethon.chat_status import (
    can_delete_messages, user_is_admin)
from hitsuki.modules.tr_engine.strings import tld


@register(pattern="^/purge")
async def purge(event):
    if event.sender_id is None:
        return

    chat = event.chat_id

    if not await user_is_admin(user_id=event.sender_id, message=event):
        await event.reply(tld(chat, "helpers_user_not_admin"))
        return

    if not await can_delete_messages(message=event):
        await event.reply(tld(chat, "helpers_bot_cant_delete"))
        return

    msg = await event.get_reply_message()
    if not msg:
        await event.reply(tld(chat, "purge_invalid"))
        return
    msg_id = msg.id
    count = 0
    delete_to = event.message.id - 1
    await event.client.delete_messages(chat, event.message.id)

    msgs = [event.reply_to_msg_id]
    for m_id in range(delete_to, msg_id - 1, -1):
        msgs.append(m_id)
        count += 1
        if len(msgs) == 100:
            await event.client.delete_messages(chat, msgs)
            msgs = []

    await event.client.delete_messages(chat, msgs)
    text = tld(chat, "purge_msg_success").format(count)
    done = await event.respond(text, parse_mode='md')

    await sleep(5)
    await done.delete()


@register(pattern="^/del$")
async def delet(event):
    if event.sender_id is None:
        return

    chat = event.chat_id

    if not await user_is_admin(user_id=event.sender_id, message=event):
        await event.reply(tld(chat, "helpers_user_not_admin"))
        return

    if not await can_delete_messages(message=event):
        await event.reply(tld(chat, "helpers_bot_cant_delete"))
        return

    msg = await event.get_reply_message()
    if not msg:
        await event.reply(tld(chat, "purge_invalid"))
        return
    currentmsg = event.message
    chat = await event.get_input_chat()
    delall = [msg, currentmsg]
    await event.client.delete_messages(chat, delall)


__help__ = True
