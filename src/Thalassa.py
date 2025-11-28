import tkinter as tk 
import ttkbootstrap as ttk
from pathlib import Path
from platformdirs import user_data_dir
from tkinter import filedialog
import os

from code.configs import Configs, SearchEntry
from code.log_parser import LogParser
from code.cursed_isles import CursedIsles

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
    return ""


def find_default_chatlog_dir():
    """Checks for the default chatlog directory for puzzle pirates."""
    # TODO: What common paths do other people use?
    home = Path.home()
    chatlog_path = home / "Documents" / "YPP_Chatlogs"
    if chatlog_path.exists():
        print("Found chatlogs:", chatlog_path)
        return chatlog_path
    print("Chatlogs folder not found")
    return ""


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


class FiltersTab:
    def __init__(self, parent, search_strings):
        self.search_strings = search_strings
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)
        
        self.filter_frames = {}  # Keeps track of UI Frames
        self.filter_vars = {}    # Keeps track of TK Variables (prevents GC, avoids Pickle)

        # Create initial filters
        for number, settings in self.search_strings.items():
            self.create_filter_widgets(self.frame, settings, number)

        # Add button to create new filter
        add_btn = ttk.Button(self.frame, text="Add New Filter", command=self.add_new_filter)
        add_btn.pack(side="bottom", pady=10)

    def create_filter_widgets(self, parent, settings, number):
        entry_frame = ttk.Frame(parent, relief="groove", padding=5)
        entry_frame.pack(fill="x", pady=5)
        self.filter_frames[number] = entry_frame

        # Create a dictionary to hold ALL Tk vars for this specific filter
        # We store this in self.filter_vars so it doesn't get garbage collected
        # But we do NOT put it in 'settings', so pickle stays safe.
        gui_vars = {}
        self.filter_vars[number] = gui_vars

        # --- Header ---
        header_frame = ttk.Frame(entry_frame)
        header_frame.pack(fill="x")

        # Name Variable
        gui_vars['name'] = tk.StringVar(value=settings.name)
        # Sync: When GUI changes -> Update Settings Object
        gui_vars['name'].trace_add("write", lambda *a: setattr(settings, 'name', gui_vars['name'].get()))

        # Editable name label
        name_label = ttk.Label(header_frame, textvariable=gui_vars['name'], font=("TkDefaultFont", 10, "bold"))
        name_label.pack(side="left")

        def edit_name(event=None):
            name_entry = ttk.Entry(header_frame, textvariable=gui_vars['name'], font=("TkDefaultFont", 10, "bold"))
            name_label.pack_forget()
            name_entry.pack(side="left")
            name_entry.focus()

            def finish_edit(event=None):
                name_entry.pack_forget()
                name_label.pack(side="left")
            
            name_entry.bind("<Return>", finish_edit)
            name_entry.bind("<FocusOut>", finish_edit)

        name_label.bind("<Button-1>", edit_name)

        expand_btn = ttk.Button(header_frame, text="Expand", width=8)
        expand_btn.pack(side="right")

        # --- Inline Checkbuttons ---
        inline_frame = ttk.Frame(entry_frame)
        inline_frame.pack(fill="x", pady=2)

        gui_vars['on'] = tk.BooleanVar(value=settings.on_off)
        gui_vars['muted'] = tk.BooleanVar(value=settings.muted)

        # Sync checkboxes
        gui_vars['on'].trace_add("write", lambda *a: setattr(settings, 'on_off', gui_vars['on'].get()))
        gui_vars['muted'].trace_add("write", lambda *a: setattr(settings, 'muted', gui_vars['muted'].get()))

        ttk.Checkbutton(inline_frame, text="On", variable=gui_vars['on']).pack(side="left", padx=5)
        ttk.Checkbutton(inline_frame, text="Muted", variable=gui_vars['muted']).pack(side="left", padx=5)

        # --- Advanced Frame ---
        advanced_frame = ttk.Frame(entry_frame)
        advanced_frame.pack_forget() 

        # 1. Channel
        ttk.Label(advanced_frame, text="Channel:").pack(anchor="w")
        gui_vars['channel'] = tk.StringVar(value=settings.channel)
        gui_vars['channel'].trace_add("write", lambda *a: setattr(settings, 'channel', gui_vars['channel'].get()))
        
        channel_entry = ttk.Entry(advanced_frame, textvariable=gui_vars['channel'])
        channel_entry.pack(fill="x", pady=2)

        # 2. Buy/Sell
        gui_vars['buy_sell'] = tk.StringVar(value=settings.buy_or_sell)
        gui_vars['buy_sell'].trace_add("write", lambda *a: setattr(settings, 'buy_or_sell', gui_vars['buy_sell'].get()))

        buy_sell_frame = ttk.Frame(advanced_frame)
        buy_sell_frame.pack(fill="x")
        buy_sell_options = ["Buy", "Sell", "Any"]
        buy_sell_dropdown = ttk.Combobox(buy_sell_frame, textvariable=gui_vars['buy_sell'], values=buy_sell_options, state="readonly")
        buy_sell_dropdown.pack_forget()

        # 3. Strings & Regex
        string_regex_frame = ttk.Frame(advanced_frame)
        
        gui_vars['search_type'] = tk.StringVar(value=settings.string_or_regex)
        gui_vars['search_type'].trace_add("write", lambda *a: setattr(settings, 'string_or_regex', gui_vars['search_type'].get()))

        string_regex_options = ["Strings", "Regex"]
        string_regex_dropdown = ttk.Combobox(string_regex_frame, textvariable=gui_vars['search_type'], values=string_regex_options, state="readonly")
        
        ttk.Label(string_regex_frame, text="Search Using:").pack(anchor="w", pady=2)
        
        # Text widgets don't use StringVar, so we don't put them in gui_vars.
        # We bind directly to KeyRelease to update settings.
        strings_text = tk.Text(string_regex_frame, height=3)
        strings_text.insert("1.0", settings.strings)
        strings_text.bind("<KeyRelease>", lambda e: setattr(settings, 'strings', strings_text.get("1.0", "end-1c")))

        regex_text = tk.Text(string_regex_frame, height=3)
        regex_text.insert("1.0", settings.regex)
        regex_text.bind("<KeyRelease>", lambda e: setattr(settings, 'regex', regex_text.get("1.0", "end-1c")))

        string_regex_frame.pack(fill="x", pady=2)
        string_regex_dropdown.pack(anchor="w", pady=2)

        # 4. Sound
        ttk.Label(advanced_frame, text="Sound:").pack(anchor="w")
        gui_vars['sound'] = tk.StringVar(value=settings.sound)
        gui_vars['sound'].trace_add("write", lambda *a: setattr(settings, 'sound', gui_vars['sound'].get()))

        sound_frame = ttk.Frame(advanced_frame)
        sound_frame.pack(fill="x", pady=2)
        ttk.Entry(sound_frame, textvariable=gui_vars['sound']).pack(side="left", fill="x", expand=True)
        ttk.Button(sound_frame, text="Browse", command=lambda: self.browse_sound(gui_vars['sound'])).pack(side="left", padx=5)

        # --- Logic Functions ---

        def toggle_advanced():
            if advanced_frame.winfo_ismapped():
                advanced_frame.pack_forget()
                expand_btn.config(text="Expand")
            else:
                advanced_frame.pack(fill="x", padx=0, pady=2, anchor="nw")
                expand_btn.config(text="Collapse")
                update_buy_sell()

        expand_btn.config(command=toggle_advanced)

        def update_buy_sell(*args):
            if gui_vars['channel'].get().strip().lower() == "trade":
                if not buy_sell_dropdown.winfo_ismapped():
                    buy_sell_dropdown.pack(anchor="w")
            else:
                buy_sell_dropdown.pack_forget()

        def update_string_regex(*args):
            if gui_vars['search_type'].get() == "Strings":
                strings_text.pack(fill="x", pady=2)
                regex_text.pack_forget()
            else:
                strings_text.pack_forget()
                regex_text.pack(fill="x", pady=2)

        # Trace the variables for UI Updates (show/hide fields)
        gui_vars['search_type'].trace_add("write", update_string_regex)
        gui_vars['channel'].trace_add("write", update_buy_sell)
        
        # Initial calls
        update_string_regex()
        update_buy_sell()

        if getattr(settings, "is_new", False):
            toggle_advanced()
            del settings.is_new 

        # --- Delete Logic ---
        frame_to_delete = entry_frame
        num_to_delete = number

        def delete_filter():
            frame_to_delete.destroy()
            
            # Remove from data model
            if num_to_delete in self.search_strings:
                del self.search_strings[num_to_delete]
            
            # Remove frames
            if num_to_delete in self.filter_frames:
                del self.filter_frames[num_to_delete]
            
            # Remove variables (clean up memory)
            if num_to_delete in self.filter_vars:
                del self.filter_vars[num_to_delete]

            # Fix Scroll Region
            try:
                widget = parent
                while widget and not isinstance(widget, tk.Canvas):
                    widget = widget.master
                if isinstance(widget, tk.Canvas):
                    widget.update_idletasks()
                    widget.configure(scrollregion=widget.bbox("all"))
            except Exception as e:
                print(f"Error updating scroll region: {e}")

        ttk.Button(advanced_frame, text="Delete Filter", command=delete_filter).pack(pady=5)

        return entry_frame

    def browse_sound(self, string_var):
        filename = filedialog.askopenfilename()
        if filename:
            string_var.set(filename)

    def add_new_filter(self):
        new_number = max(self.search_strings.keys(), default=0) + 1
        # Create your settings object (ensure SearchEntry is imported)
        settings = SearchEntry(name=f"Filter {new_number}") 
        settings.is_new = True 
        self.search_strings[new_number] = settings
        self.create_filter_widgets(self.frame, settings, new_number)


