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

from telethon import custom


def build_keyboard(buttons):
    if len(buttons) != 0:
        keyb = []
        for btn in buttons:
            if btn.same_line and keyb:
                keyb[-1].append(custom.Button.url(btn.name, url=btn.url))
            else:
                keyb.append([custom.Button.url(btn.name, url=btn.url)])
    else:
        keyb = None

    return keyb


def revert_buttons(buttons):
    return "".join(
        "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        if btn.same_line
        else "\n[{}](buttonurl://{})".format(btn.name, btn.url)
        for btn in buttons
    )
