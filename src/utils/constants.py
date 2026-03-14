import os
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
SCRIPTS_DIR = SRC_DIR / "scripts"

# Script Paths
SCRIPT_01 = SCRIPTS_DIR / "01.js"
SCRIPT_02 = SCRIPTS_DIR / "02.js"
SCRIPT_03 = SCRIPTS_DIR / "03.js"
SCRIPT_04 = SCRIPTS_DIR / "04.js"

# Default Browser Settings
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds

# Storage
# Persistent data is stored in %LOCALAPPDATA% to survive tool updates/moves
APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~"))) / "DouyinDownloader"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "DouyinDownloader")
USER_DATA_DIR = APP_DATA_DIR / "user_data"
CONFIG_FILE = APP_DATA_DIR / "config.json"
CHANNELS_FILE = APP_DATA_DIR / "channels.json"
