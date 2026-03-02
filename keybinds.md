# Void — Keybind Reference

---

## Modes

Void operates in three primary modes, plus several focus contexts.

| Mode | Description |
|------|-------------|
| **Normal** | Default mode. Navigate, delete, yank, search, and issue commands. |
| **Insert** | Text entry mode. Characters are inserted at the cursor. |
| **Command** | Entered with `:` from Normal mode. Execute editor commands. |

Focus contexts (overlay onto the current mode):

| Context | Toggle | Description |
|---------|--------|-------------|
| **Terminal** | `Ctrl+T` | Embedded shell panel at the bottom of the editor. |
| **File Finder** | `Ctrl+F` | Side panel for browsing and opening files. |

---

## Splash Screen

These binds are active on the startup splash screen before any file is open.

| Key | Action |
|-----|--------|
| `1`–`9` | Open the corresponding recent file |
| `Enter` or `Space` | Open an empty buffer |
| `Escape` | Open an empty buffer |
| `q` | Quit Void |
| `Ctrl+F` | Open the file finder |
| `:` | Enter command mode |
| Any key (during animation) | Skip the matrix rain animation |

---

## Normal Mode

### Cursor Movement

| Key | Action |
|-----|--------|
| `h` | Move left one character |
| `l` | Move right one character |
| `j` | Move down one line |
| `k` | Move up one line |
| `w` | Jump to the start of the next word |
| `b` | Jump to the start of the previous word |
| `0` | Move to the start of the line |
| `$` | Move to the end of the line |
| `^` | Move to the first non-whitespace character of the line |
| `gg` | Jump to the first line of the file |
| `G` | Jump to the last line of the file |
| `Arrow Keys` | Move in the corresponding direction (also wraps across lines) |

### Scrolling

| Key | Action |
|-----|--------|
| `Ctrl+D` | Scroll down half a page (cursor moves with it) |
| `Ctrl+U` | Scroll up half a page (cursor moves with it) |

### Editing Actions

| Key | Action |
|-----|--------|
| `i` | Enter Insert mode at the cursor |
| `o` | Open a new line below the cursor and enter Insert mode |
| `O` | Open a new line above the cursor and enter Insert mode |
| `x` | Delete the character under the cursor |
| `p` | Paste clipboard after the current line |
| `P` | Paste clipboard before the current line |
| `u` | Undo the last change |
| `Ctrl+R` | Redo the last undone change |

### Delete with Motion (Operator: `d`)

| Key Sequence | Action |
|--------------|--------|
| `dd` | Delete the entire current line (yanked to clipboard) |
| `dw` | Delete from cursor to the start of the next word |
| `d$` | Delete from cursor to the end of the line |
| `d0` | Delete from cursor to the start of the line |
| `dG` | Delete from the current line to the end of the file |
| `dgg` | Delete from the current line to the top of the file |

### Yank (Copy)

| Key Sequence | Action |
|--------------|--------|
| `yy` | Yank (copy) the current line to the clipboard |

### Search and Replace

| Key | Action |
|-----|--------|
| `/` | Open the search prompt |
| `n` | Jump to the next search match |
| `N` | Jump to the previous search match |
| `Escape` | Clear search highlights and reset search state |

**Search prompt syntax:**

| Pattern | Action |
|---------|--------|
| `/query` | Find all occurrences of "query" |
| `/find/replace/g` | Replace all occurrences of "find" with "replace" |
| `/find/replace/gc` | Replace with confirmation — prompts at each match |

**Confirmation prompt keys** (when using `/find/replace/gc`):

| Key | Action |
|-----|--------|
| `y` | Replace this match and move to the next |
| `n` | Skip this match and move to the next |
| `a` | Replace all remaining matches at once |
| `q` | Quit the replace operation |

### Tab Navigation

| Key | Action |
|-----|--------|
| `gt` | Switch to the next tab |
| `gT` | Switch to the previous tab |

### Command Mode

| Key | Action |
|-----|--------|
| `:` | Enter command mode |

