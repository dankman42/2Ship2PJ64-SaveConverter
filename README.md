# 2Ship2PJ64 Save Converter

Move your **Majora's Mask** save from [2Ship2Harkinian](https://github.com/HarbourMasters/2ship2harkinian) into **Project64** (or another N64 emulator) and carry on playing.

2Ship stores saves as JSON (`saves/file1.json`). Project64 uses the 128 KB FlashRAM image the original cartridge wrote. This tool rebuilds that image from your 2Ship save, including your owl statue save and pictograph photo.

## Download

Get `2ship-to-pj64.exe` from the [latest release](../../releases/latest). Nothing needs installing.

Windows SmartScreen may say "Windows protected your PC" because the exe isn't signed. Click **More info**, then **Run anyway**. If you'd rather not run an exe, use the Python script instead (see [Command line](#command-line)).

## How to use it

1. **Close Project64.** While a game is running it keeps its own copy of the save and can write it back over yours.
2. **Open the converter and choose your save.** Double-click the exe and browse to `file1.json` or `file2.json` in 2Ship's `saves` folder, or drag the save onto the exe. It shows the player name, hearts, masks and whether there's an owl save.
3. **Choose where to save it.** To import directly, pick the `ZELDA MAJORA'S MASK.fla` in Project64's save folder (**Options → Settings → Directories → Native saves**, in the `ZELDA MAJORA'S MASK-…` subfolder). Or save a new file anywhere.
4. **Choose slot 1 or slot 2.** If the file already exists, only the slot you pick changes and the other one is kept. The converter asks before replacing a save and makes a dated `.bak` backup first.
5. **Click Convert save** and start the game.

A full illustrated walkthrough is in [`2ship-to-pj64-guide.html`](2ship-to-pj64-guide.html).

## Requirements

- **US (NTSC-U)** Majora's Mask ROM. The Japanese and European versions arrange their saves differently.
- 2Ship2Harkinian save format version 7 (the `"version"` field at the end of the JSON).

## What carries over

| Data | Converted |
| --- | --- |
| Items, masks, songs, heart pieces, upgrades, Bombers' Notebook, scene flags, owl statues, high scores | Yes |
| Owl save, including day, time, pictograph photo and bottle timers | Yes |
| Song of Time save | Yes |
| D-pad item assignments, playtime, creation date (2Ship-only) | No |

The checksums the converter prints won't match the ones in the JSON. That's expected: 2Ship's checksum also covers its own extra fields. The converter writes the checksum the original game checks.

## Command line

```
python convert.py <file1.json> [<output.fla>] [--file 1|2]
```

Writes `ZELDA MAJORA'S MASK.fla` (Project64 byte order) and `ZELDA MAJORA'S MASK.bigendian.fla` (cartridge byte order, for mupen64plus, Ares and similar). Only the Python standard library is needed.

To run the window from source: `python gui.py`.

## Building the exe

Install Python 3 and PyInstaller (`pip install pyinstaller`), then run `build.bat`. It regenerates the icon with `make_icon.py` and writes `2ship-to-pj64.exe`.

## How it works

The save layout comes from the [zeldaret/mm](https://github.com/zeldaret/mm) decompilation (`include/z64save.h`, `src/code/z_sram_NES.c`):

| Offset | Contents |
| --- | --- |
| `0x00000` / `0x02000` | Slot 1 Song of Time save + backup (`Save`, 0x100C bytes) |
| `0x04000` / `0x06000` | Slot 2 Song of Time save + backup |
| `0x08000` / `0x0C000` | Slot 1 owl save + backup (`SaveContext` up to `fileNum`, 0x3CA0 bytes) |
| `0x10000` / `0x14000` | Slot 2 owl save + backup |
| `0x18000` / `0x1C000` | Options header (`0xA51D`) + backup |

Each save's checksum is a 16-bit sum of all its bytes, computed with the checksum field zeroed. Project64 stores FlashRAM with every 4-byte word reversed, so the tool swaps byte order when writing for Project64.

## Disclaimer

Not affiliated with Nintendo, the 2Ship2Harkinian team or the Project64 team. The Legend of Zelda: Majora's Mask is a trademark of Nintendo. This tool contains no game code or assets; all artwork is drawn in code.
