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

from config.settings import settings


#  NAMED CONSTANTS
#  Replaces magic strings 
# Control key codes
KEY_ESCAPE = "\x1b"
KEY_CTRL_D = "\x04"
KEY_CTRL_F = "\x06"
KEY_CTRL_R = "\x12"
KEY_CTRL_T = "\x14"
KEY_CTRL_U = "\x15"
KEY_CTRL_V = "\x16"
KEY_CTRL_N = "\x0e"
KEY_CTRL_P = "\x10"
KEY_ENTER = "\n"
KEY_BACKSPACE_CODES = ("KEY_BACKSPACE", "\x7f")
KEY_DELETE_CODES = ("KEY_DC", KEY_CTRL_D)

# Editor defaults loading from ~/.config/void/config.json
INDENT_WIDTH = settings["indent_width"]
INDENT_STR = " " * INDENT_WIDTH
MAX_UNDO = settings["max_undo"]
TERMINAL_HEIGHT = settings["terminal_height"]
FILE_FINDER_WIDTH = settings["file_finder_width"]
SUBPROCESS_TIMEOUT = settings["subprocess_timeout"]

# Placeholder filenames
NEW_FILE_NAME = "[new]"
