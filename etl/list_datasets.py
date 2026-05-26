import os
from pathlib import Path

DATASET_FOLDER = Path("../datasets/green_trace_export/green_trace_export_20260310_195112")

files = sorted(os.listdir(DATASET_FOLDER))
print(f"Total files: {len(files)}")
for f in files:
    print(f)
