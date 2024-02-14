from datetime import datetime
import os

class AccesstimeLogger:
    def __init__(self) -> None:
        self.__filename = "timelog.txt"

    def log_time(self) -> None:
        with open("timelog.txt", "a", encoding="utf-8") as file:
            current_time = str(datetime.now()).split(".")[0]
            file.write(f"{current_time}\n")

    def get_last_log_time(self) -> str:
        last_log = ""
        if os.path.exists(self.__filename):
            with open("timelog.txt", "r", encoding="utf-8") as file:
                last_log = file.readlines()[-1]
        return last_log
        
    def calculate_time_difference(self) -> float:
        last_log = self.get_last_log_time().replace("\n", "")
        now = datetime.now()
        converted_last_log = datetime.strptime(last_log, "%Y-%m-%d %H:%M:%S")
        difference = now - converted_last_log
        return difference.total_seconds()