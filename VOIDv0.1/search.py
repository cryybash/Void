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
from keys import KEY_ESCAPE, KEY_BACKSPACE_CODES, KEY_ENTER

class SearchState:
    def __init__(self):
        self.query = ""
        self.matches = []
        self.match_index = -1
        self.active = False
        self.confirming = False
        self.replacement = ""

    def reset(self):
        self.query = ""
        self.matches = []
        self.match_index = -1
        self.active = False
        self.confirming = False
        self.replacement = ""

    def find_all(self, buffer, query):
        self.query = query
        self.matches = []
        self.match_index = -1

        if not query:
            self.active = False
            return

        for row_idx in range(len(buffer)):
            line = buffer[row_idx]
            col = 0
            while col <= len(line) - len(query):
                pos = line.find(query, col)
                if pos == -1:
                    break
                self.matches.append((row_idx, pos))
                col = pos + 1

        self.active = True

    def next_match(self, cursor, window, buffer):
        if not self.matches:
            return False
        for i, (row, col) in enumerate(self.matches):
            if (row, col) > (cursor.row, cursor.col):
                self.match_index = i
                self._jump_to_match(cursor, window, buffer)
                return True
        self.match_index = 0
        self._jump_to_match(cursor, window, buffer)
        return True

    def prev_match(self, cursor, window, buffer):
        if not self.matches:
            return False
        for i in range(len(self.matches) - 1, -1, -1):
            row, col = self.matches[i]
            if (row, col) < (cursor.row, cursor.col):
                self.match_index = i
                self._jump_to_match(cursor, window, buffer)
                return True
        self.match_index = len(self.matches) - 1
        self._jump_to_match(cursor, window, buffer)
        return True

    def _jump_to_match(self, cursor, window, buffer):
        if self.match_index < 0 or self.match_index >= len(self.matches):
            return
        row, col = self.matches[self.match_index]
        cursor.row = row
        cursor.col = col
        cursor._col_hint = col
        if cursor.row < window.row:
            window.row = cursor.row
        elif cursor.row > window.row + window.n_rows - 1:
            window.row = cursor.row - window.n_rows + 1
        window.horizontal_scroll(cursor)

    def match_info(self):
        if not self.matches:
            return "[no matches]"
        return f"[{self.match_index + 1}/{len(self.matches)}]"
    
    def replace_all(self, buffer, replacement):
        if not self.matches or not self.query:
            return 0
        count = 0
        for row, col in reversed(self.matches):
            line = buffer.lines[row]
            buffer.lines[row] = line[:col] + replacement + line[col + len(self.query):]
            count += 1
        self.reset()
        return count


# Global search state shared across modules
search_state = SearchState()


# Prompt the user for a search query on the status line
def search_prompt(stdscr, window, restore_timeout=100):
    stdscr.timeout(-1)
    curses.curs_set(1)
    stdscr.addstr(window.n_rows, 0, "/" + " " * (window.n_cols - 1))
    stdscr.move(window.n_rows, 1)
    query = ""

    while True:
        ch = stdscr.getkey()
        if ch == KEY_ENTER:
            break
        elif ch in KEY_BACKSPACE_CODES:
            if query:
                query = query[:-1]
            else:
                stdscr.timeout(restore_timeout)
                return ""
        elif ch == KEY_ESCAPE:
            stdscr.timeout(restore_timeout)
            return ""
        elif len(ch) == 1 and ch.isprintable():
            query += ch

        display = "/" + query
        stdscr.addstr(window.n_rows, 0, display + " " * (window.n_cols - len(display)))
        stdscr.move(window.n_rows, len(display))
    stdscr.timeout(restore_timeout)
    return query