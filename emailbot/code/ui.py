import datetime
import enum
import sys
import os
import platform 

class StateType(enum.Enum):
    POSITIV = 0
    INFO = 1
    CRITICAL = 2

def display(state: str, type: StateType):
    state_message = ""

    match type:
        case StateType.POSITIV:
            state_message = f"\033[32m      {state}\033[0m"
        case StateType.INFO:
            state_message = f"\033[33m      {state}\033[0m"
        case StateType.CRITICAL:
            state_message = f"\033[31m      {state}\033[0m"

    print("------------------------\nEmail monitoring\n------------------------")
    print(str(datetime.datetime.now().ctime()) + "\n")
    print("status: " + state_message + "\n")

def displayExitScreenAndExit(error: str):
    if platform.system().lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')

    display("inactive", StateType.CRITICAL)
    print(error)
    sys.exit()