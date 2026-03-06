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
import subprocess
import os
import time
from config.keys import TERMINAL_HEIGHT, SUBPROCESS_TIMEOUT, KEY_ESCAPE
from ui.display import safe_addstr

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
        self._running_proc = None
        self._proc_start = 0
        self._awaiting_input = False

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

        # Launch process with stdin pipe for interactive input
        try:
            self._running_proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd
            )
            self._proc_start = time.time()
            
            # Make stdout non-blocking so poll_process doesn't freeze
            import fcntl
            flags = fcntl.fcntl(self._running_proc.stdout, fcntl.F_GETFL)
            fcntl.fcntl(self._running_proc.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            self._awaiting_input = False
        except Exception as e:
            self.output_lines.append(f"  [error: {str(e)}]")
            self._running_proc = None

        self.input_buffer = ""

    def poll_process(self):
        if self._running_proc is None:
            return

        # Read any available stdout without blocking
        if self._running_proc.stdout:
            try:
                data = self._running_proc.stdout.read()
                if data:
                    for line in data.rstrip("\n").split("\n"):
                        self.output_lines.append(f"  {line}")
                    self._scroll_to_bottom()
            except (BlockingIOError, IOError):
                pass


        retcode = self._running_proc.poll()

        # Still running — check if it's waiting for input
        if retcode is None:
            if time.time() - self._proc_start > SUBPROCESS_TIMEOUT:
                self._running_proc.kill()
                self._running_proc.wait()
                self.output_lines.append(f"  [timed out after {SUBPROCESS_TIMEOUT}s]")
                self._running_proc = None
                self._awaiting_input = False
                self._scroll_to_bottom()
                return

            # Check if process is blocked (no stdout ready, still alive)
            self._awaiting_input = True
            return

        # Process finished — read any remaining output
        remaining_out = self._running_proc.stdout.read()
        remaining_err = self._running_proc.stderr.read()

        if remaining_out:
            for line in remaining_out.rstrip("\n").split("\n"):
                self.output_lines.append(f"  {line}")
        if remaining_err:
            for line in remaining_err.rstrip("\n").split("\n"):
                self.output_lines.append(f"  {line}")
        if retcode != 0 and not remaining_err:
            self.output_lines.append(f"  [exit code: {retcode}]")

        self._running_proc = None
        self._awaiting_input = False
        self._scroll_to_bottom()
    
    # user input to process's stdin
    def send_input(self, text):
        if self._running_proc and self._running_proc.stdin:
            try:
                self._running_proc.stdin.write(text + "\n")
                self._running_proc.stdin.flush()
               # self.output_lines.append(f"  {text}")
                self._awaiting_input = False
                self._scroll_to_bottom()
            except (BrokenPipeError, OSError):
                self.output_lines.append("  [process closed]")
                self._running_proc = None
                self._awaiting_input = False

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
            if self._awaiting_input and self._running_proc:
                self.send_input(self.input_buffer)
                self.input_buffer = ""
            else:
                self.run_command(self.input_buffer)
        elif k in ("KEY_BACKSPACE", "\x7f"):
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
        elif k == "KEY_UP":
            if not self._awaiting_input:
                self.history_up()
        elif k == "KEY_DOWN":
            if not self._awaiting_input:
                self.history_down()
        elif k == "\x0e":  # Ctrl+N
            self.scroll_down()
        elif k == "\x10":  # Ctrl+P
            self.scroll_up()
        elif k == "\x03":  # Ctrl+C
            if self._running_proc:
                self._running_proc.kill()
                self._running_proc.wait()
                self.output_lines.append("  [killed]")
                self._running_proc = None
                self._awaiting_input = False
                self.input_buffer = ""
                self._scroll_to_bottom()
        elif len(k) == 1 and k.isprintable():
            self.input_buffer += k
        return None

    def draw(self, stdscr, start_row, n_cols):
        if not self.visible:
            return

        # Poll for output from running process
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

        if self._running_proc is not None:
            if self._awaiting_input:
                prompt = f" >> {self.input_buffer}"
            else:
                prompt = f" {short_cwd} $ [running...]"
        else:
            prompt = f" {short_cwd} $ {self.input_buffer}"
        safe_addstr(stdscr, input_row, 0, prompt[:n_cols])

        self.update_animation()
        label = f"$VOID {self.spin_chars[self.spin_index]} "
        safe_addstr(stdscr, input_row, n_cols - len(label), label, curses.A_DIM)
