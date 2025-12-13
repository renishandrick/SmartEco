"""
Configuration module for SmartEco Backend
Centralizes all paths and settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Base directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    # Model formats
    PKL_DIR = os.path.join(MODELS_DIR, "pkl")
    ONNX_DIR = os.path.join(MODELS_DIR, "onnx")
    
    # Training settings
    TRAINING_DAYS = 90
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    
    # Model hyperparameters
    ENERGY_MODEL_PARAMS = {
        "n_estimators": 100,
        "max_depth": 15,
        "random_state": 42,
        "n_jobs": -1
    }
    
    WATER_MODEL_PARAMS = {
        "n_estimators": 100,
        "max_depth": 15,
        "random_state": 42,
        "n_jobs": -1
    }
    
    ANOMALY_MODEL_PARAMS = {
        "contamination": 0.1,
        "random_state": 42,
        "n_jobs": -1
    }
    
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "smarteco")
    
    # MongoDB Collections
    COLLECTION_TELEMETRY = "telemetry"
    COLLECTION_ALERTS = "alerts"
    COLLECTION_PREDICTIONS = "predictions"
    COLLECTION_DATASETS = "datasets"
    COLLECTION_SYSTEM_LOGS = "system_logs"
    
    # Data Retention
    TELEMETRY_RETENTION_DAYS = 90
    ALERTS_RETENTION_DAYS = 180
    LOGS_RETENTION_DAYS = 30
    
    @classmethod
    def ensure_dirs(cls):
        """Create all necessary directories"""
        for dir_path in [cls.DATA_DIR, cls.PKL_DIR, cls.ONNX_DIR]:
            os.makedirs(dir_path, exist_ok=True)

# Initialize directories on import
Config.ensure_dirs()
