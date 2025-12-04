import tkinter as tk 
import ttkbootstrap as ttk
from tkinter import filedialog
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame.mixer

from thalassa_core.configs import Configs, SearchEntry
from thalassa_core.log_parser import LogParser
from thalassa_core.cursed_isles import CursedIsles
from thalassa_core.chats_tab import ChatsTab
from thalassa_core.options_tab import OptionsTab


class ThalassaGUI:
    def __init__(self, configs):
        self.configs = configs
        self.log_parser = LogParser(self.handle_log_event, self.configs)
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
        
        # Save to file
        self.configs.save_configs()
        self.window.destroy()
    
    def _create_tabs(self):
        for name in ("Mode", "Chats", "Options"):
            frame = ttk.Frame(self.notebook, style="My.TFrame")
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame
        
        self.options_tab = OptionsTab(self.tabs["Options"], self.configs, self.handle_options_event)
        self.chats_tab = ChatsTab(self.tabs["Chats"], self.configs)
        self._setup_mode_tab()
    

    def _setup_mode_tab(self, event=None):
        mode_frame = self.tabs["Mode"]
        if self.mode_content is None:
            self.mode_content = ttk.Frame(mode_frame)
            self.mode_content.pack(fill="both", expand=True)

        # Clear the mode_frame ready for new child frame
        for widget in self.mode_content.winfo_children():
            widget.destroy()

        self.configs.selected_mode = self.options_tab.mode_var.get()

        if self.configs.selected_mode == "Cursed Isles":
            self.current_mode_frame = CursedIsles(self.mode_content, self.configs)
            self.current_mode_frame.pack(fill="both", expand=True)


    def _scan_files(self):
        self.log_parser.update_all_logs()
        self.window.after(50, self._scan_files)


    def handle_log_event(self, mode, data, *args, **kwargs):
        """GUI responds to LogParser events."""
        if not self.current_mode_frame:
            print("No mode frame exists")
        if mode == "Cursed Isles": #TODO Fix this
            self.current_mode_frame.process_new_log_line(data)
        if mode == "Filter Match":
            self.chats_tab.update_output(data, *args, **kwargs)


    def handle_options_event(self, func, *args, **kwargs):
        if func == "update_log_path":
            self.log_parser.update_log_path(*args, **kwargs)
            self.configs.log_dir = args[0]
        elif func == "update_chatlog_path":
            self.log_parser.update_chatlog_path(*args, **kwargs)
            self.configs.chatlog_dir = args[0]
        elif func == "setup_mode_tab":
            self._setup_mode_tab()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    configs = Configs()
    configs.load_configs()
    gui = ThalassaGUI(configs)
    gui.run()