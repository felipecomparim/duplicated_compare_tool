#!/usr/bin/env python3
"""Duplicated & Compare Lists Tool — Python cross-platform port.

Port of ``src/duplicated_compare_tool.ahk`` (AutoHotkey v1, Windows-only)
to Python 3 + tkinter, running on macOS, Linux and Windows with stdlib only.

Features (same behavior as the AHK version):
- Finds duplicated lines (case-insensitive).
- Builds distinct lines list (case-insensitive, first-seen casing kept).
- Compare 2 lists: common, only in A, only in B, dupes in A, dupes in B.
- Custom names for lists A and B.
- Line indicator on each compare input: ``Ln X / Y``.
- Empty lines are ignored.

GUI:
- Main window auto-loads the clipboard (like the AHK hotkey flow) and also
  offers an editable input + "Analyze" so it works without a global hotkey.
- In-app shortcut Ctrl+Shift+Y reloads from clipboard (works on all 3 OSes).
- Optional OS-wide global hotkey via ``--global-hotkey`` (needs ``pynput``).

CLI (headless, useful on servers / for tests):
    python duplicated_compare_tool.py --no-gui --text "a\\nA\\nb"
    python duplicated_compare_tool.py --no-gui --file input.txt
    python duplicated_compare_tool.py --no-gui --compare-a a.txt --compare-b b.txt
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from tkinter import messagebox, ttk

APP_TITLE_MAIN = "Duplicated & Distinct lines"
APP_TITLE_COMPARE = "Compare 2 lists"
APP_GEOMETRY_MAIN = "720x640"
APP_GEOMETRY_COMPARE = "980x680"

NO_DUPLICATES_MSG = "No duplicates found."
NONE_MARKER = "(none)"


# ---------------------------------------------------------------------------
# Core logic (pure functions, no GUI — identical semantics to the AHK script)
# ---------------------------------------------------------------------------

def iter_significant_lines(text: str):
    """Yield stripped, non-empty lines in order (mirrors AHK Trim+skip)."""
    if not text:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if line:
            yield line


def build_case_insensitive_maps(text: str):
    """Return (counts, originals) keyed by casefolded line.

    ``originals`` keeps the first-seen original casing (like the AHK version).
    ``counts`` holds occurrence counts. Both preserve first-seen order.
    """
    counts: dict[str, int] = {}
    originals: dict[str, str] = {}
    for line in iter_significant_lines(text or ""):
        key = line.casefold()
        if key not in originals:
            originals[key] = line
        counts[key] = counts.get(key, 0) + 1
    return counts, originals


def analyze_text(text: str) -> dict:
    """Analyze one block of text. Returns dupes/distinct data + render texts."""
    counts, originals = build_case_insensitive_maps(text)
    dupes = [(originals[k], v) for k, v in counts.items() if v > 1]
    distinct = list(originals.values())
    if dupes:
        dupes_text = "".join(f"{orig} (x{cnt})\n" for orig, cnt in dupes)
    else:
        dupes_text = NO_DUPLICATES_MSG + "\n"
    distinct_text = "".join(f"{line}\n" for line in distinct)
    return {
        "counts": counts,
        "originals": originals,
        "dupes": dupes,
        "distinct": distinct,
        "distinct_count": len(originals),
        "dupe_count": len(dupes),
        "dupes_text": dupes_text,
        "distinct_text": distinct_text,
        "header": f"Found {len(originals)} distinct values - {len(dupes)} duplicates",
    }


def compare_texts(text_a: str, text_b: str, name_a: str = "A", name_b: str = "B") -> dict:
    """Compare two lists. Output sections mirror the AHK script exactly."""
    name_a = (name_a or "").strip() or "A"
    name_b = (name_b or "").strip() or "B"

    counts_a, originals_a = build_case_insensitive_maps(text_a)
    counts_b, originals_b = build_case_insensitive_maps(text_b)

    keys_a = set(originals_a)
    keys_b = set(originals_b)

    # Order follows first-seen order of each list (AHK iterates its maps).
    common = [originals_a[k] for k in originals_a if k in keys_b]
    only_a = [originals_a[k] for k in originals_a if k not in keys_b]
    only_b = [originals_b[k] for k in originals_b if k not in keys_a]
    dupes_a = [(originals_a[k], v) for k, v in counts_a.items() if v > 1]
    dupes_b = [(originals_b[k], v) for k, v in counts_b.items() if v > 1]

    def _block(lines):
        if not lines:
            return NONE_MARKER + "\n"
        return "".join(f"{line}\n" for line in lines)

    common_text = _block(common)
    only_a_text = _block(only_a)
    only_b_text = _block(only_b)
    dupes_a_text = _block([f"{o} (x{c})" for o, c in dupes_a])
    dupes_b_text = _block([f"{o} (x{c})" for o, c in dupes_b])

    result = (
        f"=== Comuns em {name_a} e {name_b} ({len(common)}) ===\n"
        f"{common_text}\n"
        f"=== Em {name_a} e nao em {name_b} ({len(only_a)}) ===\n"
        f"{only_a_text}\n"
        f"=== Em {name_b} e nao em {name_a} ({len(only_b)}) ===\n"
        f"{only_b_text}\n"
        f"=== Duplicado em {name_a} ({len(dupes_a)}) ===\n"
        f"{dupes_a_text}\n"
        f"=== Duplicado em {name_b} ({len(dupes_b)}) ===\n"
        f"{dupes_b_text}"
    )
    summary = (
        f"Distinct {name_a}: {len(originals_a)} | "
        f"Distinct {name_b}: {len(originals_b)} | "
        f"Common: {len(common)} | "
        f"Only {name_a}: {len(only_a)} | "
        f"Only {name_b}: {len(only_b)}"
    )
    return {
        "name_a": name_a,
        "name_b": name_b,
        "common": common,
        "only_a": only_a,
        "only_b": only_b,
        "dupes_a": dupes_a,
        "dupes_b": dupes_b,
        "distinct_a_count": len(originals_a),
        "distinct_b_count": len(originals_b),
        "result_text": result,
        "summary_text": summary,
    }


def line_indicator(total_text: str, cursor_line: int = 1) -> str:
    """Build the 'Ln X / Y' label (empty content -> 'Ln 1 / 1', like AHK)."""
    total = len(total_text.splitlines()) if total_text else 0
    total = max(total, 1)
    cur = max(1, min(cursor_line, total)) if total_text else 1
    return f"Ln {cur} / {total}"


# ---------------------------------------------------------------------------
# Clipboard helpers (tkinter-based, cross-platform)
# ---------------------------------------------------------------------------

def clipboard_get_text(root: tk.Tk) -> str:
    try:
        return root.clipboard_get()
    except tk.TclError:
        return ""


def clipboard_set_text(root: tk.Tk, text: str) -> None:
    root.clipboard_clear()
    root.clipboard_append(text or "")
    # Keep ownership while app runs (needed on Linux/X11).
    root.update()


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def _make_text(parent, height=8, readonly=False, wrap="none"):
    widget = tk.Text(parent, height=height, wrap=wrap, undo=True)
    if readonly:
        widget.configure(state="disabled", bg=parent.cget("bg") if isinstance(parent, tk.Text) else None)
    # Horizontal + vertical scrollbars are added by the caller layout if needed.
    return widget


def _set_text(widget: tk.Text, text: str, readonly=True) -> None:
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", text or "")
    if readonly:
        widget.configure(state="disabled")


class ScrolledText(tk.Frame):
    """Text area showing 12 visible lines; the rest scrolls.

    Drop-in replacement for tk.Text: the Text API used by this app
    (.get/.insert/.delete/.index/.bind/.focus_set/.configure/.cget)
    is forwarded to the inner widget.
    """

    LINES = 12

    def __init__(self, master, height=LINES, readonly=False, **kwargs):
        super().__init__(master)
        kwargs.setdefault("wrap", "none")
        kwargs.setdefault("undo", True)
        self.text = tk.Text(self, height=height, **kwargs)
        vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        hsb = tk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.text.pack(side="left", fill="both", expand=True)
        if readonly:
            self.text.configure(state="disabled")

    # -- forwarded Text API --
    def configure(self, *args, **kwargs):
        return self.text.configure(*args, **kwargs)

    config = configure

    def cget(self, *args, **kwargs):
        return self.text.cget(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.text.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.text.delete(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self.text.index(*args, **kwargs)

    def bind(self, *args, **kwargs):
        return self.text.bind(*args, **kwargs)

    def focus_set(self, *args, **kwargs):
        return self.text.focus_set(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.__dict__["text"], name)


class ComparePanel(tk.Frame):
    """Compare-2-lists panel.

    Lives as a tab inside the main window, so it can never hide behind it
    (fixes "Compare 2 lists does not appear" on some macOS/Linux WMs).
    Logic is a port of the AHK DupToolCompare GUI.
    """

    def __init__(self, master):
        super().__init__(master)

        self.name_a_var = tk.StringVar(value="A")
        self.name_b_var = tk.StringVar(value="B")
        self.pos_a_var = tk.StringVar(value="Ln 1 / 1")
        self.pos_b_var = tk.StringVar(value="Ln 1 / 1")
        self.summary_var = tk.StringVar(value="")

        # Bottom dock FIRST (side=bottom): pack() serves earlier-packed widgets
        # first, so Process/Clear/summary/result keep their space on small
        # screens and the input lists above shrink instead (all scrollable).
        # Visual order is unchanged (buttons, summary, result at the bottom).
        dock = tk.Frame(self)
        dock.pack(side="bottom", fill="x", padx=10, pady=(4, 10))
        btns = tk.Frame(dock)
        btns.pack(fill="x", pady=(0, 6))
        tk.Button(btns, text="Process", width=12, command=self.process).pack(side="left")
        tk.Button(btns, text="Clear", width=10, command=self.clear).pack(side="left", padx=(8, 0))

        tk.Label(dock, textvariable=self.summary_var, fg="blue",
                 anchor="w", justify="left").pack(fill="x")

        self.result = ScrolledText(dock, height=ScrolledText.LINES, readonly=True)
        self.result.pack(fill="x", pady=(2, 0))

        # --- List A header row ---
        row_a = tk.Frame(self)
        row_a.pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(row_a, text="List").pack(side="left")
        tk.Entry(row_a, textvariable=self.name_a_var, width=18).pack(side="left", padx=(6, 0))
        tk.Label(row_a, text="(one line per item):").pack(side="left", padx=(6, 0))
        tk.Label(row_a, textvariable=self.pos_a_var, width=12, anchor="e").pack(side="right")

        self.list_a = ScrolledText(self, height=ScrolledText.LINES)
        self.list_a.pack(fill="both", expand=True, padx=10, pady=(2, 0))

        # --- List B header row ---
        row_b = tk.Frame(self)
        row_b.pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(row_b, text="List").pack(side="left")
        tk.Entry(row_b, textvariable=self.name_b_var, width=18).pack(side="left", padx=(6, 0))
        tk.Label(row_b, text="(one line per item):").pack(side="left", padx=(6, 0))
        tk.Label(row_b, textvariable=self.pos_b_var, width=12, anchor="e").pack(side="right")

        self.list_b = ScrolledText(self, height=ScrolledText.LINES)
        self.list_b.pack(fill="both", expand=True, padx=10, pady=(2, 0))

        for widget in (self.list_a, self.list_b):
            widget.bind("<KeyRelease>", self._on_edit_activity)
            widget.bind("<ButtonRelease-1>", self._on_edit_activity)
            widget.bind("<FocusIn>", self._on_edit_activity)
            # Catch paste / cut / undo which may not fire KeyRelease reliably.
            widget.bind("<<Paste>>", lambda _e: self.after(10, self.update_line_info))
            widget.bind("<<Cut>>", lambda _e: self.after(10, self.update_line_info))

        self.update_line_info()

    # -- actions --
    def process(self) -> None:
        data = compare_texts(
            self.list_a.get("1.0", "end-1c"),
            self.list_b.get("1.0", "end-1c"),
            self.name_a_var.get(),
            self.name_b_var.get(),
        )
        self.summary_var.set(data["summary_text"])
        _set_text(self.result, data["result_text"], readonly=True)

    def clear(self) -> None:
        for w in (self.list_a, self.list_b):
            w.delete("1.0", tk.END)
        self.summary_var.set("")
        _set_text(self.result, "", readonly=True)
        self.update_line_info()

    # -- Ln X / Y indicator (port of DupTool_UpdateOneEditLineInfo) --
    def _on_edit_activity(self, _event=None) -> None:
        self.update_line_info()

    def update_line_info(self) -> None:
        for widget, var in ((self.list_a, self.pos_a_var), (self.list_b, self.pos_b_var)):
            content = widget.get("1.0", "end-1c")
            try:
                cursor = int(str(widget.index(tk.INSERT)).split(".")[0])
            except (tk.TclError, ValueError):
                cursor = 1
            var.set(line_indicator(content, cursor))


class CompareWindow(tk.Toplevel):
    """Optional detached Compare window (same panel, separate window)."""

    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.title(APP_TITLE_COMPARE)
        self.geometry(APP_GEOMETRY_COMPARE)
        try:
            if master.attributes("-topmost"):
                self.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.panel = ComparePanel(self)
        self.panel.pack(fill="both", expand=True)
        # Forward the widgets/methods used elsewhere.
        self.list_a = self.panel.list_a
        self.list_b = self.panel.list_b
        self.process = self.panel.process
        self.clear = self.panel.clear
        self.update_line_info = self.panel.update_line_info


class DuplicatesApp(tk.Tk):
    """Main window: menu bar (File/Edit/View/Tools) + tabs."""

    def __init__(self, initial_text: str = "", auto_clipboard: bool = True):
        super().__init__()
        self.title(APP_TITLE_MAIN)
        # Fit smaller (notebook) screens: never open taller than the display,
        # otherwise the bottom bar starts off-screen.
        try:
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        except tk.TclError:
            sw, sh = 1280, 800
        w = min(980, max(640, sw - 40))
        h = min(850, max(520, sh - 80))
        self.geometry(f"{w}x{h}")
        self.minsize(640, 480)
        self.topmost_var = tk.BooleanVar(value=False)
        self.header_var = tk.StringVar(value="Paste lines and click Analyze.")
        # Strong reference for the optional detached window (avoids GC flash).
        self.compare_window: CompareWindow | None = None

        self._build_menu()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # --- Tab 1: Duplicates ---
        dup_tab = tk.Frame(self.notebook)
        self.notebook.add(dup_tab, text="Duplicates")

        tk.Label(dup_tab, text="Input (one line per item):", anchor="w").pack(fill="x", padx=10, pady=(8, 0))
        self.input_text = ScrolledText(dup_tab, height=9)
        self.input_text.pack(fill="both", expand=False, padx=10, pady=(2, 0))

        in_btns = tk.Frame(dup_tab)
        in_btns.pack(fill="x", padx=10, pady=6)
        tk.Button(in_btns, text="Paste from Clipboard (Ctrl+Shift+Y)",
                  command=self.load_from_clipboard).pack(side="left")
        tk.Button(in_btns, text="Analyze", width=12,
                  command=self.analyze).pack(side="left", padx=(8, 0))
        tk.Button(in_btns, text="Clear Input", width=12,
                  command=self.clear_input).pack(side="left", padx=(8, 0))

        # Bottom action bar docks FIRST (side=bottom): pack() gives space to
        # earlier-packed widgets first, so docking the bar first guarantees it
        # is never pushed off-screen — the text areas above shrink instead
        # (they are scrollable, 12 visible lines when space allows).
        out_btns = tk.Frame(dup_tab)
        out_btns.pack(side="bottom", fill="x", padx=10, pady=8)
        tk.Button(out_btns, text="Copy Duplicates", command=self.copy_dupes).pack(side="left")
        tk.Button(out_btns, text="Copy Distinct", command=self.copy_distinct).pack(side="left", padx=(8, 0))
        tk.Button(out_btns, text="Compare 2 lists", command=self.show_compare).pack(side="left", padx=(8, 0))
        tk.Checkbutton(out_btns, text="Always on top", variable=self.topmost_var,
                       command=self.toggle_topmost).pack(side="left", padx=(12, 0))
        tk.Button(out_btns, text="Close", width=10, command=self.destroy).pack(side="right")

        tk.Label(dup_tab, textvariable=self.header_var, fg="blue", anchor="w").pack(fill="x", padx=10)

        tk.Label(dup_tab, text="Duplicated (case-insensitive) lines:", anchor="w").pack(fill="x", padx=10)
        self.dup_text = ScrolledText(dup_tab, height=9, readonly=True)
        self.dup_text.pack(fill="both", expand=True, padx=10, pady=(2, 0))

        tk.Label(dup_tab, text="Distinct values (case-insensitive) from selection:",
                 anchor="w").pack(fill="x", padx=10, pady=(6, 0))
        self.distinct_text = ScrolledText(dup_tab, height=ScrolledText.LINES, readonly=True)
        self.distinct_text.pack(fill="both", expand=True, padx=10, pady=(2, 0))

        # --- Tab 2: Compare 2 lists (embedded: always visible, never hidden) ---
        compare_tab = tk.Frame(self.notebook)
        self.notebook.add(compare_tab, text="Compare 2 lists")
        self.compare_panel = ComparePanel(compare_tab)
        self.compare_panel.pack(fill="both", expand=True)

        # In-app shortcut (works on macOS/Linux/Windows while the app is focused).
        for seq in ("<Control-Shift-Y>", "<Control-Shift-y>"):
            self.bind_all(seq, lambda _e: self.load_from_clipboard())

        if initial_text:
            self.input_text.insert("1.0", initial_text)
            self.analyze()
        elif auto_clipboard:
            self.after(50, self.load_from_clipboard)

    # -- actions --
    def load_from_clipboard(self) -> None:
        text = clipboard_get_text(self)
        if not text.strip():
            messagebox.showwarning("Duplicates", "Clipboard is empty.", parent=self)
            return
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", text)
        self.analyze()

    def analyze(self) -> None:
        data = analyze_text(self.input_text.get("1.0", "end-1c"))
        self.header_var.set(data["header"])
        _set_text(self.dup_text, data["dupes_text"], readonly=True)
        _set_text(self.distinct_text, data["distinct_text"], readonly=True)

    def clear_input(self) -> None:
        self.input_text.delete("1.0", tk.END)
        self.header_var.set("Paste lines and click Analyze.")
        _set_text(self.dup_text, "", readonly=True)
        _set_text(self.distinct_text, "", readonly=True)

    def _copy_widget(self, widget: tk.Text, label: str) -> None:
        text = widget.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("Duplicates", f"Nothing to copy ({label}).", parent=self)
            return
        clipboard_set_text(self, text + "\n")
        messagebox.showinfo("Duplicates", f"{label} copied.", parent=self)

    def copy_dupes(self) -> None:
        self._copy_widget(self.dup_text, "Duplicates")

    def copy_distinct(self) -> None:
        self._copy_widget(self.distinct_text, "Distinct list")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Copy duplicates", command=self.copy_dupes)
        edit_menu.add_command(label="Copy distinct", command=self.copy_distinct)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_checkbutton(label="Always on top",
                                  variable=self.topmost_var,
                                  command=self.toggle_topmost)
        menubar.add_cascade(label="View", menu=view_menu)

        tools_menu = tk.Menu(menubar, tearoff=False)
        tools_menu.add_command(label="Compare 2 lists", accelerator="Ctrl+T",
                               command=self.show_compare)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        self.bind_all("<Control-q>", lambda _e: self.destroy())
        self.bind_all("<Control-t>", lambda _e: self.show_compare())
        # macOS Cmd equivalents.
        self.bind_all("<Command-q>", lambda _e: self.destroy())
        self.bind_all("<Command-t>", lambda _e: self.show_compare())
        try:
            self.createcommand("tk::mac::Quit", self.destroy)
        except tk.TclError:
            pass

    def show_compare(self) -> None:
        """Switch to the embedded Compare tab — it cannot hide behind."""
        try:
            self.notebook.select(1)
        except tk.TclError:
            pass
        try:
            self.lift()
            self.compare_panel.list_a.focus_set()
        except tk.TclError:
            pass

    def open_compare(self) -> None:
        """Back-compat alias (button/shortcut target)."""
        self.show_compare()

    def open_compare_window(self) -> None:
        """Open Compare in a detached window (optional alternative)."""
        if self.compare_window is not None:
            try:
                if self.compare_window.winfo_exists():
                    self.compare_window.deiconify()
                    self.compare_window.lift()
                    self.compare_window.focus_force()
                    return
            except tk.TclError:
                pass
            self.compare_window = None
        win = CompareWindow(self)
        self.compare_window = win
        win.protocol("WM_DELETE_WINDOW", self._on_compare_close)
        try:
            win.deiconify()
            win.lift()
            win.focus_force()
        except tk.TclError:
            pass

    def _on_compare_close(self) -> None:
        if self.compare_window is not None:
            try:
                self.compare_window.destroy()
            except tk.TclError:
                pass
            self.compare_window = None

    def toggle_topmost(self) -> None:
        top = bool(self.topmost_var.get())
        try:
            self.attributes("-topmost", top)
        except tk.TclError:
            pass
        if self.compare_window is not None:
            try:
                if self.compare_window.winfo_exists():
                    self.compare_window.attributes("-topmost", top)
            except tk.TclError:
                pass


# ---------------------------------------------------------------------------
# Optional OS-wide global hotkey (needs `pynput`; in-app Ctrl+Shift+Y always works)
# ---------------------------------------------------------------------------

def maybe_register_global_hotkey(app: DuplicatesApp) -> None:
    try:
        from pynput import keyboard  # type: ignore
    except ImportError:
        print("Global hotkey disabled: 'pynput' is not installed "
              "(pip install pynput). In-app Ctrl+Shift+Y still works.",
              file=sys.stderr)
        return

    def _on_activate():
        app.after(0, app.load_from_clipboard)
        try:
            app.after(0, app.lift)
            app.after(0, app.focus_force)
        except tk.TclError:
            pass

    hotkey = keyboard.HotKey(keyboard.HotKey.parse("<ctrl>+<shift>+y"), _on_activate)

    def _for_canonical(f):
        return lambda k: f(listener.canonical(k))

    listener = keyboard.Listener(
        on_press=_for_canonical(hotkey.press),
        on_release=_for_canonical(hotkey.release),
    )
    listener.daemon = True
    listener.start()
    print("Global hotkey active: Ctrl+Shift+Y -> load clipboard.", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def read_source_text(args) -> str:
    if args.text is not None:
        return args.text
    if args.file:
        with open(args.file, encoding="utf-8-sig") as fh:
            return fh.read()
    return ""


def run_headless(args) -> int:
    if args.compare_a or args.compare_b:
        if not (args.compare_a and args.compare_b):
            print("error: --compare-a and --compare-b must be used together", file=sys.stderr)
            return 2
        with open(args.compare_a, encoding="utf-8-sig") as fh:
            text_a = fh.read()
        with open(args.compare_b, encoding="utf-8-sig") as fh:
            text_b = fh.read()
        data = compare_texts(text_a, text_b, args.name_a, args.name_b)
        print(data["summary_text"])
        print(data["result_text"])
        return 0
    text = read_source_text(args)
    if not text and not args.clipboard:
        print("error: provide --text, --file or --clipboard", file=sys.stderr)
        return 2
    if args.clipboard and not text:
        print("error: --clipboard needs a GUI session; use --text/--file instead", file=sys.stderr)
        return 2
    data = analyze_text(text)
    print(data["header"])
    print("--- Duplicated ---")
    print(data["dupes_text"], end="")
    print("--- Distinct ---")
    print(data["distinct_text"], end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Duplicated & Compare Lists Tool (Python port)")
    ap.add_argument("--run", action="store_true",
                    help="AHK compat: auto-load clipboard on start (default behavior)")
    ap.add_argument("--no-gui", action="store_true", help="print results to stdout, no window")
    ap.add_argument("--text", default=None, help="analyze this literal text (headless or GUI seed)")
    ap.add_argument("--file", default=None, help="analyze text from file")
    ap.add_argument("--clipboard", action="store_true",
                    help="(headless note) kept for parity; clipboard read needs GUI")
    ap.add_argument("--compare-a", default=None, help="file for list A (with --compare-b)")
    ap.add_argument("--compare-b", default=None, help="file for list B (with --compare-a)")
    ap.add_argument("--name-a", default="A", help="custom name for list A")
    ap.add_argument("--name-b", default="B", help="custom name for list B")
    ap.add_argument("--global-hotkey", action="store_true",
                    help="register OS-wide Ctrl+Shift+Y (requires 'pynput')")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.no_gui:
        return run_headless(args)

    initial = read_source_text(args)
    app = DuplicatesApp(initial_text=initial, auto_clipboard=not initial)
    if args.global_hotkey:
        maybe_register_global_hotkey(app)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
