"""
Task 3: Database Loader
Loads the enriched review data into a PostgreSQL database.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_PATHS

# --- DATABASE CONFIGURATION ---
# [ACTION REQUIRED] Check your credentials!

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
# Connection String
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_schema(engine):
    """
    Resets the database by dropping old tables and creating new ones.
    """
    print("Initialize Database Schema...")

    # 1. Reset: Drop tables if they exist (Clean Slate)
    # CASCADE is important: it removes the reviews table because it depends on banks
    drop_tables = text("""
    DROP TABLE IF EXISTS reviews CASCADE;
    DROP TABLE IF EXISTS banks CASCADE;
    """)

    # 2. Create Banks Table
    create_banks = text("""
    CREATE TABLE banks (
        id SERIAL PRIMARY KEY,
        bank_name VARCHAR(100) UNIQUE NOT NULL
    );
    """)

    # 3. Create Reviews Table
    # Added a UNIQUE constraint to prevent future duplicates if needed
    create_reviews = text("""
    CREATE TABLE reviews (
        id SERIAL PRIMARY KEY,
        bank_id INTEGER REFERENCES banks(id),
        review_text TEXT,
        rating INTEGER,
        review_date DATE,
        sentiment_label VARCHAR(20),
        sentiment_score FLOAT,
        source VARCHAR(50),
        CONSTRAINT unique_review UNIQUE (bank_id, review_text, review_date)
    );
    """)

    with engine.connect() as conn:
        print("  -> Dropping old tables...")
        conn.execute(drop_tables)
        print("  -> Creating new tables...")
        conn.execute(create_banks)
        conn.execute(create_reviews)
        conn.commit()
    print("✅ Schema Reset & Created.")

def load_data():
    """Reads CSV and loads it into the DB."""

    # 1. Load Data
    csv_path = DATA_PATHS.get('sentiment_results')
    if not csv_path:
        # Fallback manual path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, 'data', 'processed', 'reviews_with_sentiment.csv')

    if not os.path.exists(csv_path):
        print(f"❌ Error: File not found at {csv_path}")
        return

    print(f"Reading data from {csv_path}...")
    df = pd.read_csv(csv_path)

    # 2. Connect to DB
    try:
        engine = create_engine(DB_URL)
        create_schema(engine) # <--- This now Wipes & Recreates tables
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Check DB_USER / DB_PASS in the script.")
        return

    # 3. Populate 'banks' table
    print("Populating Banks table...")
    unique_banks = df['bank'].unique()

    with engine.connect() as conn:
        for bank in unique_banks:
            stmt = text("INSERT INTO banks (bank_name) VALUES (:name) ON CONFLICT (bank_name) DO NOTHING")
            conn.execute(stmt, {"name": bank})
        conn.commit()

    # 4. Map Bank IDs
    banks_df = pd.read_sql("SELECT * FROM banks", engine)
    bank_map = dict(zip(banks_df['bank_name'], banks_df['id']))

    # 5. Prepare Reviews
    print("Preparing Reviews table...")
    df['bank_id'] = df['bank'].map(bank_map)

    db_df = df.rename(columns={
        'review': 'review_text',
        'date': 'review_date'
    })

    # Handle missing source column if necessary
    if 'source' not in db_df.columns:
        db_df['source'] = 'Google Play'

    cols_to_keep = ['bank_id', 'review_text', 'rating', 'review_date',
                    'sentiment_label', 'sentiment_score', 'source']
    db_df = db_df[cols_to_keep]

    # --- FIX: Deduplicate Data in Python before Insert ---
    # We remove duplicates based on the same columns as our DB Unique Constraint
    print("Checking for duplicates in CSV...")
    initial_count = len(db_df)
    db_df = db_df.drop_duplicates(subset=['bank_id', 'review_text', 'review_date'])
    final_count = len(db_df)

    if initial_count > final_count:
        print(f"  -> Removed {initial_count - final_count} duplicate rows from CSV before loading.")
    # -----------------------------------------------------

    # 6. Insert Data
    print(f"Inserting {len(db_df)} reviews...")
    # if_exists='append' works fine now because the table is empty!
    db_df.to_sql('reviews', engine, if_exists='append', index=False)

    print("\n✅ SUCCESS: Data loaded into PostgreSQL!")

    # 7. Verification
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM reviews")).scalar()
        print(f"Total rows in DB: {result}")

if __name__ == "__main__":
    load_data()