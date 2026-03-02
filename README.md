<p align="center">
  <pre align="center">
██╗   ██╗ ██████╗ ██╗██████╗ 
██║   ██║██╔═══██╗██║██╔══██╗
██║   ██║██║   ██║██║██║  ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝ 
  </pre>
  <em>A terminal text editor that refuses to pick a side.</em>
</p>

---


## What is Void?

Void is a terminal-native text editor built from scratch in Python with the curses library. Although inspired by Vim/Neovim, it does not aim to clone them. It shares a baseline with other terminal editors, that I believe is necessary for rich user experiences. After that baseline Void will fork it's own path, a path I am most excited to take and share with the world.

![Void Demo](assets/BLACKVOID.gif)
![Void Demo](assets/BlUEVOID.gif)

There is an uncomfortable gap in the editor landscape. On one end, you have Vim and Neovim — lightning fast, endlessly configurable, but quite minimal by design. On the other, you have VS Code and the full GUI editors — rich with features, visually intuitive, but with heavy and inefficient mouse-driven workflows, Void lives in the space between. Yes, a tool is a tool and people have their preferences, a drill or a hammer? Why not both? And make it beautiful, because who doesn't love an elegant tool?

The vision is an editor that inherits the speed, reliability, and keyboard-driven philosophy of traditional terminal editors while reaching toward the integrated, feature-rich experience that modern developers have come to expect from GUI editors. Vim motions are the foundation — not because Void is imitating Vim, but because that language of movement is simply the fastest way to navigate and manipulate text. Everything else built on top of the foundation of traditional GUI and terminal editors is where Void becomes its own thing. I want to push boundaries that we didn't even know could exist in the editor space.

Tabbed editing. An embedded terminal. A file finder panel. Visual selection. Syntax highlighting. Find and replace with confirmation workflows. Auto-pairing. Auto-indentation. Undo history. A floating HUD. All of it running inside your terminal, all of it driven by the keyboard, and all of it just the beginning.

## Current State

**Void is a work in progress.** It has rough edges, known bugs, and missing features. Things are going to break, behavior is going to change. This is an actively evolving project, not a polished release.

That said — it works. You can open files, edit them, save them, search through them, select and manipulate text visually, manage tabs, run shell commands, and navigate your filesystem without ever leaving the terminal or reaching for a mouse. The bones are solid, and the direction is clear.

## Features

- **Vim motions** — `h` `j` `k` `l`, `w` `b`, `gg` `G`, `d` + motion, `yy`, `p`, and more
- **Modal editing** — Normal, Insert, Visual, and Command modes
- **Visual mode** — Character (`v`), Line (`V`), and Block (`Ctrl+V`) selection with delete, yank, change, and indent operations
- **Tabbed buffers** — Open multiple files, switch between them with `gt`/`gT` or `:tabn`/`:tabp`
- **Integrated terminal** — Toggle an inline shell panel with `Ctrl+T`, run commands without leaving the editor
- **File finder** — Browse and open files from a side panel with `Ctrl+F`
- **Search and replace** — `/query` to search, `/find/replace/g` for bulk replace, `/find/replace/gc` for confirmation-based replace
- **Syntax highlighting** — Token-based highlighting for Python, C++, C, Rust and JavaScript (more languages to come)
- **Auto-indentation** — Smart indent that respects Python block structures
- **Auto-pairing** — Brackets, braces, parentheses, and quotes auto-close in Insert mode
- **Undo/Redo** — Full undo history with `u` and `Ctrl+R`
- **Bracket matching** — Highlights the matching bracket or quote under the cursor
- **Indent guides** — Vertical guides drawn through indentation levels, with active block highlighting
- **Cursor line highlighting** — Visual emphasis on the current line
- **Floating HUD** — Mode indicator, filetype, clock, and session timer in a top-right overlay
- **Horizontal scrolling** — Smooth margin-based scrolling for long lines
- **Splash screen** — Animated matrix rain startup with recent file access and keybind hints
- **Recent files** — Tracks and surfaces your recently opened files on launch

![Editor Screenshot](assets/VOID10.png)

![Editor Screenshot](assets/VOID6.png)

## Getting Started

### Requirements

- Python 3.x
- A terminal emulator with color support

### Usage

```bash
# Open Void with the splash screen
python void.py

# Open a specific file
python void.py myfile.py
```

## Keybinds

A full keybind reference is available in [`keybinds.md`](keybinds.md).

**Quick overview:**

```
NORMAL                          INSERT
h j k l .... move cursor        Esc ........ back to Normal
w b ........ word jump          Enter ...... new line (auto-indent)
0 $ ^ ...... line start/end     Backspace .. delete behind
gg / G ..... file top/bottom    ([{"' ...... auto-pair
Ctrl+D/U ... half-page scroll

i .......... enter Insert       VISUAL (v / V / Ctrl+V)
o / O ...... open line below/   h j k l .... extend selection
             above              d / x ...... delete selection
dd ......... delete line        y .......... yank selection
dw d$ d0 ... delete motion      c .......... change selection
yy ......... yank line          > / < ...... indent / dedent
p / P ...... paste after/before
u .......... undo               TERMINAL (Ctrl+T)
Ctrl+R ..... redo               Esc ........ back to editor
v .......... visual (char)      Enter ...... run command
V .......... visual (line)      Up/Down .... command history
Ctrl+V ..... visual (block)
/ .......... search             FILE FINDER (Ctrl+F)
n / N ...... next/prev match    j/k ........ navigate
gt / gT .... next/prev tab      Enter ...... open / navigate
                                h .......... toggle hidden

COMMAND MODE (:)
:w  :q  :wq  :q!  :e <file>  :tabnew <file>  :saveas <file>
```

## Project Structure

```
void.py          Entry point, main loop, screen drawing, event dispatch
buffer.py        Text buffer (line storage, insert, delete)
keybinds.py      Key dispatch, EditorState, command mode, tab/file helpers
vim_motions.py   Normal mode vim motions (hjkl, w, b, d, y, etc.)
visual.py        Visual mode state + operations (delete, yank, change, indent)
editing.py       Undo/redo system, auto-indent and snapshot management
display.py       Syntax highlighting, tokenizer, line drawing, safe_addstr
search.py        Search/Replace state + prompt
terminal.py      Inline terminal panel (subprocess, history, draw)
file_finder.py   File browser panel
tab.py           Tab + TabManager (per-tab buffer/cursor/undo)
splash.py        Animated splash screen and recent file tracking
aesthetics.py    Floating HUD widget (mode label, clock, time-elapsed and filetype)
keys.py          Named constants (keycodes, defaults, config values)
```

## The Road Ahead

Void is being built with big plans. The current Python/curses implementation is the proving ground — a place to explore ideas, nail down the interaction model, and figure out what a terminal editor can really be when it stops apologizing for not being a GUI.

The long-term vision includes rewriting performance critical parts in a systems language as the project grows. It will have broader language support, plugin architecture, and features that have traditionally been reserved for heavyweight editors, but also features you would not expect in any editor — all without sacrificing the speed and directness of working inside a terminal.

This is just the beginning.

---

<p align="center">
  <sub>Built from scratch. No dependencies. No compromises. Just the terminal.</sub>
</p>

## License

Void is licensed under the [Apache License v2.0](LICENSE).
