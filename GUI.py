import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

from io_utils import (
    read_message,
    write_message,
    read_huffman_compressed,
    write_huffman_compressed,
)
from compression import (
    modified_huffman_compression,
    modified_huffman_decompression,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- theme ----------
BG, CARD, BORDER = "#F4F6F9", "#FFFFFF", "#CBD5E1"
NAVY, ACCENT, ACCENT_DARK = "#1F3A5F", "#2563EB", "#1D4ED8"
TEXT, MUTED = "#1F2937", "#6B7280"
OK, ERR = "#15803D", "#B91C1C"
FONT, MONO = "Segoe UI", "Consolas"


def clean_name(path, strip_metadata=False):
    """Accepts 'file', 'file.txt' or (for compressed input) 'file_metadata.txt'."""
    name = path.strip()
    if name.lower().endswith(".txt"):
        name = name[:-4]
    if strip_metadata and name.endswith("_metadata"):
        name = name[:-len("_metadata")]
    return name


def full_path(name):
    return os.path.normcase(os.path.abspath(os.path.join(BASE_DIR, name)))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modified Huffman Compressor")
        self.configure(bg=BG)
        self.minsize(660, 620)
        self._center(720, 720)

        self.c_in, self.c_out = tk.StringVar(), tk.StringVar()
        self.d_in, self.d_out = tk.StringVar(), tk.StringVar()
        self.stats = tk.StringVar(value="No operation yet.")
        self.status = tk.StringVar(value="Ready")

        self._setup_style()
        self._build_header()
        self._build_statusbar()      # packed before the results so it is never squeezed out
        self._build_tabs()
        self._build_results()
        self.bind("<Return>", self._on_enter)

    # ---------- window / style ----------
    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")                      # the theme that accepts custom colours everywhere
        s.configure(".", background=BG, foreground=TEXT, font=(FONT, 10))
        s.configure("Card.TFrame", background=CARD)
        s.configure("Card.TLabel", background=CARD)
        s.configure("Stats.TLabel", foreground=NAVY, font=(FONT, 10, "bold"))
        s.configure("Status.TLabel", background="#E5E9F0", foreground=MUTED, padding=(12, 5))

        s.configure("TEntry", fieldbackground=CARD, bordercolor=BORDER, padding=6)
        s.configure("TButton", background="#E5E9F0", bordercolor=BORDER, padding=(12, 6))
        s.map("TButton", background=[("active", "#D5DBE5")])
        s.configure("Accent.TButton", background=ACCENT, foreground="white",
                    bordercolor=ACCENT, font=(FONT, 10, "bold"), padding=(22, 8))
        s.map("Accent.TButton", background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)])

        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background="#E5E9F0", padding=(22, 8), font=(FONT, 10))
        s.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", ACCENT)])

        s.configure("TLabelframe", background=BG, bordercolor=BORDER)
        s.configure("TLabelframe.Label", background=BG, foreground=NAVY, font=(FONT, 10, "bold"))

    # ---------- layout ----------
    def _build_header(self):
        header = tk.Frame(self, bg=NAVY)
        header.pack(fill="x")
        tk.Label(header, text="Modified Huffman Compressor", bg=NAVY, fg="white",
                 font=(FONT, 17, "bold")).pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(header, text="Compress and decompress text files", bg=NAVY, fg="#BFD0E8",
                 font=(FONT, 10)).pack(anchor="w", padx=20, pady=(0, 14))

    def _build_statusbar(self):
        self.status_label = ttk.Label(self, textvariable=self.status, style="Status.TLabel", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

    def _build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="x", padx=16, pady=(16, 8))
        self._make_tab("Compress", self.c_in, self.c_out, "Text file to compress",
                       "Save compressed as", "Compress", self.on_compress, compressed_input=False)
        self._make_tab("Decompress", self.d_in, self.d_out, "Compressed file",
                       "Save original text as", "Decompress", self.on_decompress, compressed_input=True)

    def _make_tab(self, title, in_var, out_var, in_label, out_label, btn_text, command, compressed_input):
        tab = ttk.Frame(self.nb, style="Card.TFrame", padding=18)
        tab.columnconfigure(1, weight=1)
        self._file_row(tab, 0, in_label, in_var, "Browse…",
                       lambda: self.browse_open(in_var, compressed_input))
        self._file_row(tab, 1, out_label, out_var, "Save as…",
                       lambda: self.browse_save(out_var))
        ttk.Button(tab, text=btn_text, style="Accent.TButton", command=command
                   ).grid(row=2, column=0, columnspan=3, sticky="e", pady=(14, 0))
        self.nb.add(tab, text=title)

    def _file_row(self, parent, row, label, var, btn_text, browse):
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 14), pady=6)
        ttk.Entry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(parent, text=btn_text, command=browse).grid(row=row, column=2, padx=(8, 0), pady=6)

    def _build_results(self):
        box = ttk.LabelFrame(self, text=" Results ", padding=12)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        ttk.Label(box, textvariable=self.stats, style="Stats.TLabel").pack(anchor="w", pady=(0, 8))

        self.output = ScrolledText(box, height=12, wrap="char", font=(MONO, 10), bg=CARD, fg=TEXT,
                                   relief="flat", highlightthickness=1, highlightbackground=BORDER,
                                   padx=10, pady=8, state="disabled")
        self.output.pack(fill="both", expand=True)
        self.output.tag_configure("h", font=(MONO, 10, "bold"), foreground=NAVY, spacing3=4)
        self.output.tag_configure("bits", foreground=ACCENT)

    # ---------- helpers ----------
    def show(self, *parts):
        """parts = (text, tag) pairs; the box stays read-only for the user."""
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        for text, tag in parts:
            self.output.insert("end", text, tag or ())
        self.output.config(state="disabled")

    def set_status(self, text, ok=True):
        self.status.set(text)
        self.status_label.config(foreground=OK if ok else ERR)

    def fail(self, error):
        self.set_status(f"Error: {error}", ok=False)
        messagebox.showerror("Error", str(error))

    def get_names(self, in_var, out_var, compressed_input):
        src = clean_name(in_var.get(), strip_metadata=compressed_input)
        dst = clean_name(out_var.get())
        if not src or not dst:
            raise ValueError("Please fill in both file names.")
        if full_path(src) == full_path(dst):
            raise ValueError("The output name must be different from the input name.")
        return src, dst

    def browse_open(self, var, compressed_input):
        path = filedialog.askopenfilename(title="Select file", initialdir=BASE_DIR,
                                          filetypes=[("Text files", "*.txt")])
        if path:
            var.set(self._display(clean_name(path, strip_metadata=compressed_input)))

    def browse_save(self, var):
        path = filedialog.asksaveasfilename(title="Save as", initialdir=BASE_DIR,
                                            defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            var.set(self._display(clean_name(path)))

    @staticmethod
    def _display(name):
        """Show just the file name when it lives in the project folder, the full path otherwise."""
        if os.path.dirname(full_path(name)) == os.path.normcase(BASE_DIR):
            return os.path.basename(name)
        return name

    def _on_enter(self, _event):
        (self.on_compress, self.on_decompress)[self.nb.index(self.nb.select())]()

    # ---------- actions ----------
    def on_compress(self):
        try:
            src, dst = self.get_names(self.c_in, self.c_out, compressed_input=False)
            message = read_message(src)
            if message is None:
                raise ValueError(f"File '{src}.txt' was not found.")
            bitstream, metadata = modified_huffman_compression(message)
            write_huffman_compressed(bitstream, metadata, dst)
        except (ValueError, SyntaxError, KeyError, TypeError, OSError) as e:
            return self.fail(e)

        original_bits = len(message) * 8             # assumes 8 bits per character
        saved = (1 - len(bitstream) / original_bits) * 100
        self.stats.set(f"Characters: {len(message)}   |   Original: {original_bits} bits   |   "
                       f"Compressed: {len(bitstream)} bits   |   Saved: {saved:.1f}%")
        codes = sorted(metadata["codes"], key=lambda sc: (len(sc[1]), sc[1]))
        table = "\n".join(f"{sym!r:<12}{code}" for sym, code in codes)
        self.show(
            ("Code table\n", "h"), (table + "\n", None),
            (f"\nOTHERS is followed by a fixed {metadata['id_width']}-bit symbol id.\n\n", None),
            ("Bitstream\n", "h"), (bitstream, "bits"),
        )
        self.set_status(f"Created {dst}.txt and {dst}_metadata.txt")

    def on_decompress(self):
        try:
            src, dst = self.get_names(self.d_in, self.d_out, compressed_input=True)
            bitstream, metadata = read_huffman_compressed(src)
            if bitstream is None or metadata is None:
                raise ValueError(f"'{src}.txt' or '{src}_metadata.txt' was not found.")
            bitstream = bitstream.strip()
            message = modified_huffman_decompression(bitstream, metadata)
            write_message(message, dst)
        except (ValueError, SyntaxError, KeyError, TypeError, OSError) as e:
            return self.fail(e)

        self.stats.set(f"Bitstream: {len(bitstream)} bits   |   Characters restored: {len(message)}")
        self.show(("Decompressed text\n", "h"), ("".join(message), None))
        self.set_status(f"Created {dst}.txt")


if __name__ == "__main__":
    try:                                              # sharp text on high-DPI Windows screens
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()