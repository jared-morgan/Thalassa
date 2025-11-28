from pathlib import Path

class LogData():
    pirate: str = ""
    size: int = 0

class LogParser():
    def __init__(self, event_callback=None) -> None:
        # Dictionary  of filename and last size read
        self.log_files: dict[str, LogData] = {}
        self.event_callback = event_callback

    def _emit(self, data: str=None):
        """Notify the GUI of an event."""
        if self.event_callback:
            self.event_callback(data)
    
    def update_log_path(self, new_path: Path) -> None:
        """Update the log path and reset the log_files dictionary."""
        self.log_path: Path = new_path
        self.log_files = {}

    def _check_for_new_log_files(self) -> None:
        """Scan the log directory and update the log_files dictionary."""
        if not self.log_path.exists() or not self.log_path.is_dir():
            return

        # Find files that match the pattern "yohoho_1764097495517.log"
        for log_file in self.log_path.glob("yohoho_*.log"):
            if log_file.is_file() and log_file.suffix == ".log":
                if log_file.name not in self.log_files:
                    self.log_files[log_file.name] = LogData()

    def _update_log_file_size(self, filename: str, filesize: int) -> None:
        """Update the size of a specific log file in the log_files dictionary."""
        self.log_files[filename].size = filesize

    def _check_log_size(self, log_file_path: Path) -> int:
        """Checks if the log filesize has changed, returns the number of new bytes."""
        # Check if the file exists
        filename = log_file_path.name
        if not log_file_path.exists() or not log_file_path.is_file():
            # Delete from log_files if it no longer exists
            if filename in self.log_files:
                del self.log_files[filename]
            return 0
        
        current_size = log_file_path.stat().st_size
        last_size = self.log_files[filename].size
        if current_size > last_size:
            new_bytes = current_size - last_size
            return new_bytes
        return 0
        
    def _process_logs(self, log_file_path: Path, new_bytes: int) -> None:
        """Process new log entries from the specified log file."""
        filename = log_file_path.name
        last_size = self.log_files[filename].size
        current_size = last_size + new_bytes

        with log_file_path.open("r", encoding="utf-8") as fh:
            fh.seek(last_size)
            new_data = fh.read()
            for line in new_data.splitlines():
                self._emit(data=line)

        # Update the last read size
        self._update_log_file_size(filename, current_size)
    
        
    def update_logs(self) -> None:
        """Main log update function to check for and process new data in log files."""
        self._check_for_new_log_files()
        for filename in self.log_files.keys():
            log_file_path = self.log_path / filename
            new_bytes = self._check_log_size(log_file_path)
            if new_bytes > 0:
                # There are new bytes to read. Start reading from last_size
                self._process_logs(log_file_path, new_bytes)