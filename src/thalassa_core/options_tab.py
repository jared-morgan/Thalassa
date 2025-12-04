import tkinter as tk 
import ttkbootstrap as ttk
from tkinter import filedialog
from pathlib import Path
from platformdirs import user_data_dir
import os

def find_default_log_dir():
    """Checks for the default log directory for puzzle pirates."""
    #TODO: Check Steam paths as well
    home = Path.home()
    platformdirs_path = Path(user_data_dir("Puzzle Pirates", appauthor="Three Rings Design"))

    possible_paths = [
        Path(os.getenv("APPDATA", "")) / "Three Rings Design" / "Puzzle Pirates",
        Path(os.getenv("LOCALAPPDATA", "")) / "Puzzle Pirates",
        home / "Library" / "Application Support" / "Three Rings Design" / "Puzzle Pirates",
        home / ".local" / "share" / "Three Rings Design" / "Puzzle Pirates",
        platformdirs_path,
    ]

    possible_paths = [p for p in possible_paths if str(p).strip()]

    for p in possible_paths:
        if p.exists():
            for file in p.iterdir():
                if file.name.endswith(".log"):
                    print("Found:", p)
                    return p

    print("Puzzle Pirates folder not found")
    return None


def find_default_chatlog_dir():
    """Checks for the default chatlog directory for puzzle pirates."""
    # TODO: What common paths do other people use?
    home = Path.home()
    chatlog_path = home / "Documents" / "YPP_Chatlogs"
    if chatlog_path.exists():
        print("Found chatlogs:", chatlog_path)
        return chatlog_path
    print("Chatlogs folder not found")
    return None


class PathPickerWidget(ttk.Frame):
    """Reusable widget for selecting file paths."""
    def __init__(self, parent, label_text, initial_dir, callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.path_var = tk.StringVar(value=str(initial_dir))

        self.callback = callback
        
        # Header with label and browse button
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=5, fill="x")
        
        ttk.Label(header_frame, text=label_text).pack(side="left")
        ttk.Button(header_frame, text="Browse", command=self._browse).pack(side="right")
        
        # Entry with scrollbar
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=5, fill="x")
        
        scrollbar = ttk.Scrollbar(entry_frame, orient="horizontal")
        scrollbar.pack(side="bottom", fill="x")
        
        self.entry = ttk.Entry(entry_frame, textvariable=self.path_var, state="readonly", xscrollcommand=scrollbar.set)
        self.entry.pack(side="top", fill="x")
        scrollbar.config(command=self.entry.xview)
    
    def _browse(self):
        selected_dir = filedialog.askdirectory(title=f"Select Directory", initialdir=str(self.path_var.get()))
        if selected_dir:
            self.path_var.set(selected_dir)
            if self.callback:  # call the function with the new path
                self.callback(selected_dir)
    
    def get(self):
        return self.path_var.get()
    

