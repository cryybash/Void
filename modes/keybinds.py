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
from core.buffer import Buffer
from modes.vim_motions import handle_vim_motion, reset_pending
from core.editing import auto_indent, save_snapshot
from core.tab import Tab
from modes.search import search_state, search_prompt
from ui.splash import SplashScreen
from modes.visual import visual_state, visual_delete, visual_yank, visual_change, visual_indent
from ui.display import draw_status_bar
from config.settings import create_default_config, CONFIG_PATH
from ui.aesthetics import hud
from config.keys import (KEY_ESCAPE, KEY_CTRL_T, KEY_CTRL_F, KEY_CTRL_V, KEY_CTRL_D,
                  KEY_CTRL_U, KEY_ENTER, KEY_BACKSPACE_CODES, KEY_DELETE_CODES,
                  NEW_FILE_NAME, INDENT_WIDTH)


# ------------------------------
#  EDITOR STATE
#  Bundles mode and focus flags
# ------------------------------ 

class EditorState:
    def __init__(self):
        self.mode = "normal"
        self.modified = False
        self.terminal_focused = False
        self.finder_focused = False
        self.running = True
        self._insert_snapshot_saved = False  # for batched undo


# ---------
#  HELPERS
# --------- 

def right(window, buffer, cursor):
    cursor.right(buffer)
    window.down(buffer, cursor)
    window.horizontal_scroll(cursor)

def left(window, buffer, cursor):
    cursor.left(buffer)
    window.up(cursor)
    window.horizontal_scroll(cursor)

def save(filename, buffer):
    if not filename or filename in (NEW_FILE_NAME,):
        return False
    with open(filename, "w") as f:
        f.write("\n".join(buffer.lines) + "\n")
    return True

# Shared helper for opening a file into a new tab, returns the new tab
def open_file_in_tab(filepath, tab_manager, cursor, window):
    existing = tab_manager.find_tab(filepath)
    if existing != -1:
        if tab_manager.active_tab:
            tab_manager.active_tab.save_cursor(cursor, window)
        tab_manager.go_to_tab(existing)
        tab_manager.active_tab.restore_cursor(cursor, window)
        return tab_manager.active_tab

    if tab_manager.active_tab:
        tab_manager.active_tab.save_cursor(cursor, window)
    try:
        with open(filepath) as f:
            new_lines = f.read().splitlines()
    except FileNotFoundError:
        new_lines = [""]
    SplashScreen.add_recent_file(filepath)
    new_buffer = Buffer(new_lines if new_lines else [""])
    new_tab = Tab(filepath, new_buffer)
    tab_manager.add_tab(new_tab)
    tab_manager.active_tab.restore_cursor(cursor, window)
    return new_tab

def switch_tab(tab_manager, cursor, window, direction):
    tab_manager.active_tab.save_cursor(cursor, window)
    if direction == "next":
        tab_manager.next_tab()
    elif direction == "prev":
        tab_manager.prev_tab()
    tab_manager.active_tab.restore_cursor(cursor, window)
   
    # Reset global state that shouldn't persist across tabs
    visual_state.reset()
    search_state.reset()
    reset_pending()
    hud.reset_timer()


# --------------
#  COMMAND MODE
# -------------- 

