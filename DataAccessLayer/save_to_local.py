import pandas as pd
import pyarrow.parquet as pq
import os
from datetime import datetime
from threading import Lock
from typing import List, Dict


class ProductDataAccessLayer:
    def __init__(self, website:str,output_dir: str = ".data/products"):
        self.output_dir = output_dir
        self.lock = Lock()  # Thread-safe file operations
        self.website = website
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_partitioned_path(self) -> str:
        year_part = datetime.now().strftime("%Y")
        month_part = datetime.now().strftime("%m")
        day_part = datetime.now().strftime("%d")
        timestamp_part = datetime.now().strftime("%H-%M-%S")
        website_part = self.website.replace(" ", "_").lower()
        current_path = os.path.dirname(os.path.abspath(__name__))
        return os.path.join(
            current_path,
            self.output_dir,
            'year={}/month={}/day={}/website={}'.format(year_part, month_part, day_part, website_part),
            f"products_{timestamp_part}.parquet"
        )

    def save_product(self, product: List[Dict]) -> None:
        """Save a single product to Parquet"""
        with self.lock:
            # Convert to DataFrame
            df = pd.DataFrame(product)

            # Define file path
            file_path = self._get_partitioned_path()

            # Create directory if it doesn't exist
            os.makedirs(file_path, exist_ok=True)

            # Append or create new file
            if os.path.exists(file_path):
                existing = pq.read_table(file_path).to_pandas()
                df = pd.concat([existing, df], ignore_index=True)

            # Save with compression
            df.to_parquet(
                file_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )