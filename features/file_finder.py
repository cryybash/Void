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

import os
import curses
from keys import FILE_FINDER_WIDTH, KEY_ESCAPE
from display import safe_addstr


class FileFinder:
    def __init__(self):
        self.visible = False
        self.files = []
        self.selected = 0
        self.scroll_offset = 0
        self.width = FILE_FINDER_WIDTH
        self.cwd = os.getcwd()
        self.show_hidden = False
        self.refresh_files()
    
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.refresh_files()
    
    def refresh_files(self):
        try:
            entries = os.listdir(self.cwd)
        except PermissionError:
            entries = []

        if not self.show_hidden:
            entries = [e for e in entries if not e.startswith(".")]

        dirs = sorted([e for e in entries if os.path.isdir(os.path.join(self.cwd, e))])
        files = sorted([e for e in entries if os.path.isfile(os.path.join(self.cwd, e))])

        self.files = ["../"] + [d + "/" for d in dirs] + files
        self.selected = 0
        self.scroll_offset = 0
    
    def get_editor_cols(self, total_cols):
        if self.visible:
            return total_cols - self.width
        return total_cols

    def move_up(self):
        if self.selected > 0:
            self.selected -= 1
            if self.selected < self.scroll_offset:
                self.scroll_offset = self.selected

    def move_down(self):
        if self.selected < len(self.files) - 1:
            self.selected += 1
    
    def select(self):
        if not self.files:
            return None

        entry = self.files[self.selected]

        if entry == "../":
            self.cwd = os.path.dirname(self.cwd)
            self.refresh_files()
            return None
        elif entry.endswith("/"):
            dirname = entry.rstrip("/")
            self.cwd = os.path.join(self.cwd, dirname)
            self.refresh_files()
            return None
        else:
            return os.path.join(self.cwd, entry)
    
    def handle_key(self, k):
        if k == KEY_ESCAPE:
            return "blur"
        elif k in ("j", "KEY_DOWN"):
            self.move_down()
        elif k in ("k", "KEY_UP"):
            self.move_up()
        elif k == "\n":
            result = self.select()
            if result:
                return result
        elif k == ".":
            # Toggle hidden files (changed from 'h' to avoid vim conflict)
            self.show_hidden = not self.show_hidden
            self.refresh_files()
        elif k == "r":
            self.refresh_files()
        return None
    
    def draw(self, stdscr, start_col, n_rows, row_offset=0):
        if not self.visible:
            return

        for row in range(row_offset, n_rows + row_offset):
            safe_addstr(stdscr, row, start_col, "│", curses.A_DIM)

        header = " Files "
        short_cwd = os.path.basename(self.cwd) or self.cwd
        cwd_display = f" {short_cwd}/"
        safe_addstr(stdscr, row_offset, start_col + 1, header[:self.width - 1], curses.A_BOLD)
        safe_addstr(stdscr, row_offset + 1, start_col + 1, cwd_display[:self.width - 1], curses.A_DIM)

        list_start = row_offset + 2
        visible_rows = n_rows - 2

        if self.selected >= self.scroll_offset + visible_rows:
            self.scroll_offset = self.selected - visible_rows + 1
        if self.selected < self.scroll_offset:
            self.scroll_offset = self.selected

        visible_files = self.files[self.scroll_offset:self.scroll_offset + visible_rows]

        for i, entry in enumerate(visible_files):
            row = list_start + i
            if row >= n_rows + row_offset:
                break

            index = self.scroll_offset + i
            display = entry[:self.width - 2]

            if index == self.selected:
                attr = curses.A_REVERSE
            elif entry.endswith("/"):
                attr = curses.A_BOLD
            else:
                attr = curses.A_NORMAL

            safe_addstr(stdscr, row, start_col + 1, " " * (self.width - 1), curses.A_NORMAL)
            safe_addstr(stdscr, row, start_col + 2, display, attr)