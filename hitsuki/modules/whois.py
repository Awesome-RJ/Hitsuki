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

from datetime import datetime

from hitsuki import pbot
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.types import Message, User


def ReplyCheck(m: Message):
    reply_id = None

    if m.reply_to_message:
        reply_id = m.reply_to_message.message_id

    elif not m.from_user.is_self:
        reply_id = m.message_id

    return reply_id


infotext = (
    "**[{full_name}](tg://user?id={user_id})**\n"
    " • UserID: `{user_id}`\n"
    " • First Name: `{first_name}`\n"
    " • Last Name: `{last_name}`\n"
    " • Username: `{username}`\n"
    " • Last Online: `{last_online}`\n"
    " • Bio: __{bio}__")


def LastOnline(user: User):
    if user.is_bot:
        return ""
    elif user.status == 'recently':
        return "Recently"
    elif user.status == 'within_week':
        return "Within the last week"
    elif user.status == 'within_month':
        return "Within the last month"
    elif user.status == 'long_time_ago':
        return "A long time ago :("
    elif user.status == 'online':
        return "Currently Online"
    elif user.status == 'offline':
        return datetime.fromtimestamp((user.status.date).strftime(
            "%a, %d %b %Y, %H:%M:%S"))


def FullName(user: User):
    return (
        f'{user.first_name} {user.last_name}'
        if user.last_name
        else user.first_name
    )


@pbot.on_message(filters.command('whois'))
async def whois(c: Client, m: Message):
    cmd = m.command
    if not m.reply_to_message and len(cmd) == 1:
        get_user = m.from_user.id
    elif len(cmd) == 1:
        get_user = m.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await c.get_users(get_user)
    except PeerIdInvalid:
        await m.reply("I don't know that User.")
        return
    desc = await c.get_chat(get_user)
    desc = desc.description
    await m.reply_text(
        infotext.format(
            full_name=FullName(user),
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name or "None",
            username=user.username or "None",
            last_online=LastOnline(user),
            bio=desc or "`No bio set up.`",
        ),
        disable_web_page_preview=True,
    )