class ThalassaGUI:
    def __init__(self, configs):
        self.configs = configs
        self.log_parser = LogParser(event_callback=self.handle_log_event)
        self.window = ttk.Window(themename="darkly")
        self.window.title("Thalassa")
        self.window.geometry(f"{self.configs.window_width}x{self.configs.window_height}+{self.configs.window_x}+{self.configs.window_y}")
        
        # Save window position/size on close
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True)

        self.mode_content = None
        
        self.tabs = {}
        self._create_tabs()

        self._scan_files()

    def _on_closing(self):
        # Save GUI state
        self.configs.window_width = self.window.winfo_width()
        self.configs.window_height = self.window.winfo_height()
        self.configs.window_x = self.window.winfo_x()
        self.configs.window_y = self.window.winfo_y()
        self.configs.selected_mode = self.mode_var.get()
        self.configs.logs_path = self.log_picker.get()
        self.configs.chatlogs_path = self.chatlog_picker.get()
        
        # Save to file
        self.configs.save_configs()
        self.window.destroy()
    
    def _create_tabs(self):
        for name in ("Mode", "Chats", "Options"):
            frame = ttk.Frame(self.notebook, style="My.TFrame")
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame
        
        self._setup_options_tab()
        self._setup_chats_tab()
        self._setup_mode_tab()
        
    
    def _setup_options_tab(self):
        options_frame = self.tabs["Options"]

        if self.configs.log_dir == None:
            self.configs.log_dir = find_default_log_dir()
        self.log_parser.update_log_path(self.configs.log_dir)

        if self.configs.chatlog_dir == None:
            self.configs.chatlog_dir = find_default_chatlog_dir()
        # self.log_parser.update_chatlog_path(self.configs.chatlog_dir) # TODO: Write this func
        

        # Path pickers
        self.log_picker = PathPickerWidget(
            options_frame,
            "Logs path",
            self.configs.log_dir,
            callback=self.log_parser.update_log_path
        )
        self.log_picker.pack(padx=10, fill="x")
        
        self.chatlog_picker = PathPickerWidget(
            options_frame,
            "Chatlogs path",
            self.configs.chatlog_dir,
            # callback=self.log_parser.update_log_path #TODO: Write this func
        )
        self.chatlog_picker.pack(padx=10, fill="x")

        
        row = ttk.Frame(options_frame)
        row.pack(fill="x", pady=5)
        self.specific_pirate_var = tk.StringVar(value=self.configs.specific_pirate)
        specific_pirate_label = ttk.Label(row, text="Specific Pirate")
        specific_pirate_entry = ttk.Entry(row, textvariable=self.specific_pirate_var)

        specific_pirate_label.pack(side="left")
        specific_pirate_entry.pack(side="left", fill="x", expand=True)

        self.specific_pirate_var.trace_add("write", lambda *args:
            setattr(self.configs, "specific_pirate", self.specific_pirate_var.get()))

        # Horizontal line (separator)
        separator = ttk.Separator(options_frame, orient="horizontal")
        separator.pack(fill="x", pady=5)

        # Mode dropdown
        mode_frame = ttk.Frame(options_frame)
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
        mode_dropdown.bind("<<ComboboxSelected>>", self._setup_mode_tab)

        
        # Horizontal line (separator)
        separator = ttk.Separator(options_frame, orient="horizontal")
        separator.pack(fill="x", pady=5)


        # Rumble Settings
        rumble_settings_frame = ttk.Frame(options_frame)
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

        # Bars as Natural Width Checkbox
        self.rumble_bars_natural_width_var = tk.BooleanVar(value=self.configs.rumble_bars_natural_width)
        bars_natural_width_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Rumble Bars as Natural Width",
            variable=self.rumble_bars_natural_width_var
        )
        bars_natural_width_check.pack(side="top", anchor="w")

        # Show Drop-off Numbers Checkbox
        self.rumble_show_drop_off_var = tk.BooleanVar(value=self.configs.rumble_show_drop_off)
        show_drop_off_numbers_check = ttk.Checkbutton(  
            rumble_settings_frame,
            text="Show Drop-off Numbers",
            variable=self.rumble_show_drop_off_var
        )
        show_drop_off_numbers_check.pack(side="top", anchor="w")

        # --- Rumble Warning Sound Checkbox ---
        self.play_rumble_warning_sound_var = tk.BooleanVar(value=self.configs.rumble_play_warning_sound)
        warning_sound_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Play Warning Sound",
            variable=self.play_rumble_warning_sound_var
        )
        warning_sound_check.pack(side="top", anchor="w", pady=(10, 0))

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

        # --- Rumble Red Text Checkbox ---
        self.rumble_warning_text_var = tk.BooleanVar(value=self.configs.rumble_warning_colour)
        red_text_check = ttk.Checkbutton(
            rumble_settings_frame,
            text="Turn Text Red on Warning",
            variable=self.rumble_warning_text_var
        )
        red_text_check.pack(side="top", anchor="w", pady=(10, 0))

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

        
        # Horizontal line (separator)
        separator = ttk.Separator(options_frame, orient="horizontal")
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

    def _setup_chats_tab(self):
        chats_frame = self.tabs["Chats"]

        # Global Mute button
        self.chats_mute_var = tk.BooleanVar(value=bool(self.configs.chat_mute))
        chats_mute_check = ttk.Checkbutton(
            chats_frame,
            text="Mute All Chats",
            variable=self.chats_mute_var
        )
        self.chats_mute_var.trace_add("write", lambda *args: setattr(self.configs, 'chat_mute', self.chats_mute_var.get()))
        chats_mute_check.pack(side="top", anchor="w", pady=2)

        # Global Off button
        self.chats_off_var = tk.BooleanVar(value=bool(self.configs.chat_filter_off))
        chats_off_check = ttk.Checkbutton(
            chats_frame,
            text="All Chats Off",
            variable=self.chats_off_var
        )
        self.chats_off_var.trace_add("write", lambda *args: setattr(self.configs, 'chat_filter_off', self.chats_off_var.get()))
        chats_off_check.pack(side="top", anchor="w", pady=2)

        # Create a Notebook for subtabs inside the Chats frame
        chats_sub_notebook = ttk.Notebook(chats_frame)
        chats_sub_notebook.pack(fill="both", expand=True, pady=5)

        # Add subtabs
        for name in ("Output", "Filters"):
            sub_frame = ttk.Frame(chats_sub_notebook, style="My.TFrame")
            chats_sub_notebook.add(sub_frame, text=name)
            self.tabs[name] = sub_frame

        # Populate the Filters tab
        filters_frame = self.tabs["Filters"]

        # Create a scrollable frame
        scrollable = ScrollableFrame(filters_frame)
        scrollable.pack(fill="both", expand=True)

        # Pass the inner frame to your FiltersTab
        FiltersTab(scrollable.scroll_frame, self.configs.search_strings)

    def _setup_mode_tab(self, event=None):
        mode_frame = self.tabs["Mode"]
        if self.mode_content is None:
            self.mode_content = ttk.Frame(mode_frame)
            self.mode_content.pack(fill="both", expand=True)

        # Clear the mode_frame ready for new child frame
        for widget in self.mode_content.winfo_children():
            widget.destroy()

        self.configs.selected_mode = self.mode_var.get()

        if self.configs.selected_mode == "Cursed Isles":
            self.current_mode_frame = CursedIsles(self.mode_content, self.configs)
            self.current_mode_frame.pack(fill="both", expand=True)


    def _scan_files(self):
        self.log_parser.update_logs()
        self.window.after(50, self._scan_files)


    def handle_log_event(self, data):
        """GUI responds to LogParser events."""
        if not self.current_mode_frame:
            print("No mode frame exists")
        self.current_mode_frame.process_new_log_line(data)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    configs = Configs()
    configs.load_configs()
    gui = ThalassaGUI(configs)
    gui.run()