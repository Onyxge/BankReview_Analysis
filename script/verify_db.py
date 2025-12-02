"""
Database Verification Script
Runs SQL queries via Python to ensure data was loaded correctly.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- DATABASE CONFIGURATION ---
# [ACTION REQUIRED] make sure this matches your setup!
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Connection String
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def run_verification():
    print("=" * 50)
    print("🚀 STARTING DATABASE VERIFICATION")
    print("=" * 50)

    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            print("\n✅ Connection Successful!\n")

            # --- QUERY 1: TOTAL COUNTS ---
            print("--- 1. Total Record Counts ---")
            review_count = conn.execute(text("SELECT count(*) FROM reviews")).scalar()
            bank_count = conn.execute(text("SELECT count(*) FROM banks")).scalar()
            print(f"Total Banks:   {bank_count}")
            print(f"Total Reviews: {review_count}")

            # --- QUERY 2: REVIEWS PER BANK ---
            print("\n--- 2. Reviews Per Bank ---")
            query_per_bank = text("""
                SELECT b.bank_name, COUNT(r.id) as count
                FROM reviews r
                JOIN banks b ON r.bank_id = b.id
                GROUP BY b.bank_name
                ORDER BY count DESC;
            """)
            df_bank = pd.read_sql(query_per_bank, conn)
            print(df_bank.to_string(index=False))

            # --- QUERY 3: AVERAGE RATING PER BANK ---
            print("\n--- 3. Average Ratings ---")
            query_avg = text("""
                SELECT b.bank_name, AVG(r.rating)::NUMERIC(10,2) as avg_rating
                FROM reviews r
                JOIN banks b ON r.bank_id = b.id
                GROUP BY b.bank_name
                ORDER BY avg_rating DESC;
            """)
            df_avg = pd.read_sql(query_avg, conn)
            print(df_avg.to_string(index=False))

            # --- QUERY 4: SNEAK PEEK (Pain Points) ---
            print("\n--- 4. Sneak Peek: Recent Negative Reviews ---")
            query_neg = text("""
                SELECT b.bank_name, r.review_text, r.sentiment_score
                FROM reviews r
                JOIN banks b ON r.bank_id = b.id
                WHERE r.sentiment_label = 'NEGATIVE'
                LIMIT 3;
            """)
            df_neg = pd.read_sql(query_neg, conn)
            # Truncate text for cleaner display
            df_neg['review_text'] = df_neg['review_text'].str[:70] + "..."
            print(df_neg.to_string(index=False))

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Check your DB_USER and DB_PASS in the script!")


if __name__ == "__main__":
    run_verification()