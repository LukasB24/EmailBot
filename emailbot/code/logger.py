import os
from datetime import datetime

class Logger:
    __log_path = None
    __instance = None

    def __new__(cls, log_path = None):
        if cls.__instance is None:
            if cls.__log_path is None and log_path:
                cls.__log_path = log_path
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def write_log(self, message: str) -> None:
        if self.__log_path is None:
            print("You need to specify log path at least once when creating an instance")
            return
        
        if not os.path.exists(self.__log_path):
            os.mkdir(self.__log_path)

        with open(self.__log_path + "/log.txt", "a",  encoding="utf-8") as file:
            file.write(str(datetime.now()).split(".")[0] + ": " + message + "\n")


    