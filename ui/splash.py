# Copyright 2025 Bailey Lane-Beber
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
import random
import os
import json
from display import safe_addstr

RECENT_FILES_PATH = os.path.expanduser("~/.void_recent_files.json")

LOGO = [
    "██╗   ██╗ ██████╗ ██╗██████╗ ",
    "██║   ██║██╔═══██╗██║██╔══██╗",
    "██║   ██║██║   ██║██║██║  ██║",
    "╚██╗ ██╔╝██║   ██║██║██║  ██║",
    " ╚████╔╝ ╚██████╔╝██║██████╔╝",
    "  ╚═══╝   ╚═════╝ ╚═╝╚═════╝ ",
]

HINTS = [
    "i  Insert Mode       /  Search",
    "o  Open Line Below   n  Next Match",
    ":w Save             :q  Quit",
    "Ctrl+T  Terminal    Ctrl+F  File Finder",
]

RAIN_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(){}[]<>~"

# Color pair IDs — 50+ range to avoid conflicts with display.py and aesthetics.py
SPLASH_RAIN = 50
SPLASH_RAIN_BRIGHT = 51
SPLASH_WHITE = 52
SPLASH_GRAY = 53
SPLASH_CYAN = 54


class SplashScreen:
    def __init__(self):
        self.recent_files = self._load_recent_files()

    def _load_recent_files(self):
        try:
            with open(RECENT_FILES_PATH) as f:
                files = json.load(f)
            return [f for f in files if os.path.exists(f)][:8]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def add_recent_file(filepath):
        filepath = os.path.abspath(filepath)
        try:
            with open(RECENT_FILES_PATH) as f:
                files = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            files = []

        if filepath in files:
            files.remove(filepath)
        files.insert(0, filepath)
        files = files[:20]

        with open(RECENT_FILES_PATH, "w") as f:
            json.dump(files, f)

    def _animate_logo(self, stdscr, max_rows, max_cols):
        logo_height = len(LOGO)
        logo_width = max(len(line) for line in LOGO)

        start_row = max(0, (max_rows // 3) - (logo_height // 2))
        start_col = max(0, (max_cols // 2) - (logo_width // 2))

        logo_cells = {}
        for r, line in enumerate(LOGO):
            for c, ch in enumerate(line):
                if ch != " ":
                    logo_cells[(start_row + r, start_col + c)] = ch

        rain_cols = set()
        for (r, c) in logo_cells:
            rain_cols.add(c)

        drops = {}
        for c in rain_cols:
            drops[c] = {
                "row": random.randint(-15, -1),
                "speed": random.uniform(0.3, 1.0),
                "trail": random.randint(4, 10),
                "accumulator": 0.0,
            }

        revealed = set()
        all_done = False
        frame_interval = 0.03

        try:
            curses.init_pair(SPLASH_RAIN, curses.COLOR_GREEN, -1)
            curses.init_pair(SPLASH_RAIN_BRIGHT, 10, -1)
        except curses.error:
            pass

        rain_color = curses.color_pair(SPLASH_RAIN) | curses.A_DIM
        rain_bright = curses.color_pair(SPLASH_RAIN_BRIGHT)
        logo_color = curses.color_pair(SPLASH_RAIN_BRIGHT) | curses.A_BOLD

        stdscr.timeout(0)
        last_frame = time.monotonic()

        while not all_done:
            # Check for skip keypress
            try:
                ch = stdscr.getch()
                if ch != -1:
                    revealed = set(logo_cells.keys())
                    break
            except curses.error:
                pass

            # Frame timing using monotonic clock instead of sleep
            now = time.monotonic()
            if now - last_frame < frame_interval:
                continue
            last_frame = now

            for c in list(drops.keys()):
                drop = drops[c]
                drop["accumulator"] += drop["speed"]

                if drop["accumulator"] >= 1.0:
                    drop["accumulator"] -= 1.0
                    drop["row"] += 1
                    row = drop["row"]

                    if 0 <= row < max_rows and 0 <= c < max_cols:
                        char = random.choice(RAIN_CHARS)
                        safe_addstr(stdscr, row, c, char, rain_bright)

                    trail_row = row - 1
                    if 0 <= trail_row < max_rows and 0 <= c < max_cols:
                        if (trail_row, c) in logo_cells:
                            revealed.add((trail_row, c))
                            safe_addstr(stdscr, trail_row, c, logo_cells[(trail_row, c)], logo_color)
                        else:
                            char = random.choice(RAIN_CHARS)
                            safe_addstr(stdscr, trail_row, c, char, rain_color)

                    erase_row = row - drop["trail"]
                    if 0 <= erase_row < max_rows and 0 <= c < max_cols:
                        if (erase_row, c) not in revealed:
                            safe_addstr(stdscr, erase_row, c, " ")

                    col_logo_rows = [r for (r, cc) in logo_cells if cc == c]
                    if col_logo_rows and row - drop["trail"] > max(col_logo_rows):
                        del drops[c]

            for (r, c) in revealed:
                safe_addstr(stdscr, r, c, logo_cells[(r, c)], logo_color)

            stdscr.refresh()

            if not drops:
                all_done = True

        stdscr.timeout(-1)

        stdscr.erase()
        for (r, c), ch in logo_cells.items():
            safe_addstr(stdscr, r, c, ch, logo_color)

        return start_row, start_col, logo_height, logo_width

    def _draw_content(self, stdscr, max_rows, max_cols, logo_row, logo_height):
        content_row = logo_row + logo_height + 2

        try:
            curses.init_pair(SPLASH_WHITE, curses.COLOR_WHITE, -1)
            curses.init_pair(SPLASH_GRAY, 8, -1)
            curses.init_pair(SPLASH_CYAN, curses.COLOR_CYAN, -1)
        except curses.error:
            pass

        white = curses.color_pair(SPLASH_WHITE)
        gray = curses.color_pair(SPLASH_GRAY)
        cyan = curses.color_pair(SPLASH_CYAN)

        tagline = "A terminal text editor"
        tag_col = max(0, (max_cols // 2) - (len(tagline) // 2))
        safe_addstr(stdscr, content_row, tag_col, tagline, gray)

        content_row += 2

        hint_header = "Keybinds"
        hint_col = max(0, (max_cols // 2) - (len(hint_header) // 2))
        safe_addstr(stdscr, content_row, hint_col, hint_header, white | curses.A_BOLD)
        content_row += 1

        for hint in HINTS:
            col = max(0, (max_cols // 2) - (len(hint) // 2))
            safe_addstr(stdscr, content_row, col, hint, gray)
            content_row += 1

        content_row += 1

        if self.recent_files:
            rf_header = "Recent Files"
            rf_col = max(0, (max_cols // 2) - (len(rf_header) // 2))
            safe_addstr(stdscr, content_row, rf_col, rf_header, white | curses.A_BOLD)
            content_row += 1

            self.rf_start_row = content_row
            for i, filepath in enumerate(self.recent_files):
                display = os.path.basename(filepath)
                path_hint = os.path.dirname(filepath)
                line = f"  [{i + 1}] {display}  {path_hint}"
                col = max(0, (max_cols // 2) - (len(line) // 2))
                safe_addstr(stdscr, content_row, col, line, cyan)
                content_row += 1
        else:
            self.rf_start_row = content_row

        content_row += 1

        footer = "Press Ctrl+F to browse files  |  Enter -New File- |  q -Quit-"
        footer_col = max(0, (max_cols // 2) - (len(footer) // 2))
        safe_addstr(stdscr, content_row, footer_col, footer, gray)
    
    
    def show(self, stdscr):
        curses.curs_set(0)
        stdscr.erase()

        max_rows = curses.LINES
        max_cols = curses.COLS

        logo_row, logo_col, logo_height, logo_width = self._animate_logo(stdscr, max_rows, max_cols)
        self._draw_content(stdscr, max_rows, max_cols, logo_row, logo_height)
        stdscr.refresh()

        while True:
            k = stdscr.getkey()
            
            # Dynamic resize for splash screen           
            if k == "KEY_RESIZE": 
                curses.update_lines_cols()
                max_rows, max_cols = stdscr.getmaxyx()
                stdscr.erase()
                
                # redraw the static logo (no animation on resize)
                logo_row, logo_height = self._draw_static_logo(stdscr, max_rows, max_cols)
                self._draw_content(stdscr, max_rows, max_cols, logo_row, logo_height)
                stdscr.refresh()
                continue 
            
            elif k.isdigit() and k != "0":
                idx = int(k) - 1
                if idx < len(self.recent_files):
                    return self.recent_files[idx]
                        
            elif k == "q":
                return "__quit__"
            elif k in ("\n", " "):
                return None
            elif k == "\x1b":
                return None
            elif k == "\x06":
                return "__file_finder__"
            elif k == ":":
                return "__command__"
   
    
     # Helper func for my splashscreen resizing
    def _draw_static_logo(self, stdscr, max_rows, max_cols):
        logo_height = len(LOGO)
        logo_width = max(len(line) for line in LOGO)
        start_row = max(0, (max_rows // 3 ) - (logo_height // 2))
        start_col = max(0, (max_cols // 2) - (logo_width //2))
        
        logo_color = curses.color_pair(SPLASH_RAIN_BRIGHT) | curses.A_BOLD
        for r, line in enumerate(LOGO):
            safe_addstr(stdscr, start_row + r, start_col, line, logo_color)
        return start_row, logo_height 