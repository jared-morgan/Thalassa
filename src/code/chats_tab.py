import tkinter as tk 
import ttkbootstrap as ttk
from tkinter import filedialog
import pygame.mixer as mixer
from pathlib import Path

from code.configs import SearchEntry


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        mixer.init()

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
        settings = SearchEntry(name=f"Filter {new_number}") 
        settings.is_new = True 
        self.search_strings[new_number] = settings
        self.create_filter_widgets(self.frame, settings, new_number)


class ChatsTab(ttk.Frame):
    def __init__(self, chats_frame: ttk.Frame, configs):
        super().__init__(chats_frame)
        self.configs = configs
        self.chats_frame = chats_frame
        
        self.tabs = {}

        self._setup_chats_tab()


    def _setup_chats_tab(self):

        # Global Mute button
        self.chats_mute_var = tk.BooleanVar(value=bool(self.configs.chat_mute))
        chats_mute_check = ttk.Checkbutton(
            self.chats_frame,
            text="Mute All Chats",
            variable=self.chats_mute_var
        )
        self.chats_mute_var.trace_add("write", lambda *args: setattr(self.configs, 'chat_mute', self.chats_mute_var.get()))
        chats_mute_check.pack(side="top", anchor="w", pady=2)

        # Global Off button
        self.chats_off_var = tk.BooleanVar(value=bool(self.configs.chat_filter_off))
        chats_off_check = ttk.Checkbutton(
            self.chats_frame,
            text="All Chats Off",
            variable=self.chats_off_var
        )
        self.chats_off_var.trace_add("write", lambda *args: setattr(self.configs, 'chat_filter_off', self.chats_off_var.get()))
        chats_off_check.pack(side="top", anchor="w", pady=2)

        # Create a Notebook for subtabs inside the Chats frame
        chats_sub_notebook = ttk.Notebook(self.chats_frame)
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

    def play_sound(self, data, *args, **kwargs):
        try:
            base_dir = Path(__file__).resolve().parent.parent
            sound_path = base_dir / "media" / "sounds" / self.configs.rumble_warning_sound

            if not sound_path.exists():
                print(f"Sound file not found: {sound_path}")
                return

            mixer.music.load(str(sound_path))
            mixer.music.play()

        except Exception as e:
            print(f"Warning sound failed to play! {e}")