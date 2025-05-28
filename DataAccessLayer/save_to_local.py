import pandas as pd
import pyarrow.parquet as pq
import os
from datetime import datetime
from threading import Lock
from typing import List, Dict, Tuple, Optional

class ProductDataAccessLayer:
    def __init__(self, website: str, output_dir: str = "data/", batch_size: int = 100):
        self.output_dir = output_dir
        self.lock = Lock()  # Thread-safe operations
        self.website = website
        self.batch_size = batch_size  # Save after every N products
        self.product_buffer = []  # Accumulate products here
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_partitioned_path(self) -> Tuple[str, str]:
        year_part = datetime.now().strftime("%Y")
        month_part = datetime.now().strftime("%m")
        day_part = datetime.now().strftime("%d")
        timestamp_part = datetime.now().strftime("%H")
        website_part = self.website.replace(" ", "_").lower()
        current_path = os.path.dirname(os.path.abspath(__name__))
        folder_path = os.path.join(
            current_path,
            self.output_dir,
            'year={}/month={}/day={}/website={}'.format(year_part, month_part, day_part, website_part),
        )
        file_path = os.path.join(folder_path, f"products_{timestamp_part}.parquet")
        os.makedirs(folder_path, exist_ok=True)
        return folder_path, file_path

    def _save_batch(self) -> None:
        """Internal method to save the buffer to disk."""
        if not self.product_buffer:
            return

        with self.lock:
            df = pd.DataFrame(self.product_buffer)
            folder_path, file_path = self._get_partitioned_path()

            if os.path.exists(file_path):
                existing = pq.read_table(file_path).to_pandas()
                common_cols = [col for col in df.columns if col in existing.columns]
                existing = existing[common_cols]
                df = df[common_cols]
                df = pd.concat([existing, df], ignore_index=True)

            df.to_parquet(
                file_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            self.product_buffer = []  # Clear buffer after saving

    def add_product(self, product: Dict) -> None:
        """Add a single product to the buffer and save if batch_size is reached."""
        self.product_buffer.append(product)
        if len(self.product_buffer) >= self.batch_size:
            self._save_batch()

    def flush(self) -> None:
        """Force-save any remaining products in the buffer."""
        self._save_batch()