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
from ui.syntax import tokenize_line, detect_language
from config.colors import (COLOR_KEYWORD, COLOR_STRING, COLOR_COMMENT,
                           COLOR_NUMBER, COLOR_BUILTIN, COLOR_DECORATOR,
                           COLOR_LINE_NUM, COLOR_NORMAL, COLOR_STATUS,
                           COLOR_DEFINITION, COLOR_FUNC_NAME, COLOR_INDENT_GUIDE,
                           COLOR_TAB_ACTIVE, COLOR_TAB_INACTIVE, COLOR_SEARCH_MATCH,
                           COLOR_SEARCH_CURRENT, COLOR_CURSOR_LINE, COLOR_VISUAL_SELECT,
                           COLOR_INDENT_ACTIVE, COLOR_MATCH_PAIR, COLOR_MATCH_BOOL)


# curses safety guards
def safe_addstr(stdscr, row, col, text, attr=0):
    try:
        stdscr.addstr(row, col, text, attr)
    except curses.error:
        pass

# curses safety guards
def safe_addch(stdscr, row, col, ch, attr=0):
    try:
        stdscr.addch(row, col, ch, attr)
    except curses.error:
        pass


# Initialize curses color pairs, calls once after curses.start_color()
def init_colors():
    curses.start_color()
    curses.use_default_colors()
    
    # Normal 0-7: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    # Bright 8-15: same but brighter variants
    BRIGHT_BLACK = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15

    curses.init_pair(COLOR_KEYWORD, curses.COLOR_RED, -1)
    curses.init_pair(COLOR_STRING, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_COMMENT, BRIGHT_GREEN, -1)
    curses.init_pair(COLOR_NUMBER, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_BUILTIN, curses.COLOR_MAGENTA, -1)
    curses.init_pair(COLOR_DECORATOR, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_LINE_NUM, BRIGHT_BLACK, -1)
    curses.init_pair(COLOR_NORMAL, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_DEFINITION, BRIGHT_MAGENTA, -1)
    curses.init_pair(COLOR_FUNC_NAME, BRIGHT_CYAN, -1)
    curses.init_pair(COLOR_INDENT_GUIDE, BRIGHT_BLACK, -1)
    curses.init_pair(COLOR_TAB_ACTIVE, curses.COLOR_BLACK, BRIGHT_CYAN)
    curses.init_pair(COLOR_TAB_INACTIVE, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_SEARCH_MATCH, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(COLOR_SEARCH_CURRENT, curses.COLOR_YELLOW, BRIGHT_GREEN)
    curses.init_pair(COLOR_CURSOR_LINE, -1, 235)
    curses.init_pair(COLOR_VISUAL_SELECT, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(COLOR_INDENT_ACTIVE, curses.COLOR_BLUE, -1)
    curses.init_pair(COLOR_MATCH_PAIR, BRIGHT_YELLOW, -1)
    curses.init_pair(COLOR_MATCH_BOOL, curses.COLOR_YELLOW, -1) # NEW 

def draw_tab_bar(stdscr, tab_manager, n_cols):
    col = 0
    for i, tab in enumerate(tab_manager.tabs):
        name = f" {tab.display_name} "
        if i == tab_manager.active_index:
            color = curses.color_pair(COLOR_TAB_ACTIVE)
        else:
            color = curses.color_pair(COLOR_TAB_INACTIVE) | curses.A_DIM
        if col + len(name) < n_cols:
            safe_addstr(stdscr, 0, col, name, color)
            col += len(name)


def draw_indent_guides(stdscr, buffer, window, editor_rows, ln_width, max_cols, cursor_row=None, cursor_col=None, row_offset=0):
    tab_width = 4

    # Figure out which indent level the cursor belongs to
    active_level = -1
    if cursor_row is not None:
        cursor_line = buffer[cursor_row] if cursor_row < len(buffer) else ""
        if cursor_line.strip():
            cursor_indent = len(cursor_line) - len(cursor_line.lstrip())
        else:
            # On a blank line, look at surrounding context
            cursor_indent = 0
            for look in range(cursor_row + 1, min(cursor_row + 50, len(buffer))):
                if buffer[look].strip():
                    cursor_indent = len(buffer[look]) - len(buffer[look].lstrip())
                    break
            for look in range(cursor_row - 1, max(cursor_row - 50, -1), -1):
                if buffer[look].strip():
                    above = len(buffer[look]) - len(buffer[look].lstrip())
                    cursor_indent = min(cursor_indent, above) if cursor_indent > 0 else above
                    break

        if cursor_indent > 0:
            active_level = (cursor_indent - 1) // tab_width

        # Also highlight if cursor is physically sitting on a guide
        if cursor_col is not None and cursor_col % tab_width == 0:
            guide_level = cursor_col // tab_width
            cursor_line_indent = len(cursor_line) - len(cursor_line.lstrip()) if cursor_line.strip() else cursor_indent
            if guide_level < cursor_line_indent // tab_width:
                active_level = guide_level

    # Find the range of the active block (how far up/down the active guide extends)
    active_top = -1
    active_bot = -1
    if active_level >= 0 and cursor_row is not None:
        required_indent = (active_level + 1) * tab_width

        # Scan upward to find block start
        active_top = cursor_row
        for row in range(cursor_row - 1, -1, -1):
            line = buffer[row]
            if line.strip():
                line_indent = len(line) - len(line.lstrip())
                if line_indent < required_indent:
                    break
                active_top = row
            else:
                active_top = row  # blank lines inside blocks are included

        # Scan downward to find block end
        active_bot = cursor_row
        for row in range(cursor_row + 1, len(buffer)):
            line = buffer[row]
            if line.strip():
                line_indent = len(line) - len(line.lstrip())
                if line_indent < required_indent:
                    break
                active_bot = row
            else:
                active_bot = row

    # Draw the guides
    visible_lines = buffer[window.row:window.row + editor_rows]

    for screen_row, line in enumerate(visible_lines):
        buf_row = window.row + screen_row

        if line.strip():
            indent = len(line) - len(line.lstrip())
        else:
            indent = 0
            for look in range(buf_row + 1, min(buf_row + 50, len(buffer))):
                if buffer[look].strip():
                    indent = len(buffer[look]) - len(buffer[look].lstrip())
                    break
            for look in range(buf_row - 1, max(buf_row - 50, -1), -1):
                if buffer[look].strip():
                    above_indent = len(buffer[look]) - len(buffer[look].lstrip())
                    indent = min(indent, above_indent) if indent > 0 else above_indent
                    break

        num_guides = indent // tab_width
        for level in range(num_guides):
            col = ln_width + (level * tab_width) - window.col
            if col < ln_width or col >= max_cols:
                continue
            char_index = level * tab_width
            if char_index < len(line) and line[char_index] != " ":
                continue

            # Determine if this guide segment should be highlighted
            is_active = (level == active_level and active_top <= buf_row <= active_bot)

            if is_active:
                attr = curses.color_pair(COLOR_INDENT_ACTIVE) | curses.A_BOLD
            else:
                attr = curses.color_pair(COLOR_INDENT_GUIDE) | curses.A_DIM

            safe_addch(stdscr, screen_row + row_offset, col, curses.ACS_VLINE, attr)



# Calculate width needed for line numbers
def line_num_width(buffer):
    return len(str(len(buffer))) + 1  # +1 for padding space

def draw_line_number(stdscr, row, line_number, width):
    num_str = str(line_number).rjust(width - 1) + " "
    safe_addstr(stdscr, row, 0, num_str, curses.color_pair(COLOR_LINE_NUM))

def draw_line(stdscr, row, col_offset, line, lang, max_cols, bg_attr=None):
    tokens = tokenize_line(line, lang)
    screen_col = col_offset
    for text, color in tokens:
        if screen_col >= max_cols:
            break
        # truncate if it would go past the edge
        remaining = max_cols - screen_col
        display_text = text[:remaining]
        attr = curses.color_pair(color)
        if bg_attr is not None:
            attr |= bg_attr
        safe_addstr(stdscr, row, screen_col, display_text, attr)
        screen_col += len(display_text)

def draw_status_bar(stdscr, row, window, cursor, filename, modified, mode, search_info=""):
    mode_display = f" -- {mode.upper()} -- "
    mod_indicator = " [+]" if modified else ""
    search_display = f" {search_info}" if search_info else ""
    left_side = f"{mode_display} {filename}{mod_indicator}{search_display}"
    right_side = f"Ln {cursor.row + 1}, Col {cursor.col + 1} "

    # MIDDLE PADDING TO FILL FULL WIDTH
    padding = window.n_cols + 1 - len(left_side) - len(right_side)
    status = left_side + " " * max(padding, 1) + right_side

    safe_addstr(stdscr, row, 0, status, curses.color_pair(COLOR_STATUS))
        
def draw_search_highlights(stdscr, buffer, window, editor_rows, ln_width, max_cols, search_state, row_offset=0): 
    if not search_state.active or not search_state.query:
        return
        
    query = search_state.query
    query_len = len(query)
    
    for match_idx, (match_row, match_col) in enumerate(search_state.matches):          
        screen_row = match_row - window.row
        if screen_row < 0 or screen_row >= editor_rows:
            continue
          
        screen_col = ln_width + match_col - window.col
        if screen_col >= max_cols or screen_col + query_len <= ln_width:
            continue
            
        if match_idx == search_state.match_index:
            color = curses.color_pair(COLOR_SEARCH_CURRENT)
        else:
            color = curses.color_pair(COLOR_SEARCH_MATCH)
        
        line = buffer[match_row]
        highlight_text = line[match_col:match_col + query_len]
        
        draw_col = max(screen_col, ln_width)
        trim_left = draw_col - screen_col
        remaining = max_cols - draw_col
        display_text = highlight_text[trim_left:trim_left + remaining]
        
        if display_text:
            safe_addstr(stdscr, screen_row + row_offset, draw_col, display_text, color)
                
# Highlight the matching bracket/quote pair for the character under the cursor
def draw_matching_pair(stdscr, buffer, window, cursor, ln_width, max_cols, editor_rows, row_offset=0):
    PAIRS = {
        "(": (")", 1),
        ")": ("(", -1),
        "[": ("]", 1),
        "]": ("[", -1),
        "{": ("}", 1),
        "}": ("{", -1),
    }
    QUOTES = {'"', "'"}

    row, col = cursor.row, cursor.col
    line = buffer[row] if row < len(buffer) else ""

    if col >= len(line):
        return

    ch = line[col]

    match_row, match_col = -1, -1

    if ch in PAIRS:
        # Bracket matching
        target, direction = PAIRS[ch]
        depth = 0
        r, c = row, col

        while 0 <= r < len(buffer):
            scan_line = buffer[r]
            while 0 <= c < len(scan_line):
                scan_ch = scan_line[c]
                if scan_ch == ch:
                    depth += 1
                elif scan_ch == target:
                    depth -= 1
                    if depth == 0:
                        match_row, match_col = r, c
                        break
                c += direction

            if match_row != -1:
                break

            r += direction
            if 0 <= r < len(buffer):
                c = 0 if direction == 1 else len(buffer[r]) - 1

    elif ch in QUOTES:
        # Quote matching
        # Count quotes before cursor
        count_before = line[:col].count(ch)

        if count_before % 2 == 0:
            # This is an opening quote, search forward
            for c in range(col + 1, len(line)):
                if line[c] == ch:
                    match_row, match_col = row, c
                    break
        else:
            # This is a closing quote, search backward
            for c in range(col - 1, -1, -1):
                if line[c] == ch:
                    match_row, match_col = row, c
                    break
    else:
        return

    if match_row == -1:
        return

    # Draw highlight on the matching character
    screen_row = match_row - window.row
    if screen_row < 0 or screen_row >= editor_rows:
        return

    screen_col = ln_width + match_col - window.col
    if screen_col < ln_width or screen_col >= max_cols:
        return

    match_ch = buffer[match_row][match_col]
    attr = curses.color_pair(COLOR_MATCH_PAIR) | curses.A_BOLD | curses.A_UNDERLINE

    safe_addstr(stdscr, screen_row + row_offset, screen_col, match_ch, attr)

    # Also highlight the character under the cursor itself
    cursor_screen_row = row - window.row
    cursor_screen_col = ln_width + col - window.col
    if 0 <= cursor_screen_row < editor_rows and ln_width <= cursor_screen_col < max_cols:
        safe_addstr(stdscr, cursor_screen_row + row_offset, cursor_screen_col, ch, attr)

def draw_visual_selection(stdscr, buffer, window, editor_rows, ln_width, max_cols, visual_state, cursor, row_offset=0):
    if not visual_state.active:
        return

    color = curses.color_pair(COLOR_VISUAL_SELECT)
    ar, ac = visual_state.anchor_row, visual_state.anchor_col
    cr, cc = cursor.row, cursor.col

    for screen_row in range(editor_rows):
        buf_row = window.row + screen_row
        if buf_row >= len(buffer):
            break

        line = buffer[buf_row]

        # Determine which columns are selected on this row
        if visual_state.mode == "char":
            if (ar, ac) <= (cr, cc):
                s_row, s_col, e_row, e_col = ar, ac, cr, cc
            else:
                s_row, s_col, e_row, e_col = cr, cc, ar, ac

            if buf_row < s_row or buf_row > e_row:
                continue
            if buf_row == s_row and buf_row == e_row:
                col_start, col_end = s_col, min(e_col, len(line) - 1)
            elif buf_row == s_row:
                col_start, col_end = s_col, len(line) - 1
            elif buf_row == e_row:
                col_start, col_end = 0, min(e_col, len(line) - 1)
            else:
                col_start, col_end = 0, len(line) - 1

        elif visual_state.mode == "line":
            top = min(ar, cr)
            bot = max(ar, cr)
            if buf_row < top or buf_row > bot:
                continue
            col_start = 0
            col_end = len(line) - 1
            
            # Also highlight empty space past end of line
            start_sc = ln_width + len(line) - window.col
            for sc in range(max(start_sc, ln_width), max_cols):
                safe_addstr(stdscr, screen_row + row_offset, sc, " ", color)

        elif visual_state.mode == "block":
            top = min(ar, cr)
            bot = max(ar, cr)
            left = min(ac, cc)
            right_col = max(ac, cc)
            if buf_row < top or buf_row > bot:
                continue
            col_start = left
            col_end = min(right_col, len(line) - 1)
        else:
            continue

        # Draw the selected characters
        for buf_col in range(col_start, col_end + 1):
            if buf_col >= len(line):
                break
            screen_col = ln_width + buf_col - window.col
            if ln_width <= screen_col < max_cols:
                ch = line[buf_col]
                safe_addstr(stdscr, screen_row + row_offset, screen_col, ch, color)
                
