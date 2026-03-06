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
import tomllib

CONFIG_DIR = os.path.expanduser("~/.config/void")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.toml")


DEFAULTS = {
    "indent_width": 4,
    "max_undo": 100,
    "terminal_height": 10,
    "file_finder_width": 30,
    "subprocess_timeout": 30, # timer for when InlineTerminal is running 
    "show_indent_guides": True,
    "show_hud": True,
    "splash_animation": True,
    "scroll_margin": 5,
    "show_line_numbers": True,
    "tab_width": 4,
    "max_recent_files": 20,
    "max_recent_display": 8,
    "auto_indent": True,
    "auto_pair": True,
    "trailing_newline": True,
}

# Default template for config generate

DEFAULT_CONFIG_TOML = """\

# Void Config

# Indentation
indent_width = 4
tab_width = 4

# Editing behavior
auto_indent = true
auto_pair = true
trailing_newline = true

# UI Toggles
show_line_numbers = true
show_indent_guides = true
show_hud = true
splash_animation = true

# Panel Sizes
terminal_height = 10
file_finder_width = 30

# Limits
max_undo = 100
subprocess_timeout = 30 # How long before InlineTerminal times out running process
scroll_margin = 5

# Recent Files
max_recent_files = 20
max_recent_display = 8
"""

def load_config():
    config = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "rb") as f:
                user = tomllib.load(f)
            for key in DEFAULTS:
                if key in user:
                    config[key] = user[key]
        except (tomllib.TOMLDecodeError, OSError):
            pass
    return config


def create_default_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            f.write(DEFAULT_CONFIG_TOML)


settings = load_config()
