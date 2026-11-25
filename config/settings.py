
from pathlib import Path

# Main project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Project directories
DATASET_DIR = BASE_DIR / "datasets"
RAW_DATA_DIR = DATASET_DIR / "raw"
PROCESSED_DATA_DIR = DATASET_DIR / "processed"
SAMPLE_DATA_DIR = DATASET_DIR / "samples"

MODEL_DIR = BASE_DIR / "models"
EXPORT_DIR = BASE_DIR / "exports"

# Local NLP configuration
SPACY_MODEL = "en_core_web_sm"

# Graph configuration
DEFAULT_GRAPH_TYPE = "MultiDiGraph"

# Processing configuration
BATCH_SIZE = 100
MAX_TEXT_LENGTH = 100000

# Application configuration
APP_NAME = "KnowledgeGraphLLM"
APP_VERSION = "2.0.0"

# Create required directories automatically
directories = [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_DIR,
    MODEL_DIR,
    EXPORT_DIR
]

for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