**Available commands:**

| Command | Action |
|---------|--------|
| `:w` | Save the current file |
| `:q` | Quit (fails if there are unsaved changes) |
| `:q!` | Force quit without saving |
| `:wq` | Save and quit |
| `:e <filepath>` | Open a file in a new tab (or switch to it if already open) |
| `:tabnew <filepath>` | Open a file in a new tab |
| `:tabn` / `:tabnext` | Switch to the next tab |
| `:tabp` / `:tabprev` | Switch to the previous tab |
| `:tabc` / `:tabclose` | Close the current tab |

**Inside the command/search prompt:**

| Key | Action |
|-----|--------|
| `Enter` | Execute the command / confirm the search |
| `Backspace` | Delete the last character (cancels if empty) |
| `Escape` | Cancel and return to Normal mode |

### Global Toggles

| Key | Action |
|-----|--------|
| `Ctrl+T` | Toggle the inline terminal (and focus it) |
| `Ctrl+F` | Toggle the file finder panel (and focus it) |

---

## Insert Mode

| Key | Action |
|-----|--------|
| `Escape` | Return to Normal mode |
| `Arrow Keys` | Move the cursor |
| `Enter` | Split the line at the cursor with auto-indentation |
| `Backspace` | Delete the character before the cursor (joins lines at col 0) |
| `Delete` / `Ctrl+D` | Delete the character under the cursor |
| `(`, `[`, `{`, `"`, `"` | Auto-insert the matching closing pair |
| Any printable key | Insert the character at the cursor |

**Auto-indentation behavior:**

- New lines inherit the indentation level of the line above.
- If the previous line ends with `:` (Python block), an extra 4-space indent is added.

---

## Terminal Panel

When the terminal panel is focused (toggled with `Ctrl+T`):

| Key | Action |
|-----|--------|
| `Escape` | Return focus to the editor |
| `Enter` | Execute the current command |
| `Backspace` | Delete the last character of the input |
| `Up Arrow` | Navigate to the previous command in history |
| `Down Arrow` | Navigate to the next command in history |
| `Ctrl+N` | Scroll terminal output down |
| `Ctrl+P` | Scroll terminal output up |
| Any printable key | Append to the command input |

**Built-in terminal behavior:**

- `cd <path>` is handled natively to change the working directory.
- All other commands run via the system shell with a 10-second timeout.

---

## File Finder Panel

When the file finder panel is focused (toggled with `Ctrl+F`):

| Key | Action |
|-----|--------|
| `Escape` | Return focus to the editor |
| `j` / `Down Arrow` | Move selection down |
| `k` / `Up Arrow` | Move selection up |
| `Enter` | Open the selected file in a new tab, or navigate into a directory |
| `h` | Toggle visibility of hidden files (dotfiles) |
| `r` | Refresh the file listing |

---

## Quick Reference Card

```
NORMAL                          INSERT
h j k l .... move cursor        Esc ........ back to Normal
w b ........ word jump          Enter ...... new line (auto-indent)
0 $ ^ ...... line start/end     Backspace .. delete behind
gg / G ..... file top/bottom    ([{"" ...... auto-pair
Ctrl+D/U ... half-page scroll
                                TERMINAL (Ctrl+T)
i .......... enter Insert       Esc ........ back to editor
o / O ...... open line below/   Enter ...... run command
             above              Up/Down .... command history
x .......... delete char        Ctrl+N/P ... scroll output
dd ......... delete line
dw d$ d0 ... delete motion      FILE FINDER (Ctrl+F)
dG / dgg ... delete to end/top  j/k ........ navigate
yy ......... yank line          Enter ...... open / navigate
p / P ...... paste after/before h .......... toggle hidden
u .......... undo               r .......... refresh
Ctrl+R ..... redo
/ .......... search             COMMAND MODE (:)
n / N ...... next/prev match    :w  :q  :wq  :q!
gt / gT .... next/prev tab      :e  :tabnew  :tabn  :tabp
```
