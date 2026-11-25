
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import configuration
from config.settings import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    DATASET_DIR,
    MODEL_DIR
)

print("Project:", APP_NAME)
print("Version:", APP_VERSION)
print("Project directory:", BASE_DIR)
print("Dataset directory:", DATASET_DIR)
print("Model directory:", MODEL_DIR)

print("\nConfiguration working successfully!")
