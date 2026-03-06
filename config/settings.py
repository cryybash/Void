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
import json

CONFIG_DIR = os.path.expanduser("~/.config/void")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


DEFAULTS = {
    "indent_width": 4,
    "max_undo": 100,
    "terminal_height": 10,
    "file_finder_width": 30,
    "subprocess_timeout": 30, # timer for when InlineTerminal is running 
    "show_indent_guides": True,
    "show_hud": True,
    "splash_animation": True,
}


def load_config():
    config = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                user = json.load(f)
            for key in DEFAULTS:
                if key in user:
                    config[key] = user[key]
        except (json.JSONDecodeError, OSError):
            pass
    return config


def create_default_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULTS, f, indent=4)


settings = load_config()