class OptionsTab(ttk.Frame):
    def __init__(self, options_frame: ttk.Frame, configs, event_callback):
        super().__init__(options_frame)
        self.configs = configs
        self.options_frame = options_frame
        self.event_callback = event_callback
        

        self._setup_options_tab()

    
    def _emit(self, func, *args, **kwargs):
        self.event_callback(func, *args, **kwargs)
    
    def _setup_options_tab(self):

        if self.configs.log_dir == None:
            self.configs.log_dir = find_default_log_dir()
        if self.configs.log_dir != None:
            self._emit("update_log_path", Path(self.configs.log_dir))

        if self.configs.chatlog_dir == None:
            self.configs.chatlog_dir = find_default_chatlog_dir()
        if self.configs.chatlog_dir != None:
            self._emit("update_chatlog_path", Path(self.configs.chatlog_dir))
        

        # Path pickers
        self.log_picker = PathPickerWidget(
            self.options_frame,
            "Logs path",
            Path(self.configs.log_dir),
            callback=lambda new_path: self._emit("update_log_path", Path(new_path))
        )
        self.log_picker.pack(padx=10, fill="x")
        
        self.chatlog_picker = PathPickerWidget(
            self.options_frame,
            "Chatlogs path",
            Path(self.configs.chatlog_dir),
            callback=lambda new_path: self._emit("update_chatlog_path", Path(new_path))
        )
        self.chatlog_picker.pack(padx=10, fill="x")

        
        row = ttk.Frame(self.options_frame)
        row.pack(fill="x", pady=5)
        self.specific_pirate_var = tk.StringVar(value=self.configs.specific_pirate)
        specific_pirate_label = ttk.Label(row, text="Specific Pirate")
        specific_pirate_entry = ttk.Entry(row, textvariable=self.specific_pirate_var)

        specific_pirate_label.pack(side="left")
        specific_pirate_entry.pack(side="left", fill="x", expand=True)

        self.specific_pirate_var.trace_add("write", lambda *args:
            setattr(self.configs, "specific_pirate", self.specific_pirate_var.get()))

        # Horizontal line (separator)
        separator = ttk.Separator(self.options_frame, orient="horizontal")
        separator.pack(fill="x", pady=5)

        # Mode dropdown
        mode_frame = ttk.Frame(self.options_frame)
        mode_frame.pack(pady=10, padx=10, fill="x")
        ttk.Label(mode_frame, text="Mode").pack(side="left")
        self.mode_var = tk.StringVar(value=self.configs.selected_mode)

        #TODO: Complete missing options
        mode_options = [
            "Cursed Isles",
            "Vampire Lair",
            # "Werewolf Den",
            # "Evading",
            # "MAA",
            # "Pillage",
            # "Kraken Hunt",
            # "Automatic"
        ]
        
        mode_dropdown = ttk.Combobox(mode_frame, textvariable=self.mode_var, values=mode_options, state="readonly")
        mode_dropdown.pack(side="right", fill="x", expand=True, padx=(10, 0))
        # Bind onchange event so we can refresh GUI of mode tab
        mode_dropdown.bind("<<ComboboxSelected>>", lambda e: self._emit("setup_mode_tab"))
        self.mode_var.trace_add("write", lambda *args: setattr(self.configs, 'selected_mode', self.mode_var.get()))
        
        # Horizontal line (separator)
        separator = ttk.Separator(self.options_frame, orient="horizontal")
        separator.pack(fill="x", pady=5)


        # Rumble Settings
        rumble_settings_frame = ttk.Frame(self.options_frame)
        rumble_settings_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(rumble_settings_frame, text="Rumble Settings").pack(side="top", anchor="w", pady=(0, 5))

        # Mini Rumble Display Checkbox
        self.rumble_mini_var = tk.BooleanVar(value=self.configs.rumble_mini)
        mini_rumble_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Mini Rumble Display",
            variable=self.rumble_mini_var
        )
        mini_rumble_check.pack(side="top", anchor="w")
        self.rumble_mini_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_mini', self.rumble_mini_var.get()))

        # Bars as Natural Width Checkbox
        self.rumble_bars_natural_width_var = tk.BooleanVar(value=self.configs.rumble_bars_natural_width)
        bars_natural_width_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Rumble Bars as Natural Width",
            variable=self.rumble_bars_natural_width_var
        )
        bars_natural_width_check.pack(side="top", anchor="w")
        self.rumble_bars_natural_width_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_bars_natural_width', self.rumble_bars_natural_width_var.get()))

        # Show Drop-off Numbers Checkbox
        self.rumble_show_drop_off_var = tk.BooleanVar(value=self.configs.rumble_show_drop_off)
        show_drop_off_numbers_check = ttk.Checkbutton(  
            rumble_settings_frame,
            text="Show Drop-off Numbers",
            variable=self.rumble_show_drop_off_var
        )
        show_drop_off_numbers_check.pack(side="top", anchor="w")
        self.rumble_show_drop_off_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_show_drop_off', self.rumble_show_drop_off_var.get()))

        # --- Rumble Warning Sound Checkbox ---
        self.play_rumble_warning_sound_var = tk.BooleanVar(value=self.configs.rumble_play_warning_sound)
        warning_sound_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Play Warning Sound",
            variable=self.play_rumble_warning_sound_var
        )
        warning_sound_check.pack(side="top", anchor="w", pady=(10, 0))
        self.play_rumble_warning_sound_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_play_warning_sound', self.play_rumble_warning_sound_var.get()))

        # --- Rumble Warning Sound Lead (s) ---
        sound_lead_frame = ttk.Frame(rumble_settings_frame)
        sound_lead_frame.pack(side="top", anchor="w", pady=(2, 0))
        
        ttk.Label(sound_lead_frame, text="Warning Time (s):").pack(side="left")
        
        self.rumble_warning_lead_var = tk.IntVar(value=self.configs.rumble_warning_lead)
        sound_lead_entry = ttk.Entry(
            sound_lead_frame, 
            textvariable=self.rumble_warning_lead_var, 
            width=10
        )
        sound_lead_entry.pack(side="left", padx=(5, 0))
        self.rumble_warning_lead_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_warning_lead', self.rumble_warning_lead_var.get()))

        # --- Rumble Red Text Checkbox ---
        self.rumble_warning_text_var = tk.BooleanVar(value=self.configs.rumble_warning_colour)
        red_text_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Turn Text Red on Warning",
            variable=self.rumble_warning_text_var
        )
        red_text_check.pack(side="top", anchor="w", pady=(10, 0))
        self.rumble_warning_text_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_warning_colour', self.rumble_warning_text_var.get()))

        # --- Warning Sound File Selection ---
        ttk.Label(rumble_settings_frame, text="Warning Sound File:").pack(side="top", anchor="w", pady=(10, 0))
        
        file_select_frame = ttk.Frame(rumble_settings_frame)
        file_select_frame.pack(side="top", fill="x", anchor="w")

        self.rumble_sound_file_var = tk.StringVar(value=self.configs.rumble_warning_sound)
        
        sound_file_entry = ttk.Entry(
            file_select_frame, 
            textvariable=self.rumble_sound_file_var
        )
        sound_file_entry.pack(side="left", fill="x", expand=True)

        browse_btn = ttk.Button(file_select_frame, text="Browse", command=self.browse_sound_file)
        browse_btn.pack(side="left", padx=(5, 0))
        
        self.rumble_sound_file_var.trace_add("write", lambda *args: setattr(self.configs, 'rumble_warning_sound', self.rumble_sound_file_var.get()))

        
        # Horizontal line (separator)
        separator = ttk.Separator(self.options_frame, orient="horizontal")
        separator.pack(fill="x", pady=5)
    
    def browse_sound_file(self):
        # Determine initial directory (OS safe)
        # Assuming script is running from root, constructs ./src/media
        start_dir = os.path.join(os.getcwd(), "src", "media", "sounds")
        if not os.path.exists(start_dir):
            start_dir = os.getcwd() # Fallback if path doesn't exist

        filename = filedialog.askopenfilename(
            initialdir=start_dir,
            title="Select Warning Sound",
            filetypes=[("Audio Files", "*.ogg *.wav *.mp3"), ("All Files", "*.*")]
        )
        
        if filename:
            # Store only the filename if you want relative path, or full path if preferred
            # Here we take the basename to match the comment example "warning.ogg"
            self.rumble_sound_file_var.set(os.path.basename(filename))
            # If you need the full path, use: self.rumble_sound_file_var.set(filename)