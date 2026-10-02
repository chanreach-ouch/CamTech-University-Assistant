import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from app.ingestion.pipeline import run_pipeline

if __name__ == "__main__":
    success = run_pipeline("data/raw")
    if not success:
        sys.exit(1)
