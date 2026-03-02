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
import argparse
from buffer import Buffer
from keybinds import handle_keypress, EditorState, open_file_in_tab
from display import (init_colors, detect_language, line_num_width, draw_line_number,
                     draw_line, draw_indent_guides, draw_tab_bar, draw_status_bar,
                     draw_search_highlights, draw_matching_pair, draw_visual_selection)
from terminal import InlineTerminal
from tab import Tab, TabManager
from file_finder import FileFinder
from search import search_state 
from splash import SplashScreen
from visual import visual_state
from aesthetics import hud, init_hud_colors
from keys import NEW_FILE_NAME


# Viewing the buffer through a window 
class Window:
    def __init__(self, n_rows, n_cols, row=0, col=0):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.row = row
        self.col = col
   
    @property
    def bottom(self):
        return self.row + self.n_rows - 1
    
    def up(self, cursor):
        if cursor.row == self.row - 1 and self.row > 0:
            self.row -= 1

    def down(self, buffer, cursor):
        if cursor.row == self.bottom + 1 and self.bottom < buffer.bottom:
            self.row += 1
    
    def horizontal_scroll(self, cursor, margin=5, gutter=0):
        usable = self.n_cols - gutter
        if cursor.col - self.col >= usable - margin:
            self.col = cursor.col - usable + margin + 1
        elif cursor.col - self.col < margin and self.col > 0:
            self.col = max(cursor.col - margin, 0)     
        
    def half_page_down(self, buffer, cursor):
        amount = self.n_rows // 2
        self.row = min(self.row + amount, buffer.bottom)
        cursor.row = min(cursor.row + amount, buffer.bottom)
        cursor._clamp_col(buffer)
  
    def half_page_up(self, buffer, cursor):
        amount = self.n_rows // 2
        self.row = max(self.row - amount, 0)
        cursor.row = max(cursor.row - amount, 0)
        cursor._clamp_col(buffer)

    def translate(self, cursor):
        return cursor.row - self.row, cursor.col - self.col


# MOVING CURSOR THROUGH THE BUFFER  
class Cursor:
    def __init__(self, row=0, col=0, col_hint=None):
        self.row = row
        self._col = col
        self._col_hint = col if col_hint is None else col_hint
    
    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, col):
        self._col = col
        self._col_hint = col 
    
    def up(self, buffer):
        if self.row > 0:
            self.row -= 1
            self._clamp_col(buffer)
    
    def down(self, buffer):
        if self.row < buffer.bottom:
            self.row += 1
            self._clamp_col(buffer)

    def left(self, buffer):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(buffer[self.row])
     
    def right(self, buffer):
        if self.col < len(buffer[self.row]):
            self.col += 1
        elif self.row < buffer.bottom:
            self.row += 1
            self.col = 0
    
    def _clamp_col(self, buffer):
        self._col = min(self._col_hint, len(buffer[self.row]))


# ──────────────────────────────────
#  DRAWING HELPERS
# ──────────────────────────────────


# Draw all editor UI components for one frame
def draw_editor(stdscr, buffer, window, cursor, tab_manager, terminal, file_finder, state, search_state, visual_state, hud):
    tab = tab_manager.active_tab
    filename = tab.filename
    lang = detect_language(filename)
    
    draw_tab_bar(stdscr, tab_manager, window.n_cols + 1)
    editor_rows = terminal.get_editor_rows(window.n_rows)
    ln_width = line_num_width(buffer)
     
    for row, line in enumerate(buffer[window.row:window.row + editor_rows]):
        screen_row = row + 1
        line_number = window.row + row + 1
        display_line = line[window.col:] if window.col < len(line) else ""
        is_cursor_line = (window.row + row == cursor.row)
        draw_line_number(stdscr, screen_row, line_number, ln_width)
        bg = curses.A_BOLD if is_cursor_line else None           
        draw_line(stdscr, screen_row, ln_width, display_line, lang, window.n_cols, bg)

    draw_indent_guides(stdscr, buffer, window, editor_rows, ln_width, window.n_cols,
                       cursor_row=cursor.row, cursor_col=cursor.col, row_offset=1)
    draw_search_highlights(stdscr, buffer, window, editor_rows, ln_width, window.n_cols,
                           search_state, row_offset=1)
    draw_matching_pair(stdscr, buffer, window, cursor, ln_width, window.n_cols,
                       editor_rows, row_offset=1)
    draw_visual_selection(stdscr, buffer, window, editor_rows, ln_width, window.n_cols,
                          visual_state, cursor, row_offset=1)
    
    # Status bar
    status_row = editor_rows + 1
    if search_state.confirming:
        search_info = f"Replace with '{search_state.replacement}'? (y/n/a/q) {search_state.match_info()}"
    elif search_state.active:
        search_info = search_state.match_info()
    else:
        search_info = ""
    draw_status_bar(stdscr, status_row, window, cursor, filename, state.modified, state.mode, search_info)
    
    # Panels
    if terminal.visible:
        terminal.draw(stdscr, status_row + 1, window.n_cols + 1)
    if file_finder.visible:
        editor_cols = file_finder.get_editor_cols(window.n_cols)
        file_finder.draw(stdscr, editor_cols + 1, editor_rows, row_offset=1)
    
    hud.draw(stdscr, state.mode, filename, window.n_cols + 1, row_offset=1)
    
    # Position cursor (accounting for gutter)
    translated_row, translated_col = window.translate(cursor)
    translated_row = max(0, min(translated_row + 1, window.n_rows))
    translated_col = max(0, min(translated_col + ln_width, window.n_cols - 1))
    stdscr.move(translated_row, translated_col)

    return ln_width


