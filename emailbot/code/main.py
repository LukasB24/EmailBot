import traceback
import os
import platform
from time import sleep
from logger import Logger
import ui
from emailBot import EmailBot


if __name__ == "__main__":
    logger = Logger(os.curdir + "/logs")
    ui.display("initialize", ui.StateType.INFO)
    sleep(15)
    emailbot = EmailBot()

    if platform.system().lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')

    try:
        ui.display("active", ui.StateType.POSITIV)
        error_message = emailbot.run()

    except Exception:
        error_message = "Unhandled exception occured: see logs/log.txt for details"
        logger.write_log(str(traceback.format_exc()))

    if error_message:
        ui.displayExitScreenAndExit(error_message)
        logger.write_log(error_message)
