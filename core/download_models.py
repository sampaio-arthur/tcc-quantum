# -*- coding: utf-8 -*-
import os
from pathlib import Path

from sentence_transformers import SentenceTransformer

# Model to use (MiniLM is light and fast)
model_name = "all-MiniLM-L6-v2"
cache_dir = os.getenv("MODEL_CACHE_DIR", "/models")
marker = Path(cache_dir) / f"{model_name}.downloaded"

Path(cache_dir).mkdir(parents=True, exist_ok=True)

if marker.exists():
    print(f"Model {model_name} already available in {cache_dir}. Skipping download.")
else:
    print(f"Downloading model {model_name} to {cache_dir}...")
    SentenceTransformer(model_name, cache_folder=cache_dir)
    marker.write_text("ok")
    print("Download complete!")
