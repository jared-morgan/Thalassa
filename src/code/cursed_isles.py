import tkinter as tk 
import ttkbootstrap as ttk
from typing import Dict

class PlayerData():
    def __init__(self, name: str):
        self.ci_frame = ttk.Frame() # I need to add a parent here and in this class input?
        self.name = name
        self.score = 0
        self.chests = [0, 0, 0]  # bb, fj, cc
        self._reset_enemy_counts()
        self._reset_ally_counts()
        self.fray_count = 0
        self.swabbies_on_board = 0


class CursedIsles(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        super().__init__(parent)
        #Initialise a dictionary to hold team members
        self.team : Dict[str, int] = {}
        self.thralls = 0
    

    def _strip_names(self, data: str) -> list:
        # Example data string:
        # 2025/11/25 19:34:22:202 INFO ak.doLog: Entering game data.BoxingObject:346978(Enlightened One, Obedient Zombie, Servile Zombie, 
        # Enlightened One, Subjugated Zombie, Ensnared Zombie, Subjugated Zombie, Servile Zombie, Mindless Zombie, Qrk, Jice, 
        # Rudis, Vackert, Amizing, Karthika, Honeyy, Jice's Thrall, Rudis's Thrall, Amizing's Thrall, Karthika's Thrall, 
        # Honeyy's Thrall, Qrk's Thrall, Vackert's Thrall):0.

        # All the names are within the parentheses
        start = data.index("(") + 1
        end = data.index(")")
        names_str = data[start:end]
        names = [name.strip() for name in names_str.split(",")]
        return names
    
    def _reset_enemy_counts(self):
        self.enemy_counts = {"Enlightened One": 0,
                             "Vargas The Mad": 0,
                             "Zombie": 0,
                             "Homunculus": 0,
                             "Cultist": 0,
                             "Total": 0}
    
    def _reset_ally_counts(self):
        self.ally_counts = {"Player": 0,
                            "Swabbie": 0,
                            "Thrall": 0,
                            "Total": 0}
        
    def _add_enemy(self, enemy: str, quantity=1):
        self.enemy_counts[enemy] += 1

    def _add_ally(self, ally: str, quantity=1):
        self.ally_counts[ally] += 1

    def update_team_members(self, data: str):
        names = self._strip_names()

        # Ignore " Zombie" and "Enlightened One" entries

        for name in names:
            if "Zombie" in name or name == "Enlightened One":
                continue
            elif " Thrall" in name:
                self.thralls += 1
            elif " " in name:
                self.swabbies_onboard += 1
            else: # Must be a player name
                if name not in self.team:
                    self.team[name] = PlayerData(name)


    def increase_fray_count(self):
        self.fray_count += 1
    

    def calculate_teams(self, data: str):
        self._reset_enemy_counts()
        self._reset_ally_counts
        names = self._strip_names(data)
        
        for name in names:
            enemies = [" Zombie", "Enlightened One", "Vargas The Mad", " Homunculus", " Cultist"]

            is_enemy = False
            for enemy in enemies:
                if enemy in name:
                    self._add_enemy(enemy.strip())
                    is_enemy = True
                    break    # stop checking other enemy names

            if is_enemy:
                continue    # skip to next outer loop item

            if " Thrall" in name:
                self._add_ally("Thrall")
            elif " " in name:
                self._add_ally("Swabbie")
            else:
                self._add_ally("Player")

    
    def estimate_frays(self):
        pass
        
        