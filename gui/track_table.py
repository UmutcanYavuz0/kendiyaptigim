import webbrowser
import tkinter as tk
from tkinter import ttk

from config import BG_CARD, BG_ROW, BORDER, TEXT_DIM, FONT_H2


def build_track_header(parent) -> None:
    """Render the column-header row above the track list."""
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=2, pady=6)
    ch = ttk.Frame(parent, style="Card.TFrame", padding=(12, 4))
    ch.pack(fill="x", padx=2)
    ttk.Label(ch, text="#",     style="CardDim.TLabel", width=3).pack(side="left")
    ttk.Label(ch, text="TITLE", style="CardDim.TLabel",
              font=("Helvetica", 8, "bold")).pack(side="left", padx=(8, 0))
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=2)


def build_track_row(parent, index: int, track: dict) -> None:
    """Render a single track row."""
    row = ttk.Frame(parent, style="Row.TFrame", padding=(12, 6))
    row.pack(fill="x", padx=2)

    ttk.Label(row, text=str(index), style="RowDim.TLabel",
              width=3, anchor="e").pack(side="left")

    info = ttk.Frame(row, style="Row.TFrame")
    info.pack(side="left", fill="x", expand=True, padx=(10, 0))
    ttk.Label(info, text=track["title"], style="Row.TLabel",
              font=("Helvetica", 10, "bold")).pack(anchor="w")
    ttk.Label(info, text=track["artist"], style="RowDim.TLabel").pack(anchor="w")

    if track.get("url"):
        ttk.Button(
            row, text="LISTEN", style="Listen.TButton",
            command=lambda u=track["url"]: webbrowser.open(u),
        ).pack(side="right")
