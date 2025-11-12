from loguru import logger
import os
import json
from src.config.load_config import load_config

config_data = load_config()


_initialized = False  # Global flag to ensure setup happens only once

def setup_logger(log_filename_override=None):
    global _initialized
    if _initialized:
        return logger  # Already initialized, return same instance

    log_filename = log_filename_override or config_data.get("logging", {}).get("logger_path", "src/logs/app_logs.log")
    log_filename = os.path.abspath(log_filename)
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    log_level = config_data.get("logging", {}).get("log_level", "info").upper()

    # Clean existing handlers
    logger.remove()
    logger.add(log_filename, level=log_level, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line}] {message}")
    #logger.add(sys.stdout, level=log_level, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line}] {message}")

    _initialized = True
    return logger