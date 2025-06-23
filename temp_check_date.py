import time
import os
import logging
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────

INTERVAL = 5                 # seconds between readings
LOG_DIR = "logs"             # folder to store log files
FILENAME_PREFIX = "temp_log"  # base filename (date will be added)

# ─── Setup ────────────────────────────────────────────────────────────────────

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_filename():
    """Returns log filename with today's date."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{FILENAME_PREFIX}_{date_str}.log")

# ─── Logger Setup ─────────────────────────────────────────────────────────────

def setup_logger(log_path):
    """Creates and returns a logger writing to the specified log_path."""
    logger = logging.getLogger("TempLogger")
    logger.setLevel(logging.INFO)
    # Remove existing handlers if any (e.g., when log file changes)
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)

    return logger

# ─── Temperature Reader ───────────────────────────────────────────────────────

def get_temp_celsius():
    """
    Runs 'vcgencmd measure_temp' and returns the numeric Celsius value as a float.
    """
    raw = os.popen("vcgencmd measure_temp").read().strip()
    if raw.startswith("temp=") and raw.endswith("'C"):
        return float(raw.replace("temp=", "").replace("'C", ""))
    else:
        # Try to parse any number just in case
        digits = "".join(ch for ch in raw if (ch.isdigit() or ch == "." or ch == "-"))
        return float(digits)

# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    current_date = datetime.now().date()
    logger = setup_logger(get_log_filename())

    logger.info(f"Started temperature logging every {INTERVAL} seconds.")

    try:
        while True:
            now = datetime.now()
            temp = get_temp_celsius()
            logger.info(f"{temp:.2f}°C")

            # Check if date has changed → create new log file
            if now.date() != current_date:
                current_date = now.date()
                logger = setup_logger(get_log_filename())
                logger.info("New log file started for new day.")

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")


if __name__ == "__main__":
    main()
