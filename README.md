# PsyLang

_Short for "Psychopath Language", because only a psychopath would use this._  
PsyLang is an esolang I made, inspired by BrainFuck. It runs in Python.

---

## Getting Started

Here's what you'll need to do to run it:

1. Install Python (if you don't already have it).  
   Download from [python.org](https://python.org/downloads).

2. Download `psylang.py` (the interpreter).

3. Make a text file.

4. Change the file extension from `.txt` to `.psy`. You can now add your PsyLang code to it.

5. Put both `psylang.py` and your `.psy` file in the **same folder** (or just keep both in your Downloads folder).

6. Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux), and change directory to that folder.  

7. Run your PsyLang program by typing:

   ```bash
   python psylang.py yourprogram.psy

---

## How PsyLang Works
# Subject to change in future updates, this only applies to the 1.0 version.
PsyLang uses a 16×16 grid, each cell holding a value.  
- If a cell’s value is **0**, the cell is **black**.  
- If greater than 0, the cell is **white**.  
- Negative values do **not** exist.  
- The top-left cell is selected by default.  
- You can use characters to change the selected cell's value or move the selected cell pointer.

---

## PsyLang Commands
# More commands to be added in future updates.
| Command    | Description                                                               |
|------------|---------------------------------------------------------------------------|
| `>`        | Move pointer **right** (wraps at grid edge)                              |
| `<`        | Move pointer **left** (wraps at grid edge)                               |
| `,`        | Move pointer **up** (wraps from top to bottom)                           |
| `.`        | Move pointer **down** (wraps from bottom to top)                         |
| `+`        | Increase current cell's value by 1                                       |
| `-`        | Decrease current cell's value by 1 (minimum 0)                           |
| `x[y]`     | Bind key `x` to run code block `y` when key pressed. <br>Example: `A[+]` increases current cell when `A` is pressed. |
| `showVal()`| Show numeric values on the grid cells                                    |

---

## Tips

- You can add spaces and line breaks in your `.psy` files to make your code easier to read — PsyLang will ignore them.
- Anything works as a comment due to how psylang.py is coded - if you have text that isn't part of the main commands, PsyLang ignores it.
 
---

***Good Luck.***
