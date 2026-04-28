import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "readmind-dev-secret")
    JSON_AS_ASCII = False
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    VAULT_ROOT = os.getenv("VAULT_ROOT", "/Users/taozhang/Documents/Obsidian Vault/书籍阅读")
    DEMO_DATA_ONLY = os.getenv("DEMO_DATA_ONLY", "0") == "1"
