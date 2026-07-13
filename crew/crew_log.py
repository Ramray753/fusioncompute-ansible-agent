import os
import sys
import logging
import re
from datetime import datetime

# ==============================================================================
# LOGGING & DIRECTORY INITIALIZATION
# ==============================================================================
# [MODIFIED] Establish absolute project root directory anchor for log file generation.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Generate synchronized timestamp for this execution run
current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
sys_log_path = os.path.join(LOG_DIR, f"system_{current_timestamp}.log")
crew_log_path = os.path.join(LOG_DIR, f"crew_execution_{current_timestamp}.log")

# ==============================================================================
# LOGGER CONFIGURATION
# ==============================================================================
# 1. Configure standardized runtime logger (Outputs to Terminal & System Log File)
# Binding StreamHandler to the original sys.stdout before it gets hijacked.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(sys_log_path, encoding="utf-8")
    ]
)

# Export the configured logger to be imported by other modules
logger = logging.getLogger(__name__)

# ==============================================================================
# CONSOLE INTERCEPTOR
# ==============================================================================
# 2. Configure CrewAI console interceptor (Outputs to Terminal & Execution Log File)
class DualOutput:
    """
    Intercepts standard output to duplicate console echoes to a file.
    Strips ANSI terminal color codes to ensure clean text formatting in logs.
    """
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log_file = open(filepath, "a", encoding="utf-8")
        # Regex to match ANSI escape sequences (colors, styles, etc.)
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def write(self, message):
        # Print original colored message to the terminal
        self.terminal.write(message)
        # Write clean, uncolored string to the log file
        clean_message = self.ansi_escape.sub('', message)
        self.log_file.write(clean_message)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

# Hijack standard output dynamically for all subsequent standard print calls
sys.stdout = DualOutput(crew_log_path)