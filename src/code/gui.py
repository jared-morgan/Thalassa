# ...existing code...
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class GUI:
    def __init__(self, title="Pirate Helper", size=(300, 600)):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{size[0]}x{size[1]}")

        # --- Background / style configuration ---
        # example colours from your notes
        dark_bg = "#2C5F7A"     # Dark blue, background
        light_bg = "#a9b9c1"    # Light blue, background
        tab_bg = "#b5b79e"      # Grey, tab backgorund
        text_dark = "#000000"      # Black, text
        text_light = "#D7C94F"      # Yellow, tab text
        button_colour = "#5B93BF"  # Blue, button background


        # Gizmo
        # background Blue (44, 95, 122)
        # button blue (91, 147, 191)
        # text button yellow (215, 201, 79)
        # text shadow (74, 93, 132)
        # boxes (125, 144, 148)

        # set root window background
        self.root.configure(bg=dark_bg)

        # create a ttk style and prefer a theme that allows colour overrides
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            # if 'clam' isn't available, keep the default theme
            pass

        # style a custom frame used for notebook pages
        style.configure("My.TFrame", background=dark_bg)
        # style the notebook background and tabs
        
        tab_font = ("Verdana", 11)
        style.configure("TNotebook", background=dark_bg)
        style.configure("TNotebook.Tab", background=tab_bg, foreground=text_dark, font=tab_font)
        # style the button background and text

        button_font = ("Verdana", 10)
        style.configure("TButton", background=button_colour, foreground=text_light, font=button_font)


        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Create three tabs
        self.tabs = {}
        for name in ("Options", "Chats", "Main"):
            # use the styled frame so its background matches the root
            frame = ttk.Frame(self.notebook, style="My.TFrame")
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame

        # Add a simple button to the Options tab
        options_frame = self.tabs["Options"]
        self.options_button = ttk.Button(
            options_frame,
            text="Save Prefs",
            command=self.on_save_settings
        )
        self.options_button.pack(pady=8, padx=8)

        # --- Dropdown (Combobox) example ---
        # variable that holds the selected value
        self.option_var = tk.StringVar(value="Cursed Isles")

        # # label for the dropdown
        # ttk.Label(options_frame, text="Difficulty:").pack(anchor="w", padx=8, pady=(12, 0))

        # readonly combobox (dropdown)
        self.option_combo = ttk.Combobox(
            options_frame,
            textvariable=self.option_var,
            values=["Cused Isles", "Vampire Lair", "Werwolf Den", "Evading", "MAA", "Greedy Pillage", "Kraken Hunt"],
            state="readonly",
            width=12,
        )
        self.option_combo.pack(anchor="w", padx=8, pady=4)
        # optional: run callback when selection changes
        self.option_combo.bind("<<ComboboxSelected>>", self.on_dropdown_change)

        # --- Checkbox example ---
        self.chat_filter_var = tk.BooleanVar(value=True)
        self.chat_filter_cb = ttk.Checkbutton(
            options_frame,
            text="Chat Filters On",
            variable=self.chat_filter_var,
            onvalue=True,
            offvalue=False
        )
        self.chat_filter_cb.pack(anchor="w", padx=8, pady=(6, 12))

        # --- Checkbox example ---
        self.mini_rumble_var = tk.BooleanVar(value=True)
        self.mini_rumble_cb = ttk.Checkbutton(
            options_frame,
            text="Show Table",
            variable=self.mini_rumble_var,
            onvalue=False,
            offvalue=True
        )
        self.mini_rumble_cb.pack(anchor="w", padx=8, pady=(6, 12))

        # --- Checkbox example ---
        self.rumble_bars_as_natural_width_var = tk.BooleanVar(value=True)
        self.rumble_bars_as_natural_width_cb = ttk.Checkbutton(
            options_frame,
            text="Bars As Natural Width",
            variable=self.rumble_bars_as_natural_width_var,
            onvalue=True,
            offvalue=False
        )
        self.rumble_bars_as_natural_width_cb.pack(anchor="w", padx=8, pady=(6, 12))

        # --- Checkbox example ---
        self.show_drop_off_numbers_var = tk.BooleanVar(value=True)
        self.show_drop_off_numbers_cb = ttk.Checkbutton(
            options_frame,
            text="Show Drop-off Required",
            variable=self.show_drop_off_numbers_var,
            onvalue=True,
            offvalue=False
        )
        self.show_drop_off_numbers_cb.pack(anchor="w", padx=8, pady=(6, 12))

        # readonly combobox (dropdown)
        ttk.Label(options_frame, text="Timer Decimals:").pack(anchor="w", padx=8, pady=(4, 0))
        self.timer_decimals_var = tk.StringVar(value="1")
        self.timer_decimals_combo = ttk.Combobox(
            options_frame,
            textvariable=self.timer_decimals_var,
            values=["0", "1", "2"],
            state="readonly",
            width=4,
        )
        self.timer_decimals_combo.pack(anchor="w", padx=8, pady=4)
        # optional: run callback when selection changes
        self.timer_decimals_combo.bind("<<ComboboxSelected>>", self.on_dropdown_change)
        
        # --- Checkbox example ---
        self.swabbie_warning_sound_var = tk.BooleanVar(value=True)
        self.swabbie_warning_sound_cb = ttk.Checkbutton(
            options_frame,
            text="Play Swabbie Warning Sound",
            variable=self.swabbie_warning_sound_var,
            onvalue=True,
            offvalue=False
        )
        self.swabbie_warning_sound_cb.pack(anchor="w", padx=8, pady=(6, 0))


        # --- Text entry (typeable box) ---
        self.timer_offset_var = tk.StringVar(value="0000")
        ttk.Label(options_frame, text="Timer Offset (ms):").pack(anchor="w", padx=8, pady=(4, 0))
        # register integer validation (allows empty, optional +/-, and digits)
        int_vcmd = (self.root.register(self._validate_integer), "%P")
        self.timer_offset_text_entry = ttk.Entry(
            options_frame,
            textvariable=self.timer_offset_var,
            width=6,
            validate="key",
            validatecommand=int_vcmd,
        )
        self.timer_offset_text_entry.pack(anchor="w", padx=8, pady=(2, 8))

        # self.rumble_scaling = 12 # Idk if I should expose this yet.


    def _validate_integer(self, proposed: str) -> bool:
        """Return True if proposed text is a valid integer input (or empty)."""
        if proposed == "":
            return True
        if proposed in ("+", "-"):
            return True
        try:
            int(proposed)
            return True
        except ValueError:
            return False
        
    
    def edit_chat_filter(self, filter_id=None):
        """Edit a chat filter."""
        if filter_id is None:
            filter_id = self.create_chat_filter()
        chat_filter = self.chat_filters[filter_id]

        # "name": "Buying CI map", "channel": "trade", "buy_or_sell": "buy", "strings": ["ci map", "cursed island", "cursed isles", "ci of", "ci near"], "regex": "", "sound": "trade_chat_sound.ogg"},

    
    def create_chat_filter(self):
        """Create a new chat filter."""
        chat_filter = {
            "name": "New Filter",
            "channel": "trade",
            "buy_or_sell": "buy",
            "strings": [""],
            "regex": "",
            "sound": "trade_chat_sound.ogg"}
        self.chat_filters.append(chat_filter)
        return len(self.chat_filters) - 1


    def select_tab(self, name_or_index):
        """Select a tab by name or index."""
        if isinstance(name_or_index, int):
            self.notebook.select(name_or_index)
        else:
            for i, tab_name in enumerate(self.tabs):
                if tab_name == name_or_index:
                    self.notebook.select(i)
                    return
                
    def on_save_settings(self):
        """Callback for the Options tab button (replace with real logic)."""
        print("Save Settings")

    def on_dropdown_change(self, event=None):
        # called when user selects an item from the combobox
        print("Dropdown changed:", self.option_var.get())

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()