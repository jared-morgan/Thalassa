import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class RoundedButton(tk.Canvas):
    """Simple rounded-corner button implemented on a Canvas."""
    def __init__(self, parent, text="", command=None, radius=10, padding=8,
                 btn_color="#5B93BF", fg="white", hover_color=None, bg=None, font=None, outline_color="#000000",
        outline_width=1, **kwargs):
        bg = bg if bg is not None else (parent.cget("bg") if "bg" in parent.keys() else parent.master.cget("bg"))
        super().__init__(parent, bg=bg, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.radius = radius
        self.padding = padding
        self.btn_color = btn_color
        self.fg = fg
        self.outline_width = max(0, int(outline_width))
        self.outline_color = outline_color if outline_color is not None else self._shade(btn_color, 0.8) if self.outline_width else None
        self.hover_color = hover_color or self._shade(btn_color, 1.08)
        self.font = font or tkfont.Font(family="Verdana", size=10)
        self._pressed = False
        self._create_graphics()
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _create_graphics(self):
        self.delete("all")
        text_w = self.font.measure(self.text)
        text_h = self.font.metrics("linespace")
        width = text_w + (self.padding * 2) + int(self.outline_width * 2)
        height = text_h + int(self.padding * 0.5) + int(self.outline_width * 2)
        self.config(width=width, height=height)

        r = min(self.radius, (height - self.outline_width * 2) // 2, (width - self.outline_width * 2) // 2)
        x0, y0, x1, y1 = 0, 0, width, height

        # Outer (outline) - draw only if outline_width > 0
        if self.outline_width and self.outline_color:
            self._draw_rounded_rect(x0, y0, x1, y1, r, fill=self.outline_color, tags="inner")

        # Inner (button fill) - inset by outline_width
        ix0 = x0 + self.outline_width
        iy0 = y0 + self.outline_width
        ix1 = x1 - self.outline_width
        iy1 = y1 - self.outline_width
        ir = max(0, r - self.outline_width)
        # self._draw_rounded_rect(ix0, iy0, ix1, iy1, r, fill=self.btn_color, tags="inner")

        # center text
        self.create_text(width // 2, height // 2, text=self.text, fill=self.fg, font=self.font, tags="label")

    def _draw_rounded_rect(self, x0, y0, x1, y1, r, fill, tags="rect"):
        """Draw rounded rectangle using rectangles + corner arcs; assign tag to all pieces."""
        # middle rectangles
        self.create_rectangle(x0 + r, y0, x1 - r, y1, fill=fill, outline=fill, tags=(tags,))
        self.create_rectangle(x0, y0 + r, x1, y1 - r, fill=fill, outline=fill, tags=(tags,))
        # corner arcs
        self.create_arc(x0, y0, x0 + 2 * r, y0 + 2 * r, start=90, extent=90, fill=fill, outline=fill, tags=(tags,))
        self.create_arc(x1 - 2 * r, y0, x1, y0 + 2 * r, start=0, extent=90, fill=fill, outline=fill, tags=(tags,))
        self.create_arc(x0, y1 - 2 * r, x0 + 2 * r, y1, start=180, extent=90, fill=fill, outline=fill, tags=(tags,))
        self.create_arc(x1 - 2 * r, y1 - 2 * r, x1, y1, start=270, extent=90, fill=fill, outline=fill, tags=(tags,))

    def _on_press(self, event):
        self._pressed = True
        self.move("label", 0, 1)
        # darken the inner fill on press
        self.itemconfig("inner", fill=self._shade(self.btn_color, 0.92))

    def _on_release(self, event):
        if self._pressed:
            self._pressed = False
            self.move("label", 0, -1)
            self.itemconfig("inner", fill=self.btn_color)
            x, y = event.x, event.y
            if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
                if callable(self.command):
                    self.command()

    def _on_enter(self, _):
        self.itemconfig("inner", fill=self.hover_color)

    def _on_leave(self, _):
        if not self._pressed:
            self.itemconfig("inner", fill=self.btn_color)

    @staticmethod
    def _shade(hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r = min(255, int(int(hex_color[0:2], 16) * factor))
        g = min(255, int(int(hex_color[2:4], 16) * factor))
        b = min(255, int(int(hex_color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"