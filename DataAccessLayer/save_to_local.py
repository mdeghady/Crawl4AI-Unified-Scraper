import pandas as pd
import pyarrow.parquet as pq
import os
from datetime import datetime
from threading import Lock
from typing import List, Dict, Tuple


class ProductDataAccessLayer:
    def __init__(self, website:str,output_dir: str = "data/"):
        self.output_dir = output_dir
        self.lock = Lock()  # Thread-safe file operations
        self.website = website
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
        file_path = os.path.join(folder_path , f"products_{timestamp_part}.parquet")

        # Create directory if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        return folder_path , file_path

    def save_product(self, product: List[Dict]) -> None:
        """Save a single product to Parquet"""
        with self.lock:
            # Convert to DataFrame
            df = pd.DataFrame(product)

            # Define file path
            folder_path , file_path = self._get_partitioned_path()

            # Append or create new file
            if os.path.exists(file_path):
                existing = pq.read_table(file_path).to_pandas()

                # Choose only columns that are in the new DataFrame
                existing = existing[df.columns]

                # Concatenate existing and new DataFrame
                df = pd.concat([existing, df], ignore_index=True)

            # Save with compression
            df.to_parquet(
                file_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )