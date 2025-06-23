import time
import os
import logging
from logging.handlers import TimedRotatingFileHandler

# ─── Configuration ────────────────────────────────────────────────────────────

INTERVAL = 5                # seconds between readings
LOG_FILENAME = "temp_log.log"
BACKUP_COUNT = 7            # how many days of logs to keep
WHEN = "midnight"           # rotate at midnight every day
TIMEZONE = None             # use local time for timestamps (None) or "UTC"

# ─── Set up the logger ────────────────────────────────────────────────────────

logger = logging.getLogger("TempMonitor")
logger.setLevel(logging.INFO)

# Create handler that logs to a file, rotating at midnight
handler = TimedRotatingFileHandler(
    filename=LOG_FILENAME,
    when=WHEN,
    interval=1,
    backupCount=BACKUP_COUNT,
    utc=(TIMEZONE == "UTC")
)
# Format: 2025-06-05 14:30:00 - 48.2°C
formatter = logging.Formatter(
    fmt="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also print to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ─── Temperature-Reading Loop ─────────────────────────────────────────────────

def get_temp_celsius():
    """
    Runs 'vcgencmd measure_temp' and returns the numeric Celsius value as a float.
    """
    raw = os.popen("vcgencmd measure_temp").read().strip()  # e.g. "temp=48.2'C"
    # Strip away "temp=" and "'C"
    if raw.startswith("temp=") and raw.endswith("'C"):
        return float(raw.replace("temp=", "").replace("'C", ""))
    else:
        # Fallback: try to parse any number inside the string
        digits = "".join(ch for ch in raw if (ch.isdigit() or ch == "." or ch == "-"))
        return float(digits)


def main():
    logger.info(f"Starting temperature monitoring every {INTERVAL} seconds.")
    try:
        while True:
            temp_c = get_temp_celsius()
            message = f"{temp_c:.2f}°C"
            # This will log with timestamp (handled by the logger’s formatter)
            logger.info(message)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")


if __name__ == "__main__":
    main()