# ──────────────────────────────────
#  MAIN
# ──────────────────────────────────

def main(stdscr):
    window = Window(curses.LINES - 2, curses.COLS - 1)
    terminal = InlineTerminal(window)
    file_finder = FileFinder()
    cursor = Cursor() 
    state = EditorState()
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="?", default=None)
    args = parser.parse_args()
    init_colors()
    init_hud_colors()
    
    # Show splash screen if no file is given
    if args.filename is None:
        splash = SplashScreen()
        result = splash.show(stdscr)
        if result == "__quit__":
            return
        elif result == "__file_finder__":
            file_finder.visible = True
            state.finder_focused = True
            args.filename = None
        elif result == "__command__":
            args.filename = None
        elif result is not None:
            args.filename = result
    
    tab_manager = TabManager()
    
    # Create initial tab
    skip_first_tab = state.finder_focused and args.filename is None
    if args.filename:
        try:
            with open(args.filename) as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            lines = [""]
        SplashScreen.add_recent_file(args.filename)
        buffer = Buffer(lines if lines else [""])
        first_tab = Tab(args.filename, buffer)
        tab_manager.add_tab(first_tab)
    elif not skip_first_tab:
        buffer = Buffer([""])
        first_tab = Tab(NEW_FILE_NAME, buffer)
        tab_manager.add_tab(first_tab)
    
    curses.curs_set(1)
    
    # MAIN LOOP 
    while state.running:
        stdscr.erase() 
        curses.update_lines_cols()
        window.n_rows = curses.LINES - 2
        window.n_cols = curses.COLS - 1
        
        # If no tabs yet (waiting for file finder), just render finder and wait
        if not tab_manager.tabs:
            if file_finder.visible:
                file_finder.draw(stdscr, 0, window.n_rows, row_offset=0)
            stdscr.timeout(100)
            try:
                k = stdscr.getkey()
            except curses.error:
                continue
            if state.finder_focused:
                result = file_finder.handle_key(k)
                if result == "blur":
                    buffer = Buffer([""])
                    tab_manager.add_tab(Tab(NEW_FILE_NAME, buffer))
                    state.finder_focused = False
                    file_finder.visible = False
                elif result:
                    try:
                        with open(result) as f:
                            new_lines = f.read().splitlines()
                    except FileNotFoundError:
                        new_lines = [""]
                    buffer = Buffer(new_lines if new_lines else [""])
                    tab_manager.add_tab(Tab(result, buffer))
                    SplashScreen.add_recent_file(result)
                    state.finder_focused = False
                    file_finder.visible = False
            continue

        tab = tab_manager.active_tab
        buffer = tab.buffer
        
        # Clamp window/cursor to buffer bounds
        if window.row > max(buffer.bottom - window.n_rows + 1, 0):
            window.row = max(buffer.bottom - window.n_rows + 1, 0)
        if cursor.row < window.row:
            cursor.row = window.row
        elif cursor.row > window.row + window.n_rows - 1:
            cursor.row = window.row + window.n_rows - 1
        cursor._clamp_col(buffer)

        state.modified = tab.modified

        # Draw everything
        ln_width = draw_editor(stdscr, buffer, window, cursor, tab_manager, terminal,
                               file_finder, state, search_state, visual_state, hud)
        
        # Wire up gutter for horizontal scroll
        window.horizontal_scroll(cursor, gutter=ln_width)

        stdscr.timeout(100)
        try:
            k = stdscr.getkey()
        except curses.error:
            continue

        handle_keypress(k, stdscr, window, buffer, cursor, tab.filename, state, terminal, tab_manager, file_finder)
        
        tab.modified = state.modified


if __name__ == "__main__":
    curses.wrapper(main)