def command_mode(stdscr, window, buffer, filename, modified, tab_manager, cursor):
    stdscr.timeout(-1)
    curses.curs_set(1)
    hud.draw(stdscr, "command", filename, window.n_cols + 1, row_offset=1)
    draw_status_bar(stdscr, window.n_rows + 1, window, cursor, filename, modified, "command") 
    stdscr.addstr(window.n_rows, 0, ":" + " " * (window.n_cols - 1))
    stdscr.move(window.n_rows, 1)
    cmd = ""
    
    while True:
        ch = stdscr.getkey()
        if ch == KEY_ENTER:
            break
        elif ch in KEY_BACKSPACE_CODES:
            if cmd:
                cmd = cmd[:-1]
            else:
                break
        elif ch == KEY_ESCAPE:
            cmd = ""
            break
        else:
            cmd += ch

        stdscr.addstr(window.n_rows, 0, ":" + cmd + " " * (window.n_cols - len(cmd) - 1))
        stdscr.move(window.n_rows, len(cmd) + 1)

    if cmd == "w":
        if save(filename, buffer):
            modified = False
        else:
            stdscr.addstr(window.n_rows, 0, "No filename. Use :saveas <filename>" + " " * 20)
            stdscr.getkey()
    elif cmd == "wq":
        if save(filename, buffer):
            stdscr.timeout(100)
            return "__quit__"
        else:
            stdscr.addstr(window.n_rows, 0, "No filename. Use :saveas <filename>" + " " * 20)
            stdscr.getkey()
    elif cmd == "q":
        if modified:
            stdscr.addstr(window.n_rows, 0, "Unsaved changes! Use :q! to force quit" + " " * 20)
            stdscr.getkey()
        else:
            stdscr.timeout(100)
            return "__quit__"
    elif cmd == "q!":
        stdscr.timeout(100)
        return "__quit__"
    elif cmd in ("tabn", "tabnext"):
        switch_tab(tab_manager, cursor, window, "next")
    elif cmd in ("tabp", "tabprev"):
        switch_tab(tab_manager, cursor, window, "prev")
    elif cmd in ("tabc", "tabclose"):
        tab_manager.close_tab()
    elif cmd.startswith("e "):
        filepath = cmd[2:].strip()
        if filepath:
            open_file_in_tab(filepath, tab_manager, cursor, window)
    elif cmd.startswith("tabnew "):
        filepath = cmd[7:].strip()
        if filepath:
            open_file_in_tab(filepath, tab_manager, cursor, window)
    elif cmd.startswith("saveas "):
        new_filename = cmd[7:].strip()
        if new_filename:
            tab_manager.active_tab.filename = new_filename
            save(new_filename, buffer)
            SplashScreen.add_recent_file(new_filename)
            modified = False
    elif cmd == "config":
        create_default_config()
        open_file_in_tab(CONFIG_PATH, tab_manager, cursor, window)

    stdscr.timeout(100)
    return modified


# --------------------
#  MAIN KEY DISPATCH
# -------------------- 

