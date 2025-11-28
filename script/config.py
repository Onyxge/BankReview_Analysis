import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Play Store App IDs
APP_IDS = {
    'CBE': os.getenv('BANK_ID_CBE', 'com.combanketh.mobilebanking'),
    'BOA': os.getenv('BANK_ID_BOA', 'com.bankofabyssinia.mobilebanking'),
    'Dashen': os.getenv('BANK_ID_DASHEN', 'com.dashen.mobilebanking')
}

# Bank Names Mapping
BANK_NAMES = {
    'CBE': 'Commercial Bank of Ethiopia',
    'BOA': 'Bank of Abyssinia',
    'Dashen': 'Dashen Bank'
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'reviews_per_bank': int(os.getenv('REVIEWS_PER_BANK', 400)), # Requirement is 400+
    'max_retries': int(os.getenv('MAX_RETRIES', 3)),
    'lang': 'en',
    'country': 'us', # 'us' often gets more reviews than 'et', but we can try both
    'sort': 'NEWEST'
}

# File Paths
# We use os.path.join to ensure it works on macOS and Windows equally well
current_file_path = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_file_path)
BASE_DIR = os.path.dirname(scripts_dir)

DATA_PATHS = {
    'raw': os.path.join(BASE_DIR, 'data', 'raw'),
    'processed_dir': os.path.join(BASE_DIR, 'data', 'processed'),
    'raw_reviews': os.path.join(BASE_DIR, 'data', 'raw', 'reviews_raw.csv'),
}