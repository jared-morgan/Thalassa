import tkinter as tk
import ttkbootstrap as ttk
import time
from pathlib import Path
import pygame.mixer as mixer

class Timer(ttk.Frame):
    def __init__(self, timer_frame: ttk.Frame, configs=None):
        super().__init__(timer_frame)

        mixer.init()

        self.timer_frame = timer_frame
        
        # Configuration / State Variables
        self.warning_sound_lead = 0
        self.warning_sound_volume = 100
        self.warning_lead = 0
        self.warning_sound = "SystemHand" # Default sound
        
        # Time inputs are treated as milliseconds
        self.max_duration = 120000 
        self.using_duration = True
        self.precision: bool = configs.timer_decimals
        
        # Runtime State
        self.running = False
        self.start_time = 0
        self.time_passed = 0
        
        # UI Setup
        self._build_timer()
        self.reset() # Initialize display
    

    def reset_warnings(self):
        self._warning_played = False


    def _build_timer(self):
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        # The Time Display
        self.lbl_time = ttk.Label(
            self.timer_frame, 
            text="00:00", 
            font=("Helvetica", 48, "bold"),
            anchor="center",
            bootstyle="primary"
        )
        self.lbl_time.pack()

        # Simple Controls (for demonstration purposes)
        # btn_frame = ttk.Frame(self.timer_frame)
        # btn_frame.grid(row=1, column=0, pady=10)

        # ttk.Button(btn_frame, text="Start", command=self.start, bootstyle="success").pack(side="left", padx=5)
        # ttk.Button(btn_frame, text="Stop", command=self.stop, bootstyle="danger").pack(side="left", padx=5)
        # ttk.Button(btn_frame, text="Reset", command=self.reset, bootstyle="secondary").pack(side="left", padx=5)

    def _format_time(self, seconds):
        """Helper to format ms into MM:SS.d"""
        mins, secs = divmod(seconds, 60)

        # return f"{int(mins):02}:{int(secs):02}"
        
        if self.precision == True:
            dec = int((seconds % 1) * 10)
            return f"{int(mins):02}:{int(secs):02}.{dec}"
        else:
            return f"{int(mins):02}:{int(secs):02}"

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.monotonic()
            self._tick()
            self.warning_played = False

    def stop(self):
        self.running = False

    def reset(self):
        self.warning_played = False
        self.stop()
        self.lbl_time.configure(bootstyle="primary") # Reset color
        # self.lbl_time.config(text=self._format_time(self.current_time_ms))

    def _tick(self):
        if not self.running:
            return

        self.current_time = time.monotonic()
        self.time_passed = self.current_time - self.start_time
        
        # UI Updates
        self.lbl_time.config(text=self._format_time(self.time_passed))
        self._check_warnings()
        
        # Schedule next tick (approx 50ms for responsiveness)
        if self.running:
            self.after(50, self._tick)

    def _check_warnings(self):
        """Checks if current time breaches warning thresholds."""
        if self.warning_lead == None:
            return
        if self.using_duration:
            if self.warning_played:
                    return
            if self.max_duration - self.time_passed <= self.warning_lead:
                self.warning_played = True
                if self.warning_colour_on:
                    self.lbl_time.configure(bootstyle="danger")
                if self.warning_sound_on:
                    self._play_sound()
        
        else:
            _, secs = divmod(self.time_passed, 60)
            if 60 - secs <= self.warning_lead:
                if self.warning_played:
                    return
                self.warning_played = True
                if self.warning_colour_on:
                    self.lbl_time.configure(bootstyle="danger")
                if self.warning_sound_on > 0:
                    self._play_sound()
            else:
                self.lbl_time.configure(bootstyle="primary")
                self.warning_played = False
        

    def _play_sound(self):

        try:
            base_dir = Path(__file__).resolve().parent.parent
            sound_path = base_dir / "media" / "sounds" / self.warning_sound

            if not sound_path.exists():
                print(f"Sound file not found: {sound_path}")
                return

            mixer.music.load(str(sound_path))
            mixer.music.play()

        except Exception as e:
            print(f"Warning sound failed to play! {e}")

    # --- SETTERS ---

    def set_start_time(self, start_ms=time.monotonic()):
        self.current_time_ms = start_ms
        self.lbl_time.configure(text=self._format_time(self.current_time_ms))

    def set_max_duration(self, duration: int):
        self.max_duration = duration
        if not self.running: 
            self.reset()

    # def set_precision(self, precision: int):
    #     self.precision = precision
    #     self.lbl_time.configure(text=self._format_time(self.current_time_ms))

    def set_warning_sound(self, sound: str, lead: float, sound_on: bool, colour_on: bool):
        self.warning_sound = sound
        self.warning_lead = lead
        self.warning_sound_on = sound_on
        self.warning_colour_on = colour_on

    def set_uses_duration(self, use_duration: bool):
        self.using_duration = use_duration

