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

# UNDO/REDO logic
from config.keys import MAX_UNDO, INDENT_STR

# Save current buffer state
def save_snapshot(buffer, cursor, tab=None):
    if tab is None:
        return
    snapshot = {
        "lines": list(buffer.lines),
        "row": cursor.row,
        "col": cursor.col
    }
    tab.undo_stack.append(snapshot)
    if len(tab.undo_stack) > MAX_UNDO:
        tab.undo_stack.pop(0)
    
    # Any new edit clears redo history
    tab.redo_stack = []

# Restore previous buffer state
def undo(buffer, cursor, window, tab=None):
    if tab is None or not tab.undo_stack:
        return False
    
    tab.redo_stack.append({
        "lines": list(buffer.lines),
        "row": cursor.row,
        "col": cursor.col
    })
    snapshot = tab.undo_stack.pop()
    buffer.lines = snapshot["lines"]
    cursor.row = snapshot["row"]
    cursor.col = snapshot["col"]
    cursor._clamp_col(buffer)
    
    if cursor.row < window.row:
        window.row = cursor.row
    elif cursor.row > window.row + window.n_rows - 1:
        window.row = cursor.row - window.n_rows + 1
    return True

# Restoring next buffer state after undo    
def redo(buffer, cursor, window, tab=None):
    if tab is None or not tab.redo_stack:
        return False
    
    tab.undo_stack.append({
        "lines": list(buffer.lines),
        "row": cursor.row,
        "col": cursor.col
    })
    snapshot = tab.redo_stack.pop()
    buffer.lines = snapshot["lines"]
    cursor.row = snapshot["row"]
    cursor.col = snapshot["col"]
    cursor._clamp_col(buffer)
    if cursor.row < window.row:
        window.row = cursor.row
    elif cursor.row > window.row + window.n_rows - 1:
        window.row = cursor.row - window.n_rows + 1
    return True


def get_indentation(line):
    return line[:len(line) - len(line.lstrip())]


def get_indent_level(line):
    indent = get_indentation(line)
    stripped = line.rstrip()
    if stripped.endswith(":"):
        indent += INDENT_STR
    return indent

def auto_indent(buffer, cursor, window):
    current_line = buffer[cursor.row]
    if cursor.col == 0:
        # At start of line — just insert a blank line above, no indent
        buffer.lines.insert(cursor.row, "")
        cursor.row += 1
        window.down(buffer, cursor)
        return
    indent = get_indent_level(current_line[:cursor.col])
    buffer.split(cursor)
    cursor.row += 1
    cursor.col = 0
    window.down(buffer, cursor)
    if indent:
        buffer.insert(cursor, indent)
        cursor.col = len(indent)
