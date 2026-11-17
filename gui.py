"""2Ship to Project64: a window for converting 2Ship2Harkinian Majora's Mask saves.

Run with `python gui.py [save.json]`, or build the exe with PyInstaller (see build.bat).
All artwork is drawn in code; no game assets are included.
"""
import os
import random
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import convert as core

C = {
    'bg': '#150c22', 'panel': '#1f1331', 'field': '#2a1b42', 'line': '#3e2b5e',
    'fg': '#f1eaff', 'muted': '#a796c6', 'gold': '#e9c46a', 'gold_hi': '#f7dd98', 'ink': '#1a0f29',
    'sky_top': '#07040f', 'sky_mid': '#1d0f33', 'sky_bot': '#4a2160',
    'moon': '#e09447', 'moon_lit': '#f2b465', 'moon_dk': '#b0632c', 'halo': '#5a2a55',
    'silhouette': '#0d0716', 'ok': '#86e0ae', 'err': '#ff9a9a', 'warn': '#f3bd63',
}
TITLE_FONT = 'Georgia'
BODY_FONT = 'Segoe UI'


def resource(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw_header(cv, w, h, s):
    """Night sky over a clock town, with the moon hanging far too low."""
    for y in range(h):  # sky gradient
        t = y / h
        col = mix(C['sky_top'], C['sky_mid'], t / 0.55) if t < 0.55 else mix(C['sky_mid'], C['sky_bot'], (t - 0.55) / 0.45)
        cv.create_line(0, y, w, y, fill=col)

    rnd = random.Random(72)  # stars
    for _ in range(int(90 * s)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.75)
        r = rnd.choice((0.6, 0.8, 1.0, 1.4)) * s
        cv.create_oval(x - r, y - r, x + r, y + r, fill=mix(C['sky_mid'], '#ffffff', rnd.uniform(0.45, 1)), width=0)

    mx, my, mr = w * 0.80, h * 0.36, h * 0.58  # the moon, with a halo
    for i in range(14, 0, -1):
        rr = mr + i * 5 * s
        cv.create_oval(mx - rr, my - rr, mx + rr, my + rr, fill=mix(C['sky_mid'], C['halo'], (15 - i) / 15 * 0.8), width=0)
    for i in range(12):
        rr = mr * (1 - i * 0.035)
        ox, oy = -i * 1.6 * s, -i * 1.6 * s
        cv.create_oval(mx - rr + ox, my - rr + oy, mx + rr + ox, my + rr + oy,
                       fill=mix(C['moon_dk'], C['moon_lit'], i / 11), width=0)
    for cx, cy, cr in ((-0.35, -0.25, 0.16), (0.22, -0.42, 0.10), (0.30, 0.18, 0.20), (-0.15, 0.42, 0.12), (-0.55, 0.20, 0.08)):
        x, y, r = mx + cx * mr, my + cy * mr, cr * mr
        cv.create_oval(x - r, y - r, x + r, y + r, fill=mix(C['moon_dk'], C['moon'], 0.35), outline=mix(C['moon_dk'], C['moon_lit'], 0.2), width=max(1, int(s)))

    base = h - 18 * s  # rooftops
    roofs = [(0, base)]
    x = 0
    rnd = random.Random(3)
    while x < w:
        bw = rnd.uniform(36, 70) * s
        bh = rnd.uniform(14, 34) * s
        roofs += [(x, base - bh * 0.6), (x + bw / 2, base - bh), (x + bw, base - bh * 0.6)]
        x += bw
    roofs += [(w, base), (w, h), (0, h)]
    cv.create_polygon([c for p in roofs for c in p], fill=C['silhouette'], outline='')

    tx, tw = 58 * s, 46 * s  # clock tower
    top = 34 * s
    cv.create_rectangle(tx - tw / 2, top + 40 * s, tx + tw / 2, h, fill=C['silhouette'], width=0)
    cv.create_polygon(tx - tw / 2 - 6 * s, top + 42 * s, tx, top, tx + tw / 2 + 6 * s, top + 42 * s, fill=C['silhouette'], outline='')
    cx, cy, cr = tx, top + 72 * s, 17 * s
    cv.create_oval(cx - cr - 3 * s, cy - cr - 3 * s, cx + cr + 3 * s, cy + cr + 3 * s, fill=C['silhouette'], outline=C['gold'], width=max(1, int(1.5 * s)))
    cv.create_oval(cx - cr, cy - cr, cx + cr, cy + cr, fill='#2a1a12', outline='')
    import math
    for i in range(12):
        a = math.radians(i * 30)
        r1, r2 = cr * 0.78, cr * (0.95 if i % 3 else 0.62)
        cv.create_line(cx + r1 * math.sin(a), cy - r1 * math.cos(a), cx + r2 * math.sin(a), cy - r2 * math.cos(a),
                       fill=C['gold'], width=max(1, int(s)))
    cv.create_line(cx, cy, cx + cr * 0.5 * math.sin(math.radians(350)), cy - cr * 0.5 * math.cos(math.radians(350)), fill=C['gold_hi'], width=max(2, int(2 * s)))
    cv.create_line(cx, cy, cx + cr * 0.8 * math.sin(math.radians(180)), cy - cr * 0.8 * math.cos(math.radians(180)), fill=C['gold_hi'], width=max(1, int(1.4 * s)))
    cv.create_rectangle(tx - 5 * s, h - 34 * s, tx + 5 * s, h - 18 * s, fill=C['gold'], width=0)  # lit doorway

    lx = 112 * s  # title
    cv.create_text(lx + 2 * s, 66 * s + 2 * s, text='2Ship  →  Project64', anchor='w', fill='#000000', font=(TITLE_FONT, 25, 'bold'))
    cv.create_text(lx, 66 * s, text='2Ship  →  Project64', anchor='w', fill=C['gold'], font=(TITLE_FONT, 25, 'bold'))
    cv.create_text(lx + 2, 104 * s, text="Majora's Mask save converter", anchor='w', fill=C['fg'], font=(TITLE_FONT, 12, 'italic'))
    cv.create_text(lx + 2, 128 * s, text='DAWN OF A NEW DAY  ·  72 HOURS REMAIN', anchor='w', fill=C['muted'], font=(BODY_FONT, 8, 'bold'))


class App:
    def __init__(self, root, initial=None):
        self.root = root
        self.save = None
        self.out_native = None
        self.s = max(1.0, root.winfo_fpixels('1i') / 96)
        root.title('2Ship to Project64')
        root.configure(bg=C['bg'])
        root.resizable(False, False)
        try:
            self.icon = tk.PhotoImage(file=resource('moon.png'))
            root.iconphoto(True, self.icon)
        except Exception:
            pass

        w, h = int(640 * self.s), int(176 * self.s)
        cv = tk.Canvas(root, width=w, height=h, highlightthickness=0, bd=0, bg=C['sky_top'])
        cv.pack(fill='x')
        draw_header(cv, w, h, self.s)

        body = tk.Frame(root, bg=C['bg'], padx=int(24 * self.s), pady=int(16 * self.s))
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=1)

        self.in_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.slot_var = tk.IntVar(value=1)
        self.fmt_var = tk.StringVar(value='project64')
        self.merge_var = tk.BooleanVar(value=True)
        self.backup_var = tk.BooleanVar(value=True)

        r = 0
        r = self.heading(body, r, '1', 'Choose your 2Ship save')
        r = self.path_row(body, r, self.in_var, self.browse_in, 'in_entry')
        self.in_info = self.info_label(body, r, 'Usually saves\\file1.json in your 2Ship2Harkinian folder.'); r += 1

        r = self.heading(body, r, '2', 'Choose where to save it')
        r = self.path_row(body, r, self.out_var, self.browse_out, 'out_entry')
        self.out_info = self.info_label(body, r, "To import directly, pick the .fla in Project64's save folder (Options → Settings → Directories)."); r += 1
        fmt = tk.Frame(body, bg=C['bg']); fmt.grid(row=r, column=0, sticky='w', pady=(2, 0)); r += 1
        for val, label in (('project64', 'Project64 format'), ('big-endian', 'Other emulators (cartridge byte order)')):
            self.radio(fmt, label, self.fmt_var, val, self.refresh_output).pack(side='left', padx=(0, 18))

        r = self.heading(body, r, '3', 'Choose a file slot')
        slots = tk.Frame(body, bg=C['bg']); slots.grid(row=r, column=0, sticky='ew'); r += 1
        slots.columnconfigure((0, 1), weight=1, uniform='slot')
        self.slot_buttons = {}
        for i in (1, 2):
            b = tk.Radiobutton(slots, variable=self.slot_var, value=i, indicatoron=0, command=self.paint_slots,
                               font=(BODY_FONT, 10), justify='left', anchor='w', relief='flat', bd=0,
                               padx=int(14 * self.s), pady=int(9 * self.s), cursor='hand2',
                               highlightthickness=1, highlightbackground=C['line'])
            b.grid(row=0, column=i - 1, sticky='ew', padx=(0 if i == 1 else 6, 6 if i == 1 else 0))
            self.slot_buttons[i] = b
        opts = tk.Frame(body, bg=C['bg']); opts.grid(row=r, column=0, sticky='w', pady=(8, 0)); r += 1
        self.merge_cb = self.check(opts, 'Keep the other slot from the existing file', self.merge_var)
        self.merge_cb.pack(anchor='w')
        self.backup_cb = self.check(opts, 'Back up the existing file first', self.backup_var)
        self.backup_cb.pack(anchor='w')

        act = tk.Frame(body, bg=C['bg']); act.grid(row=r, column=0, sticky='ew', pady=(int(16 * self.s), 0)); r += 1
        act.columnconfigure(1, weight=1)
        self.go = tk.Button(act, text='Convert save', command=self.convert, font=(TITLE_FONT, 12, 'bold'),
                            bg=C['gold'], fg=C['ink'], activebackground=C['gold_hi'], activeforeground=C['ink'],
                            disabledforeground=mix(C['ink'], C['gold'], 0.55), relief='flat', bd=0,
                            padx=int(22 * self.s), pady=int(8 * self.s), cursor='hand2')
        self.go.grid(row=0, column=0, sticky='w')
        self.open_btn = self.button(act, 'Open folder', self.open_folder)
        self.open_btn.grid(row=0, column=2, sticky='e')
        self.open_btn.grid_remove()
        self.status = tk.Label(body, text='', bg=C['bg'], fg=C['muted'], font=(BODY_FONT, 9), justify='left', anchor='w',
                               wraplength=int(590 * self.s))
        self.status.grid(row=r, column=0, sticky='ew', pady=(10, 0)); r += 1

        self.in_var.trace_add('write', lambda *_: self.schedule(self.refresh_input))
        self.out_var.trace_add('write', lambda *_: self.schedule(self.refresh_output))
        self.refresh_input()
        self.refresh_output()
        if initial:
            self.set_input(initial)

    # ---- widget helpers ----
    def heading(self, parent, row, num, text):
        f = tk.Frame(parent, bg=C['bg'])
        f.grid(row=row, column=0, sticky='w', pady=(int(14 * self.s) if row else 0, int(6 * self.s)))
        tk.Label(f, text=num, bg=C['gold'], fg=C['ink'], font=(TITLE_FONT, 10, 'bold'), width=2).pack(side='left')
        tk.Label(f, text=text, bg=C['bg'], fg=C['fg'], font=(TITLE_FONT, 12, 'bold')).pack(side='left', padx=(10, 0))
        return row + 1

    def path_row(self, parent, row, var, browse, attr):
        f = tk.Frame(parent, bg=C['bg']); f.grid(row=row, column=0, sticky='ew'); f.columnconfigure(0, weight=1)
        e = tk.Entry(f, textvariable=var, bg=C['field'], fg=C['fg'], insertbackground=C['fg'], relief='flat',
                     font=(BODY_FONT, 10), highlightthickness=1, highlightbackground=C['line'], highlightcolor=C['gold'])
        e.grid(row=0, column=0, sticky='ew', ipady=int(5 * self.s))
        self.button(f, 'Browse…', browse).grid(row=0, column=1, padx=(8, 0))
        setattr(self, attr, e)
        return row + 1

    def info_label(self, parent, row, text):
        l = tk.Label(parent, text=text, bg=C['bg'], fg=C['muted'], font=(BODY_FONT, 9), anchor='w', justify='left',
                     wraplength=int(590 * self.s))
        l.grid(row=row, column=0, sticky='ew', pady=(4, 0))
        return l

    def button(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=C['field'], fg=C['fg'], activebackground=C['line'],
                         activeforeground=C['fg'], relief='flat', bd=0, font=(BODY_FONT, 10),
                         padx=int(12 * self.s), pady=int(4 * self.s), cursor='hand2')

    def radio(self, parent, text, var, val, cmd):
        return tk.Radiobutton(parent, text=text, variable=var, value=val, command=cmd, bg=C['bg'], fg=C['fg'],
                              selectcolor=C['field'], activebackground=C['bg'], activeforeground=C['gold_hi'],
                              font=(BODY_FONT, 9), bd=0, highlightthickness=0, cursor='hand2')

    def check(self, parent, text, var):
        return tk.Checkbutton(parent, text=text, variable=var, bg=C['bg'], fg=C['fg'], selectcolor=C['field'],
                              activebackground=C['bg'], activeforeground=C['gold_hi'], font=(BODY_FONT, 9),
                              disabledforeground=mix(C['muted'], C['bg'], 0.45), bd=0, highlightthickness=0, cursor='hand2')

    def schedule(self, fn):
        key = fn.__name__
        if getattr(self, '_job_' + key, None):
            self.root.after_cancel(getattr(self, '_job_' + key))
        setattr(self, '_job_' + key, self.root.after(250, fn))

    def say(self, text, kind='muted'):
        self.status.config(text=text, fg=C[kind])

    # ---- input ----
    def browse_in(self):
        start = os.path.dirname(self.in_var.get()) if self.in_var.get() else None
        p = filedialog.askopenfilename(title='Choose your 2Ship save', initialdir=start,
                                       filetypes=[('2Ship save', '*.json'), ('All files', '*.*')])
        if p:
            self.set_input(p)

    def set_input(self, p):
        p = os.path.normpath(p)
        self.in_var.set(p)
        self.slot_var.set(core.slot_from_filename(p))
        if not self.out_var.get():
            self.set_output(os.path.join(os.path.dirname(p), core.OUT_NAME))
        self.in_entry.xview_moveto(1)
        self.refresh_input()

    def set_output(self, p):
        self.out_var.set(os.path.normpath(p))
        self.out_entry.xview_moveto(1)

    def refresh_input(self):
        p = self.in_var.get().strip().strip('"')
        self.save = None
        if not p:
            self.in_info.config(text='Usually saves\\file1.json in your 2Ship2Harkinian folder.', fg=C['muted'])
        elif not os.path.isfile(p):
            self.in_info.config(text="That file doesn't exist.", fg=C['err'])
        else:
            try:
                self.save = core.load_save(p)
                i = core.describe_json(self.save)
                hearts = f"{i['hearts']:g} heart{'s' if i['hearts'] != 1 else ''}"
                bits = [i['name'], hearts, f"{i['masks']} mask{'s' if i['masks'] != 1 else ''}", f"{i['rupees']} rupees"]
                text = '  ·  '.join(bits)
                text += f"\nOwl save on Day {i['owl_day']}, {i['owl_time']} is included." if i['owl'] else '\nNo owl save. You\'ll start from your last Song of Time save.'
                self.in_info.config(text=text, fg=C['ok'])
            except Exception:
                self.in_info.config(text="This isn't a 2Ship Majora's Mask save. Choose saves\\file1.json or file2.json.", fg=C['err'])
        self.paint_slots()

    # ---- output ----
    def browse_out(self):
        cur = self.out_var.get()
        p = filedialog.asksaveasfilename(title='Save as (pick an existing .fla to import into it)',
                                         initialdir=os.path.dirname(cur) if cur else None,
                                         initialfile=os.path.basename(cur) if cur else core.OUT_NAME,
                                         defaultextension='.fla', confirmoverwrite=False,
                                         filetypes=[('N64 FlashRAM save', '*.fla'), ('All files', '*.*')])
        if p:
            self.set_output(p)

    def refresh_output(self):
        p = self.out_var.get().strip().strip('"')
        self.out_native = None
        exists = bool(p) and os.path.isfile(p)
        if exists:
            try:
                with open(p, 'rb') as f:
                    self.out_native, fmt = core.to_native(f.read(), assume_pj64=self.fmt_var.get() == 'project64')
                if fmt != self.fmt_var.get():
                    self.fmt_var.set(fmt)
                self.out_info.config(text='This file already exists. Your save goes into the slot you choose below.', fg=C['warn'])
            except OSError as e:
                self.out_info.config(text=f"Can't read this file: {e.strerror}. It may be a OneDrive file that hasn't downloaded.", fg=C['err'])
        elif p:
            d = os.path.dirname(p)
            ok = not d or os.path.isdir(d)
            self.out_info.config(text='A new save file will be created.' if ok else "That folder doesn't exist.",
                                 fg=C['muted'] if ok else C['err'])
        else:
            self.out_info.config(text="To import directly, pick the .fla in Project64's save folder (Options → Settings → Directories).", fg=C['muted'])
        state = 'normal' if self.out_native is not None else 'disabled'
        self.merge_cb.config(state=state)
        self.backup_cb.config(state=state)
        self.paint_slots()

    def paint_slots(self):
        held = core.describe_flash(self.out_native) if self.out_native is not None else {1: 'empty', 2: 'empty'}
        name = core.describe_json(self.save)['name'] if self.save else None
        for i, b in self.slot_buttons.items():
            sel = self.slot_var.get() == i
            now = held[i]
            if sel and name:
                line2 = f'{name} goes here' + ('' if now == 'empty' else f', replacing {now}')
            else:
                line2 = 'Empty' if now == 'empty' else f'Has: {now}'
            b.config(text=f'Slot {i}\n{line2}',
                     bg=C['gold'] if sel else C['field'], fg=C['ink'] if sel else C['fg'],
                     selectcolor=C['gold'], activebackground=C['gold_hi'] if sel else C['line'],
                     activeforeground=C['ink'] if sel else C['fg'])
        self.update_go()

    def update_go(self):
        p = self.out_var.get().strip()
        d = os.path.dirname(p)
        ready = self.save is not None and p and (not d or os.path.isdir(d))
        self.go.config(state='normal' if ready else 'disabled')

    # ---- convert ----
    def convert(self):
        src = self.in_var.get().strip().strip('"')
        dst = self.out_var.get().strip().strip('"')
        slot = self.slot_var.get()
        self.refresh_output()
        if self.out_native is not None:
            held = core.describe_flash(self.out_native)[slot]
            if held != 'empty' and not messagebox.askyesno(
                    'Replace this save?', f'Slot {slot} in this file holds "{held}".\n\nReplace it with your 2Ship save?',
                    icon='warning', parent=self.root):
                return
        try:
            res = core.write_flash(core.load_save(src), dst, slot,
                                   pj64=self.fmt_var.get() == 'project64',
                                   merge=self.merge_var.get(), backup=self.backup_var.get())
        except Exception as e:
            self.say(f'Conversion failed: {e}', 'err')
            return
        name = core.describe_json(self.save)['name']
        msg = f'Done. {name} is in slot {slot} of {os.path.basename(dst)}.'
        if res['backup']:
            msg += f"\nYour old file was backed up as {os.path.basename(res['backup'])}."
        msg += "\nIf Project64 is open, restart it before playing. Otherwise it can write its old copy over this file."
        self.say(msg, 'ok')
        self.last_dir = os.path.dirname(os.path.abspath(dst))
        self.open_btn.grid()
        self.refresh_output()

    def open_folder(self):
        try:
            os.startfile(self.last_dir)
        except Exception:
            pass


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    App(root, sys.argv[1] if len(sys.argv) > 1 else None)
    root.mainloop()


if __name__ == '__main__':
    main()
