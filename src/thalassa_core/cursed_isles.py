import tkinter as tk 
import ttkbootstrap as ttk
from functools import partial

from thalassa_core.timer import Timer
from thalassa_core.hom import Homunculus
from thalassa_core.rumble import Rumble

class PlayerData:
    def __init__(self, parent: tk.Widget, name: str):
        self.name = name
        self.score = 0
        self.chests = [0, 0, 0]  # bb, fj, cc
        

class CursedIsles(ttk.Frame):
    def __init__(self, cursed_isles_frame: ttk.Frame, configs):
        super().__init__(cursed_isles_frame)
        self.configs = configs
        self.team: dict[str, PlayerData] = {}

        self.cursed_isles_frame = cursed_isles_frame

        self._start_ci() # Resets all the values
        self.ci_in_progress = False

        self.timer_frame = ttk.Frame(cursed_isles_frame)
        self.timer = Timer(self.timer_frame, configs)

        self.hom_frame = ttk.Frame(cursed_isles_frame)
        self.homunculus = Homunculus(self.hom_frame)

        self.rumble_frame = ttk.Frame(cursed_isles_frame)
        self.rumble = Rumble(self.rumble_frame, self.configs)

        self.LOG_EVENT_PATTERNS = [
            ("Reporting ready data.BoxingObject:", self._start_rumble),
            ("replaced=class com.threerings.piracy.puzzle.boxing.client.BoxingPanel", self._stop_rumble),
            ("Reporting ready data.SwordObject", self._start_sf),
            ("replaced=class com.threerings.piracy.puzzle.sword.client.SwordPanel", self._stop_sf),
            ("Setting place view com.threerings.yohoho.sea.seamonster.cursed.client.GauntletScenePanel", self._start_ci),
            ("Disabling skirmish environment mod [mod=dark_seas]", self._stop_ci),
            ("Stopping foraging in 119 seconds", self._start_forage),
        ]



    def _strip_names(self, data: str) -> list:
        data = "2025/11/25 19:20:11:789 INFO ak.doLog: Reporting ready data.BoxingObject:344547(Qrk, Qrk's Thrall, Jice, Jice's Thrall, Rudis, Rudis's Thrall, Vackert, Vackert's Thrall, Amizing, Amizing's Thrall, Karthika, Karthika's Thrall, Honeyy, Honeyy's Thrall, Enlightened One, Subjugated Zombie, Controlled Zombie, Subjugated Zombie, Dominated Zombie, Ensnared Zombie, Dominated Zombie):0."
        try:
            start = data.index("(") + 1
            end = data.index(")")
            names_str = data[start:end]
            names = [name.strip() for name in names_str.split(",")]
            return names
        except ValueError:
            return []

    
    def _reset_enemy_counts(self):
        self.enemy_counts = {
            "Enlightened One": 0, "Vargas The Mad": 0, "Zombie": 0,
            "Homunculus": 0, "Cultist": 0, "Total": 0
        }
    
    def _reset_ally_counts(self):
        self.ally_counts = {
            "Player": 0, "Swabbie": 0, "Thrall": 0, "Total": 0
        }

    def _reset_all_fray_teams(self):
        self._reset_ally_counts()
        self._reset_enemy_counts()
        
    def _add_enemy(self, enemy: str, quantity=1):
        if enemy in self.enemy_counts:
            self.enemy_counts[enemy] += quantity

    def _add_ally(self, ally: str, quantity=1):
        if ally in self.ally_counts:
            self.ally_counts[ally] += quantity

    def _calculate_teams(self, data: str):
        # Reset counts for this specific log read
        self._reset_all_fray_teams()
        
        names = self._strip_names(data)
        
        enemies_list = [" Zombie", "Enlightened One", "Vargas The Mad", " Homunculus", " Cultist"]

        for name in names:
            is_enemy = False
            for enemy_type in enemies_list:
                if enemy_type in name:
                    self._add_enemy(enemy_type.strip())
                    self._add_enemy("Total")
                    is_enemy = True
                    break

            if is_enemy:
                continue

            if " Thrall" in name:
                self._add_ally("Thrall")
                self._add_ally("Total")
                self.thralls += 1
            elif " " in name:
                self._add_ally("Swabbie")
                self._add_ally("Total")
            else:
                self._add_ally("Player")
                self._add_ally("Total")
                # Add to team dictionary if new (fray 1)
                if name not in self.team:
                    self.team[name] = PlayerData(self.cursed_isles_frame, name)


    def _start_general_fray(self, data: str = None):
        self.timer_frame.pack(fill="both", expand=True)
        self.timer.reset()
        self.timer.set_uses_duration(False)
        self.timer.start()
        self._calculate_teams(data)

    
    def _start_rumble(self, data: str = None):
        self.rumble_active = True
        self._start_general_fray(data)
        self.rumble.set_start_time()
        self.rumble_frame.pack(fill="both", expand=True)
        self.timer.set_warning_sound(
            self.configs.rumble_warning_sound, 
            self.configs.rumble_warning_lead,
            self.configs.rumble_play_warning_sound,
            self.configs.rumble_warning_colour)

    
    def _stop_rumble(self, data: str = None):
        self.rumble_active = False
        self.rumble.set_rumble_active(False)
        if not self.forage_active:
            self.timer_frame.pack_forget()
        self.rumble_frame.pack_forget()


    def _start_sf(self, data: str = None):
        self._start_general_fray(data)
        if self.enemy_counts["Homunculus"] > 0:
            self.homunculus.reset_homu_colours()
            self.hom_frame.pack(fill="both", expand=True)
        self.timer.set_warning_sound(
            None, 
            None,
            False,
            False)

    
    def _stop_sf(self, data: str = None):
        self.sf_active = False
        if not self.forage_active:
            self.timer_frame.pack_forget()
        self.hom_frame.pack_forget()
            

    def _start_ci(self, data: str = None):
        self.team: dict[str, PlayerData] = {}
        self.thralls = 0
        self.frays_won = 0
        self.current_fray = 0
        self.swabbies_on_board = 0
        self.rumble_active = False
        self.sf_active = False
        self.forage_active = False
        self._reset_all_fray_teams()
        self.ci_in_progress = True
        

    def _stop_ci(self, data: str = None):
        pass


    def _start_forage(self, data: str = None):
        self._stop_sf()
        self._stop_rumble()
        self.forage_active = True
        self.timer_frame.pack(fill="both", expand=True)
        self.timer.reset()
        self.timer.set_uses_duration(True)
        self.timer.set_max_duration(120000)
        self.timer.start()
        self.frays_won += 1
        self.timer.set_warning_sound(
            None, 
            self.configs.forage_warning_lead,
            False,
            self.configs.forage_warning_colour)
        self.after(120000, self._stop_forage)


    def _stop_forage(self, data: str = None):
        self.timer_frame.pack_forget()
        self.forage_active = False


    def process_new_log_line(self, data: str):
        for pattern, event_func in self.LOG_EVENT_PATTERNS:
            if pattern in data:
                event_func(data)
                break   # stop checking patterns for this line of data