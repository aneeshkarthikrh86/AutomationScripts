# /utils/logger.py
from datetime import datetime

class Logger:
    @staticmethod
    def log_success(message: str):
        print(f"✅ {datetime.now().strftime('%H:%M:%S')} - {message}")

    @staticmethod
    def log_failure(message: str):
        print(f"❌ {datetime.now().strftime('%H:%M:%S')} - {message}")

    @staticmethod
    def log_info(message: str):
        print(f"ℹ️ {datetime.now().strftime('%H:%M:%S')} - {message}")
