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

import asyncio
import html
import os
import re
import sys

import aiohttp
import regex
from aiohttp import ClientSession
from hitsuki import SUDO_USERS, TOKEN, pbot
from pyrogram import Client, filters
from pyrogram.types import Message

# Some commands in this module are EduuRobot ports (authorized)
# EduuRobot commands:
# /dice, /ping, /pyroid, sed/regex, /upgrade, /cmd, /restart
#
# The /ip command is a pyrogram adaptation of MicroBot
#
# EduuRobot: github.com/AmanoTeam/EduuRobot
# MicroBot: github.com/Nick80835/microbot
#
# Please do not remove these comments!


@pbot.on_message(filters.command('dice'))
async def dice(c: Client, m: Message):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.message_id)
    await dicen.reply_text(
        f"The dice stopped at the number {dicen.dice.value}", quote=True)


@pbot.on_message(filters.command("pyroid") & filters.private)
async def ids_private(c: Client, m: Message):
    await m.reply_text("<b>Info:</b>\n\n"
                       "<b>Name:</b> <code>{first_name} {last_name}</code>\n"
                       "<b>Username:</b> @{username}\n"
                       "<b>User ID:</b> <code>{user_id}</code>\n"
                       "<b>Language:</b> {lang}\n"
                       "<b>Chat type:</b> {chat_type}".format(
                           first_name=m.from_user.first_name,
                           last_name=m.from_user.last_name or "",
                           username=m.from_user.username,
                           user_id=m.from_user.id,
                           lang=m.from_user.language_code,
                           chat_type=m.chat.type
                       ),
                       parse_mode="HTML")


@pbot.on_message(filters.command("pyroid") & filters.group)
async def ids(c: Client, m: Message):
    d = m.reply_to_message or m
    await m.reply_text("<b>Info:</b>\n\n"
                       "<b>Name:</b> <code>{first_name} {last_name}</code>\n"
                       "<b>Username:</b> @{username}\n"
                       "<b>User ID:</b> <code>{user_id}</code>\n"
                       "<b>Datacenter:</b> {user_dc}\n"
                       "<b>Language:</b> {lang}\n\n"
                       "<b>Chat name:</b> <code>{chat_title}</code>\n"
                       "<b>Chat username:</b> @{chat_username}\n"
                       "<b>Chat ID:</b> <code>{chat_id}</code>\n"
                       "<b>Chat type:</b> {chat_type}".format(
                           first_name=html.escape(d.from_user.first_name),
                           last_name=html.escape(d.from_user.last_name or ""),
                           username=d.from_user.username,
                           user_id=d.from_user.id,
                           user_dc=d.from_user.dc_id,
                           lang=d.from_user.language_code or "-",
                           chat_title=m.chat.title,
                           chat_username=m.chat.username,
                           chat_id=m.chat.id,
                           chat_type=m.chat.type
                       ),
                       parse_mode="HTML")


@pbot.on_message(filters.regex(r'^s/(.+)?/(.+)?(/.+)?') & filters.reply)
async def sed(c: Client, m: Message):
    exp = regex.split(r'(?<![^\\]\\)/', m.text)
    pattern = exp[1]
    replace_with = exp[2].replace(r'\/', '/')
    rflags = 0

    flags = exp[3] if len(exp) > 3 else ''
    count = 0 if 'g' in flags else 1
    if 'i' in flags and 's' in flags:
        rflags = regex.I | regex.S
    elif 'i' in flags:
        rflags = regex.I
    elif 's' in flags:
        rflags = regex.S

    text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return

    try:
        res = regex.sub(
            pattern,
            replace_with,
            text,
            count=count,
            flags=rflags,
            timeout=1)
    except TimeoutError:
        await m.reply_text("Oops, your regex pattern ran for too long.")
    except regex.error as e:
        await m.reply_text(str(e))
    else:
        await c.send_message(m.chat.id, f'<pre>{html.escape(res)}</pre>',
                             reply_to_message_id=m.reply_to_message.message_id)


@pbot.on_message(filters.command("banall") &
                 filters.group & filters.user(SUDO_USERS))
async def ban_all(c: Client, m: Message):
    chat = m.chat.id

    async for member in c.iter_chat_members(chat):
        user_id = member.user.id
        url = (
            f"https://api.telegram.org/bot{TOKEN}/kickChatMember?chat_id={chat}&user_id={user_id}")
        async with aiohttp.ClientSession() as session:
            await session.get(url)


@pbot.on_message(filters.command("upgrade") & filters.user(SUDO_USERS))
async def upgrade(c: Client, m: Message):
    sm = await m.reply_text("Upgrading sources...")
    proc = await asyncio.create_subprocess_shell("git pull --no-edit",
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.STDOUT)
    stdout = (await proc.communicate())[0]
    if proc.returncode == 0:
        if "Already up to date." in stdout.decode():
            await sm.edit_text("There's nothing to upgrade.")
        else:
            await sm.edit_text("Restarting...")
            args = [sys.executable, "-m", "hitsuki"]
            os.execl(sys.executable, *args)
    else:
        await sm.edit_text(f"Upgrade failed (process exited with {proc.returncode}):\n{stdout.decode()}")
        proc = await asyncio.create_subprocess_shell("git merge --abort")
        await proc.communicate()


@pbot.on_message(filters.command("cmd") & filters.user(SUDO_USERS))
async def run_cmd(c: Client, m: Message):
    cmd = m.text.split(maxsplit=1)[1]
    if re.match('(?i)poweroff|halt|shutdown|reboot', cmd):
        res = ('Forbidden command.')
    else:
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        res = ("<b>Output:</b>\n<code>{}</code>".format(html.escape(stdout.decode().strip())) if stdout else '') + \
              ("\n<b>Errors:</b>\n<code>{}</code>".format(
                  html.escape(stderr.decode().strip())) if stderr else '')
    await m.reply_text(res)


@pbot.on_message(filters.command("restart") & filters.user(SUDO_USERS))
async def restart(c: Client, m: Message):
    await m.reply_text("Restarting...")
    args = [sys.executable, "-m", "hitsuki"]
    os.execl(sys.executable, *args)


@pbot.on_message(filters.command("ip"))
async def ip(c: Client, m: Message):
    ip = m.text.split(maxsplit=1)[1]

    aioclient = ClientSession()
    if not ip:
        await m.reply_text("Provide an IP!")
        return

    async with aioclient.get(f"http://ip-api.com/json/{ip}") as response:
        if response.status == 200:
            lookup_json = await response.json()
        else:
            await m.reply_text(f"An error occurred when looking for **{ip}**: **{response.status}**", parse_mode="markdown")
            return

    fixed_lookup = {}

    special = {"lat": "Latitude", "lon": "Longitude",
               "isp": "ISP", "as": "AS", "asname": "AS name"}
    for key, value in lookup_json.items():
        if key in special:
            fixed_lookup[special[key]] = str(value)
            continue

        key = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", key)
        key = key.capitalize()

        if not value:
            value = "None"

        fixed_lookup[key] = str(value)

    text = ""

    for key, value in fixed_lookup.items():
        text = f"{text}**{key}:** `{value}`\n"

    await m.reply_text(text, parse_mode="markdown")
