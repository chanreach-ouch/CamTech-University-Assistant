import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.pipeline import run_pipeline

if __name__ == "__main__":
    success = run_pipeline()
    if success:
        print("Pipeline finished.")
    else:
        print("Pipeline failed.")
