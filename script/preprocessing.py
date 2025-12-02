"""
Data Preprocessing Script
Task 1: Data Preprocessing

This script cleans and preprocesses the scraped reviews data.
- Handles missing values
- Normalizes dates
- Cleans text data
- Filters out Amharic reviews using REGEX
- Renames columns to match Challenge Requirements
"""

import sys
import os

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime

import re
from config import DATA_PATHS


class ReviewPreprocessor:
    """Preprocessor class for review data"""

    def __init__(self, input_path=None, output_path=None):
        """
        Initialize preprocessor
        Args:
            input_path (str): Path to raw reviews CSV
            output_path (str): Path to save processed reviews
        """
        self.input_path = input_path or DATA_PATHS['raw_reviews']
        self.output_path = output_path or DATA_PATHS.get('processed_reviews')

        if not self.output_path:
             self.output_path = os.path.join(DATA_PATHS['processed_dir'], 'reviews_processed.csv')

        self.df = None
        self.stats = {}

    def load_data(self):
        """Load raw reviews data"""
        print("Loading raw data...")
        try:
            self.df = pd.read_csv(self.input_path)
            print(f"Loaded {len(self.df)} reviews")
            self.stats['original_count'] = len(self.df)
            return True
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.input_path}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load data: {str(e)}")
            return False

    def check_missing_data(self):
        """Check for missing data"""
        print("\n[1/6] Checking for missing data...")
        missing = self.df.isnull().sum()
        self.stats['missing_before'] = missing.to_dict()

    def handle_missing_values(self):
        """Handle missing values"""
        print("\n[2/6] Handling missing values...")

        critical_cols = ['review_text', 'rating', 'bank_name']
        before_count = len(self.df)

        self.df = self.df.dropna(subset=critical_cols)
        removed = before_count - len(self.df)

        if removed > 0:
            print(f"Removed {removed} rows with missing critical values")

        if 'user_name' in self.df.columns:
            self.df['user_name'] = self.df['user_name'].fillna('Anonymous')
        if 'thumbs_up' in self.df.columns:
            self.df['thumbs_up'] = self.df['thumbs_up'].fillna(0)
        if 'reply_content' in self.df.columns:
            self.df['reply_content'] = self.df['reply_content'].fillna('')

        self.stats['rows_removed_missing'] = removed
        self.stats['count_after_missing'] = len(self.df)

    def normalize_dates(self):
        """Normalize date formats to YYYY-MM-DD"""
        print("\n[3/6] Normalizing dates...")

        try:
            # FIX: errors='coerce' turns "invalid_date" into NaT instead of crashing
            self.df['review_date'] = pd.to_datetime(self.df['review_date'], errors='coerce')

            # Drop rows where date conversion failed (optional, but cleaner)
            self.df = self.df.dropna(subset=['review_date'])

            self.df['review_date'] = self.df['review_date'].dt.date

            # Extract metadata
            self.df['review_year'] = pd.to_datetime(self.df['review_date']).dt.year
            self.df['review_month'] = pd.to_datetime(self.df['review_date']).dt.month

            print(f"Date range: {self.df['review_date'].min()} to {self.df['review_date'].max()}")

        except Exception as e:
            print(f"WARNING: Error normalizing dates: {str(e)}")

    def clean_text(self):
        """Clean review text and filter out Amharic using REGEX"""
        print("\n[4/6] Cleaning text...")

        def clean_review_text(text):
            if pd.isna(text) or text == '':
                return ''
            text = str(text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

        # 1. Basic Cleaning
        self.df['review_text'] = self.df['review_text'].apply(clean_review_text)

        # 2. Filter Amharic (Ethiopic) Characters using REGEX
        # This keeps short English reviews like "Bad UI" which LangDetect deletes
        print("   -> Filtering Amharic characters (Regex method)...")
        before_amharic = len(self.df)

        def has_amharic(text):
            return bool(re.search(r'[\u1200-\u137F]', text))

        self.df = self.df[~self.df['review_text'].apply(has_amharic)]

        amharic_removed = before_amharic - len(self.df)
        if amharic_removed > 0:
            print(f"Removed {amharic_removed} reviews containing Amharic text")

        self.stats['amharic_reviews_removed'] = amharic_removed

        # 3. Remove Empty Strings
        before_empty = len(self.df)
        self.df = self.df[self.df['review_text'].str.len() > 0]
        empty_removed = before_empty - len(self.df)

        if empty_removed > 0:
            print(f"Removed {empty_removed} reviews with empty text")

        self.df['text_length'] = self.df['review_text'].str.len()

        self.stats['empty_reviews_removed'] = empty_removed
        self.stats['count_after_cleaning'] = len(self.df)

    def validate_ratings(self):
        """Validate rating values (should be 1-5)"""
        print("\n[5/6] Validating ratings...")

        invalid = self.df[(self.df['rating'] < 1) | (self.df['rating'] > 5)]

        if len(invalid) > 0:
            print(f"WARNING: Found {len(invalid)} reviews with invalid ratings")
            self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]
        else:
            print("All ratings are valid (1-5)")

        self.stats['invalid_ratings_removed'] = len(invalid)

    def prepare_final_output(self):
        """Prepare final output format"""
        print("\n[6/6] Preparing final output...")

        print("   -> Renaming columns to: review, date, bank...")
        self.df = self.df.rename(columns={
            'review_text': 'review',
            'review_date': 'date',
            'bank_name': 'bank'
        })

        output_columns = [
            'review_id',
            'review', 'rating', 'date', 'bank', 'source',
            'bank_code', 'review_year', 'review_month', 'user_name', 'thumbs_up', 'text_length'
        ]

        output_columns = [col for col in output_columns if col in self.df.columns]
        self.df = self.df[output_columns]
        self.df = self.df.sort_values(['bank', 'date'], ascending=[True, False])
        self.df = self.df.reset_index(drop=True)

        print(f"Final dataset: {len(self.df)} reviews")

    def save_data(self):
        """Save processed data"""
        print("\nSaving processed data...")
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            self.df.to_csv(self.output_path, index=False)
            print(f"Data saved to: {self.output_path}")
            self.stats['final_count'] = len(self.df)
            return True
        except Exception as e:
            print(f"ERROR: Failed to save data: {str(e)}")
            return False

    def generate_report(self):
        """Generate preprocessing report"""
        print("\n" + "=" * 60)
        print("PREPROCESSING REPORT")
        print("=" * 60)
        # (Simplified report print for brevity, logic remains same as previous scripts)
        print(f"Final records: {len(self.df)}")

    def process(self):
        """Run complete preprocessing pipeline"""
        print("=" * 60)
        print("STARTING DATA PREPROCESSING")
        print("=" * 60)

        if not self.load_data():
            return False

        self.check_missing_data()
        self.handle_missing_values()
        self.normalize_dates()
        self.clean_text()
        self.validate_ratings()
        self.prepare_final_output()

        if self.save_data():
            self.generate_report()
            return True

        return False

def main():
    preprocessor = ReviewPreprocessor()
    preprocessor.process()

if __name__ == "__main__":
    main()