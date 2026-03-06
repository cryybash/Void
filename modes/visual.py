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

from core.editing import save_snapshot

# -------------------
#  VISUAL MODE STATE
# -------------------

class VisualState:
    def __init__(self):
        self.active = False
        self.mode = None        # "char", "line", or "block"
        self.anchor_row = 0
        self.anchor_col = 0

    def start(self, mode, cursor):
        self.active = True
        self.mode = mode
        self.anchor_row = cursor.row
        self.anchor_col = cursor.col

    def reset(self):
        self.active = False
        self.mode = None
        self.anchor_row = 0
        self.anchor_col = 0

    def get_range(self, cursor):
        ar, ac = self.anchor_row, self.anchor_col
        cr, cc = cursor.row, cursor.col

        if self.mode == "char":
            if (ar, ac) <= (cr, cc):
                return (ar, ac, cr, cc)
            else:
                return (cr, cc, ar, ac)

        elif self.mode == "line":
            if ar <= cr:
                return (ar, 0, cr, 0)
            else:
                return (cr, 0, ar, 0)

        elif self.mode == "block":
            top = min(ar, cr)
            bot = max(ar, cr)
            left = min(ac, cc)
            right = max(ac, cc)
            return (top, left, bot, right)



# ------------------------ 
#  VISUAL MODE OPERATIONS
# ------------------------ 

# Delete the selected region, works for all three visual modes
def visual_delete(buffer, cursor, window, state, tab=None):
    import modes.vim_motions as vim_motions
    save_snapshot(buffer, cursor, tab)
    r = state.get_range(cursor)

    if state.mode == "char":
        s_row, s_col, e_row, e_col = r
        if s_row == e_row:
            line = buffer.lines[s_row]
            vim_motions.clipboard = [line[s_col:e_col + 1]]
            buffer.lines[s_row] = line[:s_col] + line[e_col + 1:]
        else:
            first = buffer.lines[s_row]
            last = buffer.lines[e_row]
            vim_motions.clipboard = (
                [first[s_col:]] +
                buffer.lines[s_row + 1:e_row] +
                [last[:e_col + 1]]
            )
            buffer.lines[s_row] = first[:s_col] + last[e_col + 1:]
            del buffer.lines[s_row + 1:e_row + 1]
        cursor.row = s_row
        cursor.col = s_col

    elif state.mode == "line":
        s_row, _, e_row, _ = r
        vim_motions.clipboard = buffer.lines[s_row:e_row + 1]
        del buffer.lines[s_row:e_row + 1]
        if not buffer.lines:
            buffer.lines = [""]
        cursor.row = min(s_row, len(buffer.lines) - 1)
        cursor.col = 0

    elif state.mode == "block":
        top, left, bot, right = r
        vim_motions.clipboard = []
        for row in range(top, bot + 1):
            line = buffer.lines[row]
            vim_motions.clipboard.append(line[left:right + 1])
            buffer.lines[row] = line[:left] + line[right + 1:]
        cursor.row = top
        cursor.col = left

    cursor._clamp_col(buffer)
    state.reset()
    return True

def visual_yank(buffer, cursor, state):
    import modes.vim_motions as vim_motions
    r = state.get_range(cursor)

    if state.mode == "char":
        s_row, s_col, e_row, e_col = r
        if s_row == e_row:
            vim_motions.clipboard = [buffer.lines[s_row][s_col:e_col + 1]]
        else:
            first = buffer.lines[s_row]
            last = buffer.lines[e_row]
            vim_motions.clipboard = (
                [first[s_col:]] +
                buffer.lines[s_row + 1:e_row] +
                [last[:e_col + 1]]
            )

    elif state.mode == "line":
        s_row, _, e_row, _ = r
        vim_motions.clipboard = list(buffer.lines[s_row:e_row + 1])

    elif state.mode == "block":
        top, left, bot, right = r
        vim_motions.clipboard = []
        for row in range(top, bot + 1):
            line = buffer.lines[row]
            vim_motions.clipboard.append(line[left:right + 1])

    s_row = r[0]
    s_col = r[1]
    cursor.row = s_row
    cursor.col = s_col
    state.reset()
    return False

def visual_change(buffer, cursor, window, state, tab=None):
    visual_delete(buffer, cursor, window, state, tab)
    return "insert"


def visual_indent(buffer, cursor, state, direction=1, tab=None):
    from config.keys import INDENT_STR
    save_snapshot(buffer, cursor, tab)
    r = state.get_range(cursor)

    if state.mode == "block":
        top, _, bot, _ = r
    else:
        top = r[0]
        bot = r[2]

    for row in range(top, bot + 1):
        line = buffer.lines[row]
        if direction > 0:
            buffer.lines[row] = INDENT_STR + line
        else:
            if line.startswith(INDENT_STR):
                buffer.lines[row] = line[len(INDENT_STR):]
            elif line.startswith("\t"):
                buffer.lines[row] = line[1:]
            else:
                stripped = line.lstrip(" ")
                removed = len(line) - len(stripped)
                if removed > 0:
                    buffer.lines[row] = line[min(removed, len(INDENT_STR)):]

    cursor._clamp_col(buffer)
    state.reset()
    return True


# Global visual state shared across modules
visual_state = VisualState()
