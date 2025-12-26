"""
Simple CSV ingestion entrypoint.

For now, this module delegates to your existing `scripts.store_data_from_csv`
so we don't duplicate logic.
"""

import subprocess
import sys
from pathlib import Path


def build_vector_db_from_csv(csv_path: str = "E:\\PYTHON\\BrainV2\\data\\raw\\dataset.csv"):
    """
    Call the existing script to store data from CSV into ChromaDB.
    """
    root = Path(__file__).resolve().parents[2]
    script_path = root / "scripts" / "store_data_from_csv.py"

    cmd = [sys.executable, str(script_path), "--csv", csv_path]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build_vector_db_from_csv()


