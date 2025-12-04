from pathlib import Path
import re

class LogData():
    pirate: str = ""
    size: int = 0

class LogParser():
    def __init__(self, event_callback, configs) -> None:
        # Dictionary  of filename and last size read]
        self.configs = configs
        self.log_files: dict[str, LogData] = {}
        self.chatlog_files: dict[str, LogData] = {}
        self.event_callback = event_callback

        self.chatlog_path: Path | None = None
        self.log_path: Path | None = None
        self.new_log_path: Path | None = None
        self.new_chatlog_path: Path | None = None

        self.SELL_STRINGS = ["sell", "[s]", "wts", "free", "giving"]
        self.BUY_STRINGS = ["buy", "[b]", "wtb", "lf", "looking"]

        self.LOG_EVENT_PATTERNS = [
            ("Entering game data.BoxingObject", "Cursed Isles"), # Start of Rumble
            ("replaced=class com.threerings.piracy.puzzle.boxing.client.BoxingPanel", "Cursed Isles"), # End of Rumble
            ("Entering game data.SwordObject", "Cursed Isles"), # Start of SF
            ("replaced=class com.threerings.piracy.puzzle.sword.client.SwordPanel", "Cursed Isles"), # End of SF
            ("Setting place view com.threerings.yohoho.sea.seamonster.cursed.client.GauntletScenePanel", "Cursed Isles"), # Start of CI
            ("Disabling skirmish environment mod [mod=dark_seas]", "Cursed Isles"), # End of CI
            ("Stopping foraging in 119 seconds", "Cursed Isles"), # Start of CI Forage
        ]

        self.CHATLOG_EVENT_PATTERNS = []


    def _emit(self, mode, data: str = None, *args, **kwargs):
        """Notify the GUI of an event."""
        if self.event_callback:
            self.event_callback(mode, data, *args, **kwargs)
    

    def update_log_path(self, new_path: Path) -> None:
        """Changes a temporary path which will be set at the end of the update loop"""
        self.new_log_path = new_path
    

    def update_chatlog_path(self, new_path: Path) -> None:
        """Changes a temporary path which will be set at the end of the update loop"""
        self.new_chatlog_path = new_path


    def _check_for_new_log_files(self) -> None:
        """Scan the log directory and update the log_files dictionary."""
        try:
            if self.log_path == None or not self.log_path.exists() or not self.log_path.is_dir():
                print(F"No log path set. {self.log_path}")
                return
        except Exception as error:
            print(F"Failed to load logs: {error = }")

        # Find files that match the pattern "yohoho_1764097495517.log"
        for log_file in self.log_path.glob("yohoho_*.log"):
            if log_file.is_file() and log_file.suffix == ".log":
                if log_file.name not in self.log_files:
                    self.log_files[log_file.name] = LogData()
                    new_file_size = log_file.stat().st_size
                    print(F"New log file found {log_file.name}: with filesize: {new_file_size}")
                    self._update_file_size(self.log_files, log_file.name, new_file_size)

    
    def _check_for_new_chatlog_files(self) -> None:
        """Scan the chatlog directory and update the chatlog_files dictionary."""
        try:
            if self.chatlog_path == None or not self.chatlog_path.exists() or not self.chatlog_path.is_dir():
                return
        except Exception as error:
            print(F"Failed to load chatlogs: {error = }")
        for chatlog_file in self.chatlog_path.glob("*"):
            # Checks if it is a file (not a directory) AND has no extension
            if chatlog_file.is_file() and chatlog_file.suffix.lower() in ("", ".txt"):
                if chatlog_file.name not in self.chatlog_files:
                    self.chatlog_files[chatlog_file.name] = LogData()
                    new_file_size = chatlog_file.stat().st_size
                    self._update_file_size(self.chatlog_files, chatlog_file.name, new_file_size)


    def _update_file_size(self, directory, filename: str, filesize: int) -> None:
        """Update the size of a specific file in the dictionary."""
        directory[filename].size = filesize

    def _check_file_size(self, directory, file_path: Path) -> int:
        """Checks if the filesize has changed, returns the number of new bytes."""
        # Check if the file exists
        filename = file_path.name
        if not file_path.exists() or not file_path.is_file():
            # Delete from log_files if it no longer exists
            if filename in directory:
                del directory[filename]
            return 0
        
        current_size = file_path.stat().st_size
        last_size = directory[filename].size
        if current_size > last_size:
            new_bytes = current_size - last_size
            return new_bytes
        return 0
        
    def _process_logs(self, log_file_path: Path, new_bytes: int) -> None:
        """Process new log entries from the specified log file."""
        filename = log_file_path.name
        directory = self.log_files
        last_size = self.log_files[filename].size
        current_size = last_size + new_bytes

        with log_file_path.open("r", encoding="utf-8") as fh:
            fh.seek(last_size)
            new_data = fh.read()
            for line in new_data.splitlines():
                for pattern, mode in self.LOG_EVENT_PATTERNS:
                    if pattern in line:
                        print(F"Pattern matched: {pattern}")
                        self._emit(mode=mode, data=line)

        # Update the last read size
        self._update_file_size(directory, filename, current_size)
            

    
    def _process_chatlogs(self, chatlog_file_path: Path, new_bytes: int) -> None:
        """Process new chatlog entries from the specified chatlog file."""
        filename = chatlog_file_path.name
        directory = self.chatlog_files
        last_size = self.chatlog_files[filename].size
        current_size = last_size + new_bytes

        with chatlog_file_path.open("r", encoding="utf-8", errors="replace") as fh:
            fh.seek(last_size)
            new_data = fh.read()
            for line in new_data.splitlines():
                for pattern, mode in self.LOG_EVENT_PATTERNS:
                    if pattern in line:
                        self._emit(mode=mode, data=line)
                self.apply_custom_chatlog_filters(line)

        # Update the last read size
        self._update_file_size(directory, filename, current_size)


    def apply_custom_chatlog_filters(self, line): #TODO add ability to click to copy pirates name to clipboard
        line_lower = line.lower()
        buy_and_sell_split = False
        buy_parts = []
        sell_parts = []

        if self.configs.chat_filter_off: # All filters have been disabled
            return

        # Iterate over the SearchEntry objects
        for key, entry in self.configs.search_strings.items():
            
            # 1. Check if the filter is enabled
            if not entry.on_off:
                continue

            # 2. Channel Check (Preserving original logic for log format parsing)
            # Assuming entry.channel is a string like "trade", "global", etc.
            try:
                # Matches old logic: checks if specific channel is set and matches log line index 2
                if entry.channel and entry.channel != line_lower.split(" ")[2]:
                    continue
            except IndexError:
                continue # line is part of a multiline message or format is otherwise wrong

            # 3. Regex Logic
            if entry.string_or_regex == "Regex":
                if entry.regex and re.search(entry.regex, line_lower):
                    self._emit("Filter Match", line, key=key)
                    #TODO Implement match kwarg to self._emit such that the matching text can be highlighted.
                continue

            # 4. String Logic
            elif entry.string_or_regex == "Strings":
                search_terms = []
                # Split by pipe and strip whitespace
                search_terms.extend([term.strip() for term in entry.strings.split('|') if term.strip()])

                if entry.channel == "trade":
                    if not buy_and_sell_split:
                        buy_parts, sell_parts = self.split_buy_and_sell(line_lower)
                        buy_and_sell_split = True
                    
                    # Logic: If I want to BUY, I search the 'sell_parts' of the message
                    if entry.buy_or_sell.lower() == "buy":
                        for term in search_terms:
                            for part in sell_parts:
                                if term in part:
                                    self._emit("Filter Match", line, key=key, match=term)
                    
                    # Logic: If I want to SELL, I search the 'buy_parts' of the message
                    elif entry.buy_or_sell.lower() == "sell":
                        for term in search_terms:
                            for part in buy_parts:
                                if term in part:
                                    self._emit("Filter Match", line, key=key, match=term)
                else:
                    # Standard channel search (Global, Crew, etc.)
                    for term in search_terms:
                        if term in line_lower:
                            self._emit("Filter Match", line, key=key, match=term)

    
    def split_buy_and_sell(self, message: str) -> tuple[list[str], list[str]]:
        buy_set = {k.lower() for k in self.BUY_STRINGS}
        sell_set = {k.lower() for k in self.SELL_STRINGS}

        all_keywords = sorted(buy_set | sell_set, key=len, reverse=True)
        if not all_keywords:
            return [], []

        # Match any keyword literally, case-insensitive
        pattern = "(" + "|".join(re.escape(k) for k in all_keywords) + ")"
        matches = list(re.finditer(pattern, message, flags=re.IGNORECASE))

        if not matches:
            return [], []

        buy_parts = []
        sell_parts = []

        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(message)
            segment = message[start:end].strip()
            keyword = m.group(1).lower()
            if keyword in buy_set:
                buy_parts.append(segment)
            else:
                sell_parts.append(segment)

        return buy_parts, sell_parts
    
        
    def update_logs(self) -> None:
        """Main log update function to check for and process new data in log files."""
        self._check_for_new_log_files()
        for filename in list(self.log_files.keys()):
            log_file_path = self.log_path / filename
            new_bytes = self._check_file_size(self.log_files, log_file_path)
            if new_bytes > 0:
                # There are new bytes to read. Start reading from last_size
                self._process_logs(log_file_path, new_bytes)

        if self.new_log_path != None:
            print(F"Log Path changed to {self.new_log_path}")
            self.log_path = self.new_log_path
            self.new_log_path = None

    def update_chatlogs(self) -> None:
        """Main chatlog update function to check for and process new data in chatlog files."""
        self._check_for_new_chatlog_files()
        for filename in list(self.chatlog_files.keys()):
            chatlog_file_path = self.chatlog_path / filename
            new_bytes = self._check_file_size(self.chatlog_files, chatlog_file_path)
            if new_bytes > 0:
                # There are new bytes to read. Start reading from last_size
                self._process_chatlogs(chatlog_file_path, new_bytes)
        
        if self.new_chatlog_path != None:
            print(F"Chatlog Path changed to {self.log_path}")
            self.chatlog_path = self.new_chatlog_path
            self.new_chatlog_path = None

    
    def update_all_logs(self):
        self.update_chatlogs()
        self.update_logs()