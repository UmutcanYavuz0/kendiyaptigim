import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

from config import (
    GENRES, ERAS,
    BG_DARK, BG_CARD, BG_ROW, ACCENT, ACCENT_DK,
    TEXT_PRI, TEXT_SEC, TEXT_DIM, BORDER,
    FONT, FONT_SM, FONT_H1, FONT_H2,
)
from controllers.album_controller import AlbumController
from gui.track_table import build_track_header, build_track_row


class AlbumCoverStudio:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Album Cover Studio")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1050x750")
        self.root.minsize(900, 650)

        self._cover_image   = None
        self._cover_photo   = None
        self._album_data    = None
        self._tracklist     = []
        self._is_generating = False

        self._controller = AlbumController(
            on_status=self._set_status,
            on_success=lambda d, t, c: self.root.after(0, lambda: self._show_album(d, t, c)),
            on_error=lambda e:         self.root.after(0, lambda: self._on_error(e)),
        )

        self._build_styles()
        self._build_ui()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _build_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(".", background=BG_DARK, foreground=TEXT_PRI,
                    fieldbackground=BG_CARD, font=FONT)
        s.configure("TFrame",         background=BG_DARK)
        s.configure("Card.TFrame",    background=BG_CARD)
        s.configure("Row.TFrame",     background=BG_ROW)
        s.configure("TLabel",         background=BG_DARK, foreground=TEXT_PRI, font=FONT)
        s.configure("Dim.TLabel",     background=BG_DARK, foreground=TEXT_SEC, font=FONT_SM)
        s.configure("Card.TLabel",    background=BG_CARD, foreground=TEXT_PRI, font=FONT)
        s.configure("CardDim.TLabel", background=BG_CARD, foreground=TEXT_SEC, font=FONT_SM)
        s.configure("Row.TLabel",     background=BG_ROW,  foreground=TEXT_PRI, font=FONT)
        s.configure("RowDim.TLabel",  background=BG_ROW,  foreground=TEXT_SEC, font=FONT_SM)
        s.configure("Accent.TLabel",  background=BG_DARK, foreground=ACCENT,
                    font=("Helvetica", 9, "bold"))
        s.configure("H1.TLabel",      background=BG_DARK, foreground=TEXT_PRI, font=FONT_H1)
        s.configure("H2.TLabel",      background=BG_CARD, foreground=TEXT_PRI, font=FONT_H2)
        s.configure("Tag.TLabel",     background=BG_CARD, foreground=ACCENT,   font=FONT_SM)

        for name, bg, fg in [
            ("Accent.TButton", ACCENT,    "#000000"),
            ("Save.TButton",   ACCENT,    "#000000"),
            ("Listen.TButton", "#333333", TEXT_PRI),
        ]:
            s.configure(name, background=bg, foreground=fg,
                        font=("Helvetica", 9, "bold"),
                        borderwidth=0, relief="flat", padding=(8, 5))
        s.map("Accent.TButton", background=[("active", ACCENT_DK)])
        s.map("Save.TButton",   background=[("active", ACCENT_DK)])
        s.map("Listen.TButton",
              background=[("active", ACCENT), ("pressed", ACCENT_DK)],
              foreground=[("active", "#000000")])

        s.configure("TCombobox", fieldbackground=BG_CARD, background=BG_CARD,
                    foreground=TEXT_PRI, selectbackground=BG_CARD,
                    selectforeground=TEXT_PRI, arrowcolor=ACCENT)
        s.map("TCombobox",
              fieldbackground=[("readonly", BG_CARD)],
              foreground=[("readonly", TEXT_PRI)])
        s.configure("TSpinbox", fieldbackground=BG_CARD, background=BG_CARD,
                    foreground=TEXT_PRI, arrowcolor=ACCENT)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        hdr = ttk.Frame(self.root, style="TFrame", padding=(20, 14, 20, 10))
        hdr.pack(fill="x")
        ttk.Label(hdr, text="Album Cover Studio", style="H1.TLabel").pack(side="left")
        ttk.Label(hdr, text="  Describe your mood, enjoy the generated tracklist.",
                  style="Dim.TLabel").pack(side="left")
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        body = ttk.Frame(self.root, style="TFrame")
        body.pack(fill="both", expand=True)
        self._left_panel(body)
        self._right_panel(body)

    def _left_panel(self, parent):
        frame = ttk.Frame(parent, style="TFrame", padding=(20, 16, 12, 16))
        frame.pack(side="left", fill="y")
        frame.pack_propagate(False)
        frame.configure(width=340)

        ttk.Label(frame, text="Your Mood (English or Turkish)",
                  style="Accent.TLabel").pack(anchor="w")
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=(2, 6))

        self._journal = tk.Text(
            frame, height=7, wrap="word",
            bg=BG_CARD, fg=TEXT_PRI, insertbackground=ACCENT,
            relief="flat", font=FONT, padx=8, pady=8,
            highlightbackground=BORDER, highlightcolor=ACCENT, highlightthickness=1,
        )
        self._journal.pack(fill="x")
        self._journal.insert(
            "1.0",
            "I was looking at the sea in İzmir. It was raining softly, "
            "and an old song was playing through my headphones. "
            "I felt both peaceful and melancholic...",
        )

        pad = {"pady": (12, 0)}

        ttk.Label(frame, text="Genre", style="Accent.TLabel").pack(anchor="w", **pad)
        self._genre_var = tk.StringVar(value=GENRES[0])
        ttk.Combobox(frame, textvariable=self._genre_var,
                     values=GENRES, state="readonly").pack(fill="x", pady=(4, 0))

        ttk.Label(frame, text="Era", style="Accent.TLabel").pack(anchor="w", **pad)
        self._era_var = tk.StringVar(value="2000s")
        ttk.Combobox(frame, textvariable=self._era_var,
                     values=ERAS, state="readonly").pack(fill="x", pady=(4, 0))

        ttk.Label(frame, text="Track Count", style="Accent.TLabel").pack(anchor="w", **pad)
        self._tc_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=6, to=14, textvariable=self._tc_var,
                    state="readonly", width=6).pack(anchor="w", pady=(4, 0))

        self._gen_btn = ttk.Button(
            frame, text="GENERATE ALBUM",
            style="Accent.TButton", command=self._on_generate,
        )
        self._gen_btn.pack(fill="x", pady=(18, 0))

        self._status_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self._status_var,
                  style="Dim.TLabel", wraplength=300).pack(anchor="w", pady=(8, 0))

    def _right_panel(self, parent):
        outer = ttk.Frame(parent, style="TFrame", padding=(8, 8, 16, 16))
        outer.pack(side="left", fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=BG_DARK, highlightthickness=0)
        vbar = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._result_frame = ttk.Frame(self._canvas, style="TFrame")
        self._win_id = self._canvas.create_window(
            (0, 0), window=self._result_frame, anchor="nw")

        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._win_id, width=e.width))
        self._result_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._show_placeholder()

    def _show_placeholder(self):
        for w in self._result_frame.winfo_children():
            w.destroy()
        self._canvas.yview_moveto(0)
        ph = ttk.Frame(self._result_frame, style="TFrame", padding=60)
        ph.pack(expand=True, fill="both")
        ttk.Label(ph, text="♪", font=("Helvetica", 48),
                  background=BG_DARK, foreground=TEXT_DIM).pack()
        ttk.Label(ph, text="Generated tracklist will be shown here.",
                  style="Dim.TLabel").pack(pady=(10, 0))

    # ── Generate ──────────────────────────────────────────────────────────────

    def _on_generate(self):
        if self._is_generating:
            return

        journal = self._journal.get("1.0", "end").strip()
        if not journal:
            messagebox.showwarning("Eksik", "Lütfen bir ruh hali veya metin girin.")
            return

        self._is_generating = True
        self._gen_btn.state(["disabled"])
        self._status_var.set("⏳ Başlatılıyor...")
        self._cover_image = None
        self._cover_photo = None
        self._album_data  = None
        self._tracklist   = []
        self._show_placeholder()

        self._controller.generate(
            journal=journal,
            genre=self._genre_var.get(),
            era=self._era_var.get(),
            track_count=self._tc_var.get(),
        )

    def _set_status(self, msg: str):
        self.root.after(0, lambda: self._status_var.set(msg))

    def _on_error(self, msg: str):
        if "429" in msg:
            user_msg = "Günlük API limitini aştınız. Yeni bir API key deneyin veya biraz bekleyin."
        elif "503" in msg:
            user_msg = "Sunucu şu an çok yoğun. Birkaç saniye bekleyip tekrar deneyin."
        else:
            user_msg = msg

        self._status_var.set(f"❌ {user_msg}")
        self._is_generating = False
        self._gen_btn.state(["!disabled"])
        messagebox.showerror("Hata", user_msg)

    # ── Album display ─────────────────────────────────────────────────────────

    def _show_album(self, data: dict, tracks: list, cover):
        self._album_data  = data
        self._tracklist   = tracks
        self._cover_image = cover

        for w in self._result_frame.winfo_children():
            w.destroy()
        self._canvas.yview_moveto(0)

        # ── Header card ──────────────────────────────────────────────────────
        card = ttk.Frame(self._result_frame, style="Card.TFrame", padding=16)
        card.pack(fill="x", padx=2, pady=(4, 0))

        img_r = cover.resize((130, 130), Image.LANCZOS)
        self._cover_photo = ImageTk.PhotoImage(img_r)
        tk.Label(card, image=self._cover_photo, bg=BG_CARD, bd=0).pack(side="left", anchor="n")

        meta = ttk.Frame(card, style="Card.TFrame", padding=(14, 0, 0, 0))
        meta.pack(side="left", fill="both", expand=True)

        ttk.Label(meta, text="ALBUM · CURATED PLAYLIST",
                  style="CardDim.TLabel", font=("Helvetica", 8, "bold")).pack(anchor="w")
        ttk.Label(meta, text=data.get("album_name", "?"),
                  style="H2.TLabel", font=("Helvetica", 20, "bold")).pack(anchor="w", pady=(2, 4))
        ttk.Label(meta, text=data.get("mood_description", ""),
                  style="CardDim.TLabel", wraplength=420, justify="left").pack(anchor="w")
        ttk.Label(
            meta,
            text=f"{data.get('year','')}  •  {len(tracks)} songs  •  {data.get('label','')}",
            style="CardDim.TLabel",
        ).pack(anchor="w", pady=(6, 4))
        ttk.Label(
            meta,
            text="  ".join(f"#{t}" for t in data.get("lastfm_tags", [])[:6]),
            style="Tag.TLabel",
        ).pack(anchor="w")

        # ── Track list ───────────────────────────────────────────────────────
        build_track_header(self._result_frame)
        for i, track in enumerate(tracks, 1):
            build_track_row(self._result_frame, i, track)

        # ── Save button ──────────────────────────────────────────────────────
        tk.Frame(self._result_frame, bg=BORDER, height=1).pack(fill="x", padx=2, pady=(8, 0))
        ttk.Button(
            self._result_frame, text="💾  SAVE ALBUM (JSON + PNG)",
            style="Save.TButton", command=self._save,
        ).pack(fill="x", padx=2, pady=(6, 12))

        self._status_var.set(f"✅ {len(tracks)} gerçek şarkı yüklendi.")
        self._is_generating = False
        self._gen_btn.state(["!disabled"])

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        if not self._album_data or not self._cover_image:
            messagebox.showwarning("Boş", "Önce albüm oluşturun.")
            return
        folder = filedialog.askdirectory(title="Kayıt Klasörü Seç")
        if not folder:
            return
        name = self._album_data.get("album_name", "album").replace(" ", "_")
        json_path = os.path.join(folder, f"{name}.json")
        png_path  = os.path.join(folder, f"{name}_cover.png")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self._album_data, f, ensure_ascii=False, indent=2)
        self._cover_image.save(png_path, "PNG")
        messagebox.showinfo("Kaydedildi!", f"{json_path}\n{png_path}")
