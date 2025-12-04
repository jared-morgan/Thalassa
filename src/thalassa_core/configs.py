from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import pickle

@dataclass
class SearchEntry:
    name: str = "New Search"
    on_off: bool = True
    muted: bool = False
    channel: str = "trade"
    buy_or_sell: str = "Buy"
    string_or_regex: str = "Strings"
    strings: str = ""
    regex: str = ""
    sound: str = "trade_chat_sound.ogg"

@dataclass
class Configs:
    search_strings: dict[str, SearchEntry] = field(default_factory=lambda: {
        1: SearchEntry(
            name="Buying CI Map",
            on_off=True,
            muted=False,
            channel="trade",
            buy_or_sell="Buy",
            string_or_regex="Strings",
            strings="ci map | cursed island | cursed isles | ci of | ci near",
            regex="",
            sound="trade_chat_sound.ogg"
        ),
        2: SearchEntry(
            name="Buying Vampire Reliq",
            on_off=True,
            muted=False,
            channel="trade",
            buy_or_sell="Buy",
            string_or_regex="Strings",
            strings="reliq | vamp charm | v charm | vampire charm | vampiric charm | vampirate charm",
            regex="",
            sound="trade_chat_sound.ogg"
        ),
        3: SearchEntry(
            name="Buying WWWFinder",
            on_off=True,
            muted=False,
            channel="trade",
            buy_or_sell="Buy",
            string_or_regex="Strings",
            strings="wayfinder | way-finder | wolf charm | w charm | ww charm | werewolf charm | werewolves charm",
            regex="",
            sound="trade_chat_sound.ogg"
        ),
    })

    log_dir: Path|None = None
    chatlog_dir: Path|None = None

    chat_filter_off: bool = False
    chat_mute: bool = False

    timer_offset: int = 0
    play_swabbie_warning_sound: bool = True
    swabbie_warning_sound = "plank_swabbie.mp3"
    rumble_mini: bool = False
    rumble_bars_natural_width: bool = False
    rumble_show_drop_off: bool = True
    rumble_play_warning_sound: bool = True
    rumble_warning_lead: float = 10.0
    rumble_warning_colour: bool = True
    rumble_warning_sound = "warning.ogg"
    forage_warning_lead: float = 15.0
    forage_warning_colour: bool = True
    timer_decimals: bool = False

    # GUI State
    window_width: int = 300
    window_height: int = 600
    window_x: int = 100
    window_y: int = 100
    selected_mode: str = "Cursed Isles"
    specific_pirate = ""

    settings_file: Path = Path.cwd() / "src" / "media" / "settings.pkl"

    @property
    def name(self) -> str:
        return self.chatlogs_path.stem.split("_")[0] if self.chatlogs_path.stem else ""


    def save_configs(self, path: Optional[Path] = None) -> None:
        path = Path(path) if path else self.settings_file
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("wb") as fh:
            pickle.dump(self, fh, protocol=pickle.HIGHEST_PROTOCOL)


        
    def load_configs(self, path: Optional[Path] = None) -> None:
        path = Path(path) if path else self.settings_file
        
        if not path.exists():
            return

        try:
            with path.open("rb") as fh:
                loaded: "Configs" = pickle.load(fh)

            # copy loaded attributes into self
            for k, v in vars(loaded).items():
                # Safety check: Only update attributes that actually exist in the current code
                if hasattr(self, k): 
                    setattr(self, k, v)
                else:
                    print(f"Warning: Skipping unknown config key '{k}' from save file.")

        except Exception as e:
            print(f"Failed to load configs: {e}")
            return

  
        