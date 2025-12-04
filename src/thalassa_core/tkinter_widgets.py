import tkinter as tk 
import ttkbootstrap as ttk
from tkinter import filedialog

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self)
        self.scroll_frame = ttk.Frame(self.canvas)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Window inside the canvas
        self.window_id = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Update scroll region when frame changes
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bind canvas width to scroll_frame width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Optional: bind mouse wheel scrolling
        self.scroll_frame.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.scroll_frame.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _on_canvas_configure(self, event):
        # Force scroll_frame to match canvas width
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")