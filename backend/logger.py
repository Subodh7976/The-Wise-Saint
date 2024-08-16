import logging
import os
import sys
from datetime import datetime

class PrintToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip() != '':
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass

def setup_logging():
    # Create log file name with timestamp
    LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
    logs_path = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_path, exist_ok=True)
    LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

    # Configure logging
    logging.basicConfig(
        filename=LOG_FILE_PATH,
        format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    # Create logger
    logger = logging.getLogger()

    # Redirect stdout and stderr to logger
    sys.stdout = PrintToLogger(logger, logging.INFO)
    sys.stderr = PrintToLogger(logger, logging.ERROR)

    return logger