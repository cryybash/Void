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
import subprocess
import os
import time
from keys import TERMINAL_HEIGHT, SUBPROCESS_TIMEOUT, KEY_ESCAPE
from display import safe_addstr

class InlineTerminal:
    def __init__(self, window):
        self.spin_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.spin_index = 0
        self.last_spin = time.time()
        self.visible = False
        self.output_lines = []
        self.input_buffer = ""
        self.history = []
        self.history_pos = -1
        self.height = TERMINAL_HEIGHT
        self.scroll_offset = 0
        self.cwd = os.getcwd()
        self._running_proc = None  # for non-blocking execution
        self._proc_start = 0

    def update_animation(self):
        now = time.time()
        if now - self.last_spin >= 0.1:
            self.spin_index = (self.spin_index + 1) % len(self.spin_chars)
            self.last_spin = now

    def toggle(self):
        self.visible = not self.visible

    def get_editor_rows(self, total_rows):
        if self.visible:
            return total_rows - self.height
        return total_rows

    def run_command(self, cmd):
        if not cmd.strip():
            return

        self.history.append(cmd)
        self.history_pos = -1

        # Handle cd specially
        if cmd.strip().startswith("cd "):
            path = cmd.strip()[3:].strip()
            try:
                new_dir = os.path.join(self.cwd, path)
                new_dir = os.path.abspath(new_dir)
                os.chdir(new_dir)
                self.cwd = new_dir
                self.output_lines.append(f"$ {cmd}")
                self.output_lines.append(f"  -> {self.cwd}")
            except FileNotFoundError:
                self.output_lines.append(f"$ {cmd}")
                self.output_lines.append(f"  cd: no such directory: {path}")
            self.input_buffer = ""
            self._scroll_to_bottom()
            return

        self.output_lines.append(f"$ {cmd}")

        # Launch non-blocking process
        try:
            self._running_proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd
            )
            self._proc_start = time.time()
        except Exception as e:
            self.output_lines.append(f"  [error: {str(e)}]")
            self._running_proc = None

        self.input_buffer = ""
    # Check if a running process has finished, call from main loop
    def poll_process(self):
        if self._running_proc is None:
            return

        retcode = self._running_proc.poll()

        # Check for timeout
        if retcode is None:
            if time.time() - self._proc_start > SUBPROCESS_TIMEOUT:
                self._running_proc.kill()
                self._running_proc.wait()
                self.output_lines.append(f"  [timed out after {SUBPROCESS_TIMEOUT}s]")
                self._running_proc = None
                self._scroll_to_bottom()
            return

        # Process finished
        stdout = self._running_proc.stdout.read()
        stderr = self._running_proc.stderr.read()

        if stdout:
            for line in stdout.rstrip("\n").split("\n"):
                self.output_lines.append(f"  {line}")
        if stderr:
            for line in stderr.rstrip("\n").split("\n"):
                self.output_lines.append(f"  {line}")
        if retcode != 0 and not stderr:
            self.output_lines.append(f"  [exit code: {retcode}]")

        self._running_proc = None
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        visible_rows = self.height - 2
        if len(self.output_lines) > visible_rows:
            self.scroll_offset = len(self.output_lines) - visible_rows
        else:
            self.scroll_offset = 0

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        visible_rows = self.height - 2
        max_offset = max(len(self.output_lines) - visible_rows, 0)
        if self.scroll_offset < max_offset:
            self.scroll_offset += 1

    def history_up(self):
        if self.history:
            if self.history_pos == -1:
                self.history_pos = len(self.history) - 1
            elif self.history_pos > 0:
                self.history_pos -= 1
            self.input_buffer = self.history[self.history_pos]

    def history_down(self):
        if self.history_pos != -1:
            if self.history_pos < len(self.history) - 1:
                self.history_pos += 1
                self.input_buffer = self.history[self.history_pos]
            else:
                self.history_pos = -1
                self.input_buffer = ""

    def handle_key(self, k):
        if k == KEY_ESCAPE:
            return "blur"
        elif k == "\n":
            self.run_command(self.input_buffer)
        elif k in ("KEY_BACKSPACE", "\x7f"):
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
        elif k == "KEY_UP":
            self.history_up()
        elif k == "KEY_DOWN":
            self.history_down()
        elif k == "\x0e":  # Ctrl+N
            self.scroll_down()
        elif k == "\x10":  # Ctrl+P
            self.scroll_up()
        elif len(k) == 1 and k.isprintable():
            self.input_buffer += k
        return None

    def draw(self, stdscr, start_row, n_cols):
        if not self.visible:
            return

        # Poll for finished process output
        self.poll_process()
        
        border = "_" * n_cols
        safe_addstr(stdscr, start_row, 0, border[:n_cols], curses.A_DIM)

        visible_rows = self.height - 2
        visible_output = self.output_lines[self.scroll_offset:self.scroll_offset + visible_rows]

        for i in range(visible_rows):
            row = start_row + 1 + i
            if row >= start_row + self.height - 1:
                break
            if i < len(visible_output):
                line = visible_output[i][:n_cols]
                safe_addstr(stdscr, row, 0, line, curses.A_DIM)
            else:
                safe_addstr(stdscr, row, 0, " " * n_cols)

        input_row = start_row + self.height - 1
        short_cwd = os.path.basename(self.cwd) or self.cwd

        # Show running indicator if process is active
        if self._running_proc is not None:
            prompt = f" {short_cwd} $ [running...]"
        else:
            prompt = f" {short_cwd} $ {self.input_buffer}"
        safe_addstr(stdscr, input_row, 0, prompt[:n_cols])

        self.update_animation()
        label = f"$VOID {self.spin_chars[self.spin_index]} "
        safe_addstr(stdscr, input_row, n_cols - len(label), label, curses.A_DIM)