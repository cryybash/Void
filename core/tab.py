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

import os
from config.keys import NEW_FILE_NAME

# Each tab holds its own buffer, cursor state, file, and editor state
class Tab:
    def __init__(self, filename, buffer, cursor_row=0, cursor_col=0):
        self.filename = filename
        self.buffer = buffer
        self.cursor_row = cursor_row
        self.cursor_col = cursor_col
        self.modified = False
        self.window_row = 0  # scroll position
        self.window_col = 0
        self.undo_stack = []
        self.redo_stack = []

    @property
    def display_name(self):
        name = os.path.basename(self.filename) if self.filename else NEW_FILE_NAME
        if self.modified:
            name = "● " + name
        return name
    
    # Store cursor and window position      
    def save_cursor(self, cursor, window):
        self.cursor_row = cursor.row
        self.cursor_col = cursor.col
        self.window_row = window.row
        self.window_col = window.col
    
    # Restore cursor and window position
    def restore_cursor(self, cursor, window):
        cursor.row = self.cursor_row
        cursor.col = self.cursor_col
        cursor._col_hint = self.cursor_col
        window.row = self.window_row
        window.col = self.window_col

class TabManager:
    def __init__(self):
        self.tabs = []
        self.active_index = 0

    @property
    def active_tab(self):
        if self.tabs:
            return self.tabs[self.active_index]
        return None
    
    def add_tab(self, tab):
        self.tabs.append(tab)
        self.active_index = len(self.tabs) - 1
    
    def close_tab(self, index=None):
        if index is None:
            index = self.active_index

        if len(self.tabs) <= 1:
            return False

        self.tabs.pop(index)
        if self.active_index >= len(self.tabs):
            self.active_index = len(self.tabs) - 1
        return True
    
    def next_tab(self):
        if len(self.tabs) > 1:
            self.active_index = (self.active_index + 1) % len(self.tabs)
    
    def prev_tab(self):
        if len(self.tabs) > 1:
            self.active_index = (self.active_index - 1) % len(self.tabs)
    
    def go_to_tab(self, index):
        if 0 <= index < len(self.tabs):
            self.active_index = index
    
    def find_tab(self, filename):
        for i, tab in enumerate(self.tabs):
            if tab.filename == filename:
                return i
        return -1
