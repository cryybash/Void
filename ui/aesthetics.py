# Copyright 2026 Bailey Lane-Beber
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import curses
import time
import os
from config.keys import NEW_FILE_NAME
from ui.display import safe_addstr

#  COLOR PAIR IDS FOR HUD
#  Starting at 30 to avoid conflicts

HUD_NORMAL = 30
HUD_INSERT = 31
HUD_VISUAL = 32
HUD_VISUAL_LINE = 33
HUD_VISUAL_BLOCK = 34
HUD_COMMAND = 35
HUD_BORDER = 36
HUD_DIM = 37
BRIGHT_CYAN = 14

MODE_COLORS = {
    "normal":       HUD_NORMAL,
    "insert":       HUD_INSERT,
    "visual":       HUD_VISUAL,
    "visual-line":  HUD_VISUAL_LINE,
    "visual-block": HUD_VISUAL_BLOCK,
    "command":      HUD_COMMAND,
}

MODE_LABELS = {
    "normal":       " NORMAL ",
    "insert":       " INSERT ",
    "visual":       " VISUAL ",
    "visual-line":  " V-LINE ",
    "visual-block": " V-BLOCK ",
    "command":      " COMMAND ",
}


def init_hud_colors():
    curses.init_pair(HUD_NORMAL,       curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(HUD_INSERT,       curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(HUD_VISUAL,       curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(HUD_VISUAL_LINE,  curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(HUD_VISUAL_BLOCK, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(HUD_COMMAND,      curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(HUD_BORDER, BRIGHT_CYAN, -1)
    curses.init_pair(HUD_DIM,    BRIGHT_CYAN, -1)


class FloatingHUD:
    def __init__(self):
        self.start_time = time.time()
    
    def reset_timer(self):
        self.start_time = time.time()
    
    def _format_elapsed(self):
        elapsed = int(time.time() - self.start_time)
        if elapsed < 60:
            return f"{elapsed}s"
        elif elapsed < 3600:
            return f"{elapsed // 60}m"
        else:
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            return f"{h}h{m}m"

    def _get_filetype(self, filename):
        if not filename or filename == NEW_FILE_NAME:
            return "txt"
        ext = os.path.splitext(filename)[1]
        if ext:
            return ext[1:]
        return "txt"
    
    def draw(self, stdscr, mode, filename, n_cols, row_offset=1):
        mode_label = MODE_LABELS.get(mode, f" {mode.upper()} ")
        filetype = self._get_filetype(filename)
        clock = time.strftime("%H:%M")
        elapsed = self._format_elapsed()

        sep = " │ "
        inner = f"{mode_label}{sep}.{filetype}{sep}{clock}{sep}{elapsed} "

        box_width = len(inner) + 2
        box_row = row_offset
        box_col = n_cols - box_width - 1

        if box_col < 0:
            return

        mode_color_id = MODE_COLORS.get(mode, HUD_NORMAL)
        mode_color = curses.color_pair(mode_color_id) | curses.A_BOLD
        border_color = curses.color_pair(HUD_BORDER)
        dim_color = curses.color_pair(HUD_DIM)
        sep_color = curses.color_pair(HUD_BORDER) | curses.A_DIM

        top = "╭" + "─" * (box_width - 2) + "╮"
        safe_addstr(stdscr, box_row, box_col, top, border_color)

        mid_row = box_row + 1
        safe_addstr(stdscr, mid_row, box_col, "│", border_color)

        col = box_col + 1

        safe_addstr(stdscr, mid_row, col, mode_label, mode_color)
        col += len(mode_label)

        safe_addstr(stdscr, mid_row, col, sep, sep_color)
        col += len(sep)

        ft_display = f".{filetype}"
        safe_addstr(stdscr, mid_row, col, ft_display, dim_color | curses.A_BOLD)
        col += len(ft_display)

        safe_addstr(stdscr, mid_row, col, sep, sep_color)
        col += len(sep)

        safe_addstr(stdscr, mid_row, col, clock, dim_color)
        col += len(clock)

        safe_addstr(stdscr, mid_row, col, sep, sep_color)
        col += len(sep)

        elapsed_display = f"{elapsed} "
        safe_addstr(stdscr, mid_row, col, elapsed_display, dim_color)
        col += len(elapsed_display)

        safe_addstr(stdscr, mid_row, box_col + box_width - 1, "│", border_color)

        bot = "╰" + "─" * (box_width - 2) + "╯"
        safe_addstr(stdscr, box_row + 2, box_col, bot, border_color)


# Global HUD instance
hud = FloatingHUD()
