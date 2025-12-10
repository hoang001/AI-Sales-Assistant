# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env từ thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DB_PATH = BASE_DIR / "store.db"
    RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "products.json"
    VECTOR_DB_PATH = BASE_DIR / "data" / "vector_db"
    
    # Ngân hàng nhận tiền (để sinh QR)
    BANK_ID = "BIDV"
    BANK_ACC = "0987654321" # Thay số của bạn

settings = Config()