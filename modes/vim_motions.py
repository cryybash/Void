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

from editing import save_snapshot, undo, redo
from search import search_state
from keys import KEY_CTRL_D, KEY_CTRL_U, KEY_CTRL_R

# CLIPBOARD for yank/paste
clipboard = []


# ──────────────────────────────────
#        VIM MOTION FUNCTIONS
# ──────────────────────────────────

def motion_h(buffer, cursor, window):
    if cursor.col > 0:
        cursor.col -= 1

def motion_l(buffer, cursor, window):
    if cursor.col < len(buffer[cursor.row]) - 1:
        cursor.col += 1
    elif cursor.col < len(buffer[cursor.row]):
        cursor.col = len(buffer[cursor.row])

def motion_j(buffer, cursor, window):
    if cursor.row < buffer.bottom:
        cursor.row += 1
        cursor._clamp_col(buffer)
        window.down(buffer, cursor)

def motion_k(buffer, cursor, window):
    if cursor.row > 0:
        cursor.row -= 1
        cursor._clamp_col(buffer)
        window.up(cursor)

def motion_w(buffer, cursor, window):
    row, col = cursor.row, cursor.col
    line = buffer[row]

    if col >= len(line):
        if row < buffer.bottom:
            cursor.row += 1
            cursor.col = 0
            new_line = buffer[cursor.row]
            i = 0
            while i < len(new_line) and new_line[i] == " ":
                i += 1
            cursor.col = i
            window.down(buffer, cursor)
        return

    i = col
    if line[i].isalnum() or line[i] == "_":
        while i < len(line) and (line[i].isalnum() or line[i] == "_"):
            i += 1
    elif not line[i].isspace():
        while i < len(line) and not line[i].isalnum() and line[i] != "_" and not line[i].isspace():
            i += 1

    while i < len(line) and line[i].isspace():
        i += 1

    if i >= len(line):
        if row < buffer.bottom:
            cursor.row += 1
            cursor.col = 0
            new_line = buffer[cursor.row]
            j = 0
            while j < len(new_line) and new_line[j] == " ":
                j += 1
            cursor.col = j
            window.down(buffer, cursor)
        else:
            cursor.col = max(len(line) - 1, 0)
    else:
        cursor.col = i

def motion_b(buffer, cursor, window):
    row, col = cursor.row, cursor.col
    line = buffer[row]

    if col == 0:
        if row > 0:
            cursor.row -= 1
            cursor.col = max(len(buffer[cursor.row]) - 1, 0)
            window.up(cursor)
        return

    i = col - 1
    while i > 0 and line[i].isspace():
        i -= 1

    if i >= 0 and (line[i].isalnum() or line[i] == "_"):
        while i > 0 and (line[i - 1].isalnum() or line[i - 1] == "_"):
            i -= 1
    elif i >= 0 and not line[i].isspace():
        while i > 0 and not line[i - 1].isalnum() and line[i - 1] != "_" and not line[i - 1].isspace():
            i -= 1

    cursor.col = i

def motion_0(buffer, cursor, window):
    cursor.col = 0

def motion_dollar(buffer, cursor, window):
    cursor.col = max(len(buffer[cursor.row]) - 1, 0)

def motion_caret(buffer, cursor, window):
    line = buffer[cursor.row]
    i = 0
    while i < len(line) and line[i].isspace():
        i += 1
    cursor.col = i

def motion_gg(buffer, cursor, window):
    cursor.row = 0
    cursor.col = 0
    window.row = 0

def motion_G(buffer, cursor, window):
    cursor.row = buffer.bottom
    cursor._clamp_col(buffer)
    if cursor.row > window.n_rows - 1:
        window.row = cursor.row - window.n_rows + 1

# ──────────────────────────────────
#  OPERATOR FUNCTIONS
# ──────────────────────────────────