def handle_keypress(k, stdscr, window, buffer, cursor, filename, state, terminal, tab_manager, file_finder):
    tab = tab_manager.active_tab

    # Terminal focus toggle
    if k == KEY_CTRL_T:
        if state.terminal_focused:
            terminal.visible = False
            state.terminal_focused = False
        elif terminal.visible:
            state.terminal_focused = True
        else:
            terminal.visible = True
            state.terminal_focused = True
        return
    
    if state.terminal_focused:
        result = terminal.handle_key(k)
        if result == "blur":
            state.terminal_focused = False
        return
    
    # File finder focus toggle
    if k == KEY_CTRL_F:
        if state.finder_focused:
            file_finder.visible = False
            state.finder_focused = False
        elif file_finder.visible:
            state.finder_focused = True
        else:
            file_finder.visible = True
            file_finder.refresh_files()
            state.finder_focused = True
        return
        
    if state.finder_focused:
        result = file_finder.handle_key(k)
        if result == "blur":
            state.finder_focused = False
        elif result:
            open_file_in_tab(result, tab_manager, cursor, window)
            state.finder_focused = False
            file_finder.visible = False
        return
        
    # --------------------------
    #  NORMAL MODE
    # -------------------------- 
    if state.mode == "normal":
        if k == ":":
            state.mode = "command"
            result = command_mode(stdscr, window, buffer, filename, state.modified, tab_manager, cursor)
            
            if result == "__quit__":
                state.running = False
                return
            
            if result is not None:
                state.modified = result
            state.mode = "normal"
        elif k == "/":
            query = search_prompt(stdscr, window)
            if query:
                parts = query.split("/")
                if len(parts) == 3 and parts[2] in ("g", "gc"):
                    find_text, replace_text, flag = parts
                    search_state.find_all(buffer, find_text)
                    
                    if search_state.matches:
                        save_snapshot(buffer, cursor, tab)
                        
                        if flag == "gc":
                            search_state.replacement = replace_text
                            search_state.confirming = True
                            search_state.match_index = 0
                            search_state._jump_to_match(cursor, window, buffer)
                        else:
                            count = search_state.replace_all(buffer, replace_text)
                            state.modified = True
                else:
                    search_state.find_all(buffer, query)
                    search_state.next_match(cursor, window, buffer)
                
        elif k == KEY_ESCAPE:
            search_state.reset()
        
        elif search_state.confirming and k in ("y", "n", "a", "q"):
            if k == "y":
                row, col = search_state.matches[search_state.match_index]
                line = buffer.lines[row]
                buffer.lines[row] = line[:col] + search_state.replacement + line[col + len(search_state.query):]
                state.modified = True
                search_state.find_all(buffer, search_state.query)
                
                if not search_state.matches:
                    search_state.reset()
                else:
                    search_state.confirming = True
                    search_state.match_index = min(search_state.match_index, len(search_state.matches) - 1)
                    search_state._jump_to_match(cursor, window, buffer)
            elif k == "n":
                if len(search_state.matches) <= 1:
                    search_state.reset()
                else:
                    search_state.match_index = (search_state.match_index + 1) % len(search_state.matches)
                    search_state._jump_to_match(cursor, window, buffer)
            elif k == "a":
                search_state.replace_all(buffer, search_state.replacement)
                state.modified = True
            elif k == "q":
                search_state.reset()
                
        elif k == "i":
            state.mode = "insert"
            state._insert_snapshot_saved = False
            print("\033[6 q", end="", flush=True)
        elif k == "v":
            visual_state.start("char", cursor)
            state.mode = "visual"
        elif k == "V":
            visual_state.start("line", cursor)
            state.mode = "visual-line"
        elif k == KEY_CTRL_V:
            visual_state.start("block", cursor)
            state.mode = "visual-block"
        elif k == "KEY_UP":
            cursor.up(buffer)
            window.up(cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_DOWN":
            cursor.down(buffer)
            window.down(buffer, cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_LEFT":
            cursor.left(buffer)
            window.up(cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_RIGHT":
            right(window, buffer, cursor)
        else:
            result, mode_change = handle_vim_motion(k, buffer, cursor, window, tab)
            if result == "tab_next":
                switch_tab(tab_manager, cursor, window, "next")
            elif result == "tab_prev":
                switch_tab(tab_manager, cursor, window, "prev")
            elif result:
                state.modified = True
            if mode_change:
                state.mode = mode_change
                if mode_change == "insert":
                    state._insert_snapshot_saved = False
                    print("\033[6 q", end="", flush=True)
    # -------------------------- 
    #  INSERT MODE - batched undo
    # --------------------------- 
    elif state.mode == "insert":
        if k == KEY_ESCAPE:
            state.mode = "normal"
            print("\033[2 q", end="", flush=True)
        elif k == "KEY_UP":
            cursor.up(buffer)
            window.up(cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_DOWN":
            cursor.down(buffer)
            window.down(buffer, cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_LEFT":
            cursor.left(buffer)
            window.up(cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_RIGHT":
            right(window, buffer, cursor)
        elif k == KEY_ENTER:
            if not state._insert_snapshot_saved:
                save_snapshot(buffer, cursor, tab)
                state._insert_snapshot_saved = True
            auto_indent(buffer, cursor, window)
            state.modified = True
        elif k in KEY_DELETE_CODES:
            if not state._insert_snapshot_saved:
                save_snapshot(buffer, cursor, tab)
                state._insert_snapshot_saved = True
            buffer.delete(cursor)
            state.modified = True
        
        elif k in KEY_BACKSPACE_CODES:
            if (cursor.row, cursor.col) > (0, 0):
                if not state._insert_snapshot_saved:
                    save_snapshot(buffer, cursor, tab)
                    state._insert_snapshot_saved = True
                line = buffer[cursor.row]
                text_before = line[:cursor.col]
                if text_before and text_before.isspace() and len(text_before) >= INDENT_WIDTH:
                    # Delete back to previous indent level
                    remove = len(text_before) % INDENT_WIDTH or INDENT_WIDTH
                    for _ in range(remove):
                        left(window, buffer, cursor)
                        buffer.delete(cursor)
                else:
                    left(window, buffer, cursor)
                    buffer.delete(cursor)
                state.modified = True

        elif k in ("(", "[", "{", '"', "'"):
            if not state._insert_snapshot_saved:
                save_snapshot(buffer, cursor, tab)
                state._insert_snapshot_saved = True
            pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
            buffer.insert(cursor, k + pairs[k])
            right(window, buffer, cursor)
            state.modified = True
        else:
            if not state._insert_snapshot_saved:
                save_snapshot(buffer, cursor, tab)
                state._insert_snapshot_saved = True
            buffer.insert(cursor, k)
            for _ in k:
                right(window, buffer, cursor)
            state.modified = True

    # ---------------
    #  VISUAL MODE
    # ---------------
    elif state.mode in ("visual", "visual-line", "visual-block"):
        if k == KEY_ESCAPE:
            visual_state.reset()
            state.mode = "normal"
        elif k == "v":
            if visual_state.mode == "char":
                visual_state.reset()
                state.mode = "normal"
            else:
                visual_state.mode = "char"
                state.mode = "visual"
        elif k == "V":
            if visual_state.mode == "line":
                visual_state.reset()
                state.mode = "normal"
            else:
                visual_state.mode = "line"
                state.mode = "visual-line"
        elif k == KEY_CTRL_V:
            if visual_state.mode == "block":
                visual_state.reset()
                state.mode = "normal"
            else:
                visual_state.mode = "block"
                state.mode = "visual-block"
        elif k == "h":
            if cursor.col > 0:
                cursor.col -= 1
        elif k == "l":
            if cursor.col < len(buffer[cursor.row]):
                cursor.col += 1
        elif k == "j":
            if cursor.row < buffer.bottom:
                cursor.row += 1
                cursor._clamp_col(buffer)
                window.down(buffer, cursor)
        elif k == "k":
            if cursor.row > 0:
                cursor.row -= 1
                cursor._clamp_col(buffer)
                window.up(cursor)
        elif k == "w":
            from modes.vim_motions import motion_w
            motion_w(buffer, cursor, window)
        elif k == "b":
            from modes.vim_motions import motion_b
            motion_b(buffer, cursor, window)
        elif k == "0":
            cursor.col = 0
        elif k == "$":
            cursor.col = max(len(buffer[cursor.row]) - 1, 0)
        elif k == "^":
            from modes.vim_motions import motion_caret
            motion_caret(buffer, cursor, window)
        elif k == "G":
            from modes.vim_motions import motion_G
            motion_G(buffer, cursor, window)
        elif k == "g":
            pass
        elif k == "KEY_UP":
            cursor.up(buffer)
            window.up(cursor)
        elif k == "KEY_DOWN":
            cursor.down(buffer)
            window.down(buffer, cursor)
        elif k == "KEY_LEFT":
            if cursor.col > 0:
                cursor.col -= 1
        elif k == "KEY_RIGHT":
            if cursor.col < len(buffer[cursor.row]):
                cursor.col += 1
        elif k == KEY_CTRL_D:
            window.half_page_down(buffer, cursor)
        elif k == KEY_CTRL_U:
            window.half_page_up(buffer, cursor)
        elif k == "d" or k == "x":
            state.modified = visual_delete(buffer, cursor, window, visual_state, tab)
            state.mode = "normal"
        elif k == "y":
            visual_yank(buffer, cursor, visual_state)
            state.mode = "normal"
        elif k == "c":
            result = visual_change(buffer, cursor, window, visual_state, tab)
            state.modified = True
            state.mode = result
            state._insert_snapshot_saved = False
            print("\033[6 q", end="", flush=True)
        elif k == ">":
            state.modified = visual_indent(buffer, cursor, visual_state, direction=1, tab=tab)
            state.mode = "normal"
        elif k == "<":
            state.modified = visual_indent(buffer, cursor, visual_state, direction=-1, tab=tab)
            state.mode = "normal"

        window.horizontal_scroll(cursor)
