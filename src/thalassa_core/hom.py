import tkinter as tk
import ttkbootstrap as ttk
from functools import partial

class Homunculus(ttk.Frame):
    def __init__(self, hom_frame):
        super().__init__(hom_frame)

        self.hom_frame = hom_frame
        
        # 1. Logic Data
        self.HOM_TRANSLATIONS = {
            "white": "blue", "yellow": "blue",
            "purple": "green","orange": "green",
            "blue": "red", "red": "red",
            "green": "yellow", "black": "yellow"
        }
        
        self.HOM_SWORD_COLOURS = {}
        self.HOM_DROP_COLOURS = {"blue": 0, "green": 0, "red": 0, "yellow": 0}
        
        self.sword_buttons = {}
        self.drop_labels = {}

        # 2. COLOUR CONFIGURATION
        # Change Hex codes or Text colours here.
        self.COLOUR_CONFIG = {
            "red":    {"hex": "#d9534f", "text": "white"},
            "green":  {"hex": "#5cb85c", "text": "white"},
            "blue":   {"hex": "#0275d8", "text": "white"},
            "yellow": {"hex": "#f0ad4e", "text": "black"},
            "purple": {"hex": "#800080", "text": "white"},
            "orange": {"hex": "#fd7e14", "text": "black"},
            "white":  {"hex": "#ffffff", "text": "black"},
            "black":  {"hex": "#343a40", "text": "white"},
        }

        # 3. Create the Custom Styles based on the config above
        self._configure_styles()

        # 4. Build UI
        self._build_hom_frame()
        self.reset_homu_colours()

    def _configure_styles(self):
        """
        Dynamically generates ttk styles for every colour in COLOUR_CONFIG.
        Creates a Button style (e.g., 'Red.TButton') and a Label style (e.g., 'Red.TLabel').
        """
        style = ttk.Style()
        
        for name, data in self.COLOUR_CONFIG.items():
            bg_colour = data["hex"]
            fg_colour = data["text"]
            
            # Capitalize name for style ID (e.g., "red" -> "Red")
            style_name = name.title() 

            # --- 1. Button Style ---
            # Define the darker shade for when the button is pressed (active)
            active_bg = self._adjust_brightness(bg_colour, 0.8) # 80% brightness

            btn_style = f"{style_name}.TButton"
            style.configure(
                btn_style, 
                background=bg_colour, 
                foreground=fg_colour,
                bordercolour=bg_colour
            )
            # Map dynamic states (hover, pressed)
            style.map(
                btn_style, 
                background=[('active', active_bg), ('pressed', active_bg)],
                foreground=[('active', fg_colour), ('pressed', fg_colour)]
            )

            # --- 2. Label Style (for Drop Totals) ---
            lbl_style = f"{style_name}.TLabel"
            style.configure(
                lbl_style, 
                background=bg_colour, 
                foreground=fg_colour,
                anchor="center"
            )

    def _build_hom_frame(self):
        """Construct the Homunculus Counter Frame UI."""

        # --- Main Content Area ---
        content_frame = ttk.Frame(self.hom_frame)
        content_frame.pack(side="top", expand=True, fill="both", padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1, uniform="group1")
        content_frame.columnconfigure(1, weight=1, uniform="group1")

        # --- Utility Buttons ---
        utility_frame = ttk.Frame(content_frame)
        utility_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Split this cell into 2 equal parts
        utility_frame.columnconfigure(0, weight=1, uniform="group2")
        utility_frame.columnconfigure(1, weight=1, uniform="group2")

        copy_btn = ttk.Button(utility_frame, text="Copy", bootstyle="secondary", command=self._copy_to_clipboard)
        copy_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        reset_btn = ttk.Button(utility_frame, text="Reset", bootstyle="secondary", command=self.reset_homu_colours)
        reset_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        # --- Build Sword Buttons (Left) ---
        sword_container = ttk.Labelframe(content_frame, text="Sword Count", padding=10)
        sword_container.grid(row=1, column=0, sticky="nsew", padx=5)

        for colour in self.HOM_TRANSLATIONS.keys():
            # Use the custom style generated: e.g. "Red.TButton"
            custom_style = f"{colour.title()}.TButton"

            btn = ttk.Button(
                sword_container, 
                text=f"{colour.title()}: 0", 
                style=custom_style,
                width=12,
                command=partial(self._increment_hom, colour, 1) 
            )
            btn.pack(pady=2, padx=5, fill="x")
            
            # Bindings
            btn.bind("<Button-3>", partial(self._on_right_click, colour)) 
            btn.bind("<Button-2>", partial(self._copy_to_clipboard, colour)) 

            self.sword_buttons[colour] = btn

        # --- Build Drop Rectangles (Right) ---
        drop_container = ttk.Labelframe(content_frame, text="Drop Totals", padding=10)
        drop_container.grid(row=1, column=1, sticky="nsew", padx=5)

        for colour in self.HOM_DROP_COLOURS.keys():
            # Use the custom label style: e.g. "Red.TLabel"
            custom_style = f"{colour.title()}.TButton"
            
            lbl = ttk.Button(
                drop_container, 
                text=f"{colour.title()}: 0", 
                style=custom_style,
                width=12
            )
            lbl.pack(pady=2, padx=5, fill="x")
            
            self.drop_labels[colour] = lbl

    def _adjust_brightness(self, hex_colour, factor):
        """ Helper to darken a hex colour for the 'active' button state """
        hex_colour = hex_colour.lstrip('#')
        # Convert to RGB
        r, g, b = tuple(int(hex_colour[i:i+2], 16) for i in (0, 2, 4))
        # Dim values
        r = int(max(0, min(255, r * factor)))
        g = int(max(0, min(255, g * factor)))
        b = int(max(0, min(255, b * factor)))
        # Return Hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _on_right_click(self, colour, event):
        self._increment_hom(colour, -1)


    def _increment_hom(self, colour: str, amount: int):
        current_val = self.HOM_SWORD_COLOURS.get(colour, 0)
        
        if current_val + amount < 0:
            return

        self.HOM_SWORD_COLOURS[colour] += amount
        
        true_colour = self._translate_hom_colour(colour)
        self.HOM_DROP_COLOURS[true_colour] += amount

        self._update_ui()

    def reset_homu_colours(self):
        self.HOM_SWORD_COLOURS = {k: 0 for k in self.HOM_TRANSLATIONS.keys()}
        self.HOM_DROP_COLOURS = {k: 0 for k in self.HOM_DROP_COLOURS.keys()}
        
        if hasattr(self, 'sword_buttons'):
            self._update_ui()

    def _update_ui(self):
        for colour, count in self.HOM_SWORD_COLOURS.items():
            self.sword_buttons[colour].config(text=f"{colour.title()}: {count}")
            
        for colour, count in self.HOM_DROP_COLOURS.items():
            self.drop_labels[colour].config(text=f"{colour.title()}: {count}")

    def _translate_hom_colour(self, colour: str):
        return self.HOM_TRANSLATIONS[colour]

    def _copy_to_clipboard(self, target: str=None, event=None):
        if target != None:
            target_true = self._translate_hom_colour(target)
        else:
            target_true = None
        hom_count = "/ve Homunculus Count:"
        sorted_hom_colours = dict(sorted(self.HOM_DROP_COLOURS.items(), key=lambda item: item[1], reverse=True))
        for colour in sorted_hom_colours:
            count = sorted_hom_colours[colour]
            if count > 0:
                hom_count += f"\n{count} {colour.capitalize()}"
                if target_true == colour:
                    hom_count += " <-- attacking"
        self.hom_frame.clipboard_clear()
        self.hom_frame.clipboard_append(hom_count)
        

if __name__ == "__main__":
    # Initialize with a basic theme, but custom styles will override the buttons
    root = ttk.Window(themename="litera") 
    root.title("Homunculus Counter")
    
    app = Homunculus(root)
    app.pack(fill="both", expand=True)
    
    root.mainloop()