def op_delete_line(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    clipboard = [buffer[cursor.row]]
    if len(buffer) == 1:
        buffer.lines[0] = ""
        cursor.col = 0
    else:
        buffer.lines.pop(cursor.row)
        if cursor.row > buffer.bottom:
            cursor.row = buffer.bottom
        cursor._clamp_col(buffer)
    return True

def op_yank_line(buffer, cursor, window):
    global clipboard
    clipboard = [buffer[cursor.row]]
    return False

def op_paste_after(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    if not clipboard:
        return False
    for i, line in enumerate(clipboard):
        buffer.lines.insert(cursor.row + 1 + i, line)
    cursor.row += 1
    cursor.col = 0
    cursor._clamp_col(buffer)
    window.down(buffer, cursor)
    return True

def op_paste_before(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    if not clipboard:
        return False
    for i, line in enumerate(clipboard):
        buffer.lines.insert(cursor.row + i, line)
    cursor.col = 0
    cursor._clamp_col(buffer)
    return True

def op_delete_char(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    line = buffer[cursor.row]
    if len(line) == 0:
        return False
    col = cursor.col
    if col < len(line):
        buffer.lines[cursor.row] = line[:col] + line[col + 1:]
        if cursor.col >= len(buffer[cursor.row]) and cursor.col > 0:
            cursor.col -= 1
        return True
    return False

def op_open_below(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    buffer.lines.insert(cursor.row + 1, "")
    cursor.row += 1
    cursor.col = 0
    window.down(buffer, cursor)
    return "insert"

def op_open_above(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    buffer.lines.insert(cursor.row, "")
    cursor.col = 0
    return "insert"


# ──────────────────────────────────
#  DELETE WITH MOTION (d + motion)
# ──────────────────────────────────

def delete_to_end(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    line = buffer[cursor.row]
    clipboard = [line[cursor.col:]]
    buffer.lines[cursor.row] = line[:cursor.col]
    if cursor.col > 0:
        cursor.col -= 1
    return True

def delete_to_start(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    line = buffer[cursor.row]
    clipboard = [line[:cursor.col]]
    buffer.lines[cursor.row] = line[cursor.col:]
    cursor.col = 0
    return True

def delete_word(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    line = buffer[cursor.row]
    start = cursor.col
    
    i = start
    if i < len(line):
        if line[i].isalnum() or line[i] == "_":
            while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                i += 1
        elif not line[i].isspace():
            while i < len(line) and not line[i].isalnum() and line[i] != "_" and not line[i].isspace():
                i += 1
        while i < len(line) and line[i].isspace():
            i += 1

    clipboard = [line[start:i]]
    buffer.lines[cursor.row] = line[:start] + line[i:]
    cursor._clamp_col(buffer)
    return True

def delete_to_top(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    clipboard = buffer.lines[:cursor.row + 1]
    buffer.lines = buffer.lines[cursor.row + 1:] if cursor.row + 1 < len(buffer) else [""]
    cursor.row = 0
    cursor.col = 0
    window.row = 0
    return True

def delete_to_bottom(buffer, cursor, window, tab=None):
    save_snapshot(buffer, cursor, tab)
    global clipboard
    clipboard = buffer.lines[cursor.row:]
    buffer.lines = buffer.lines[:cursor.row] if cursor.row > 0 else [""]
    if cursor.row > buffer.bottom:
        cursor.row = buffer.bottom
    cursor._clamp_col(buffer)
    return True


# ──────────────────────────────────
#  PENDING STATE & DISPATCH
# ──────────────────────────────────

pending_op = None
key_buffer = ""


def reset_pending():
    global pending_op, key_buffer
    pending_op = None
    key_buffer = ""

def handle_vim_motion(k, buffer, cursor, window, tab=None):
    global pending_op, key_buffer
    modified = False
    mode_change = None

    key_buffer += k

    # PENDING OPERATOR: waiting for a motion after d, y, etc.
    if pending_op == "d":
        if key_buffer == "dd":
            modified = op_delete_line(buffer, cursor, window, tab)
            reset_pending()
            return modified, mode_change
        elif key_buffer == "dw":
            modified = delete_word(buffer, cursor, window, tab)
            reset_pending()
            return modified, mode_change
        elif key_buffer == "d$":
            modified = delete_to_end(buffer, cursor, window, tab)
            reset_pending()
            return modified, mode_change
        elif key_buffer == "d0":
            modified = delete_to_start(buffer, cursor, window, tab)
            reset_pending()
            return modified, mode_change
        elif key_buffer == "dG":
            modified = delete_to_bottom(buffer, cursor, window, tab)
            reset_pending()
            return modified, mode_change
        elif key_buffer == "dg":
            return modified, mode_change
        elif key_buffer == "dgg":
            modified = delete_to_top(buffer, cursor, window, tab)
            reset_pending()
            return modified, mode_change
        else:
            reset_pending()
            return modified, mode_change

    if pending_op == "y":
        if key_buffer == "yy":
            op_yank_line(buffer, cursor, window)
            reset_pending()
            return modified, mode_change
        else:
            reset_pending()
            return modified, mode_change

    # SINGLE KEY MOTIONS
    if key_buffer == "h":
        motion_h(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "j":
        motion_j(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "k":
        motion_k(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "l":
        motion_l(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "w":
        motion_w(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "b":
        motion_b(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "0":
        motion_0(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "$":
        motion_dollar(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "^":
        motion_caret(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "G":
        motion_G(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "g":
        pass  # waiting for second key
    elif key_buffer == "gg":
        motion_gg(buffer, cursor, window)
        reset_pending()
    elif key_buffer == "gt":
        reset_pending()
        return "tab_next", None
    elif key_buffer == "gT":
        reset_pending()
        return "tab_prev", None
    elif key_buffer == "n":
        search_state.next_match(cursor, window, buffer)
        reset_pending()
    elif key_buffer == "N":
        search_state.prev_match(cursor, window, buffer)
        reset_pending()
    elif key_buffer == "d":
        pending_op = "d"
    elif key_buffer == "y":
        pending_op = "y"
    elif key_buffer == "x":
        modified = op_delete_char(buffer, cursor, window, tab)
        reset_pending()
    elif key_buffer == "p":
        modified = op_paste_after(buffer, cursor, window, tab)
        reset_pending()
    elif key_buffer == "P":
        modified = op_paste_before(buffer, cursor, window, tab)
        reset_pending()
    elif key_buffer == "o":
        result = op_open_below(buffer, cursor, window, tab)
        modified = True
        mode_change = result
        reset_pending()
    elif key_buffer == "O":
        result = op_open_above(buffer, cursor, window, tab)
        modified = True
        mode_change = result
        reset_pending()
    elif key_buffer == KEY_CTRL_D:
        window.half_page_down(buffer, cursor)
        reset_pending()
    elif key_buffer == KEY_CTRL_U:
        window.half_page_up(buffer, cursor)
        reset_pending()
    elif key_buffer == "u":
        modified = undo(buffer, cursor, window, tab)
        reset_pending()
    elif key_buffer == KEY_CTRL_R:
         modified = redo(buffer, cursor, window, tab)
         reset_pending()
    else:
        reset_pending()

    if pending_op is None and key_buffer not in ("g",):
        key_buffer = ""

    return modified, mode_change