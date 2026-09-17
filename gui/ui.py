import tkinter as tk
from tkinter import ttk

BG = "#F4F7F6"
SIDEBAR = "#163A35"
SIDEBAR_HOVER = "#24564E"
ACCENT = "#2E8B75"
WHITE = "#FFFFFF"
TEXT = "#1F2937"
SECONDARY = "#6B7280"
DANGER = "#B94A48"

def responsive_window(window, max_width=1050, max_height=680,
                      min_width=760, min_height=520):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    width = min(max_width, int(screen_w * 0.88))
    height = min(max_height, int(screen_h * 0.84))

    width = max(width, min_width)
    height = max(height, min_height)

    width = min(width, screen_w - 30)
    height = min(height, screen_h - 70)

    x = max((screen_w - width) // 2, 10)
    y = max((screen_h - height) // 2, 25)

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.minsize(min(min_width, screen_w - 30), min(min_height, screen_h - 70))
    window.resizable(True, True)

def setup_style():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Treeview", rowheight=27, font=("Arial", 9))
    style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
    style.configure("TCombobox", padding=4)

def make_scrollable_table(parent, columns, widths=None, height=10):
    frame = tk.Frame(parent, bg=WHITE)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        height=height
    )

    widths = widths or {}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(
            col,
            width=widths.get(col, 110),
            minwidth=60,
            anchor="center",
            stretch=True
        )

    ybar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    xbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)

    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    return frame, tree
