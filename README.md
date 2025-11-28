# 🏦 Ethiopian Banking App Sentiment Analysis

Project: Customer Experience Analytics for Fintech Apps (Week 2 Challenge)

Organization: Omega Consultancy

Author: [Your Name]

Date: November 2025

### 📖 Overview

This project analyzes customer satisfaction for the mobile banking applications of three major Ethiopian banks: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank.

By scraping user reviews from the Google Play Store and applying Natural Language Processing (NLP), this project identifies key satisfaction drivers and pain points to help stakeholders improve user retention and feature development.

### 🎯 Business Objective

Scrape real-world user feedback.

Analyze sentiment (Positive or Negative) using AI models from Hugging Face Transformers.

Extract thematic insights such as keywords like "Login", "Crash", and "Speed".

Deliver actionable recommendations for app improvement.

### 🛠️ **Tech Stack**

* **Language:** Python 3.11
* **Data Collection:** google-play-scraper
* **Data Engineering:** pandas, numpy
* **NLP & AI:** transformers (DistilBERT for sentiment), nltk (tokenization & stopwords), langdetect (language filtering)
* **Visualization:** seaborn, matplotlib
* **Environment Management:** python-dotenv

### 📂 Project Structure

```
BankReview_Analysis/
├── data/
│   ├── raw/                  # Initial scraped data (reviews_raw.csv)
│   └── processed/            # Cleaned and enriched data (reviews_with_sentiment.csv)
├── notebooks/
│   └── task2_analysis.ipynb  # Sentiment and thematic analysis (visualizations)
├── scripts/
│   ├── config.py             # Global settings (App IDs, paths)
│   ├── scraper.py            # Task 1 scraper with jitter and retry logic
│   ├── preprocessing.py      # Task 1 cleaning pipeline (Regex and Langdetect)
│   └── clean_data.py         # Legacy basic cleaner
├── .env                      # Environment variables (ignored by Git)
├── .gitignore
├── README.md
└── requirements.txt
```

### 🚀 How to Run

**Setup**

```
git clone <your-repo-url>
cd BankReview_Analysis
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Data Collection (Task 1)

```
python scripts/scraper.py
```

Output: data/raw/reviews_raw.csv

Data Preprocessing (Task 1)

```
python scripts/preprocessing_regex.py
```

Output: data/processed/reviews_processed_regex.csv

Analysis (Task 2)

```
jupyter notebook notebooks/task2_analysis.ipynb
```

Sentiment uses distilbert-base-uncased-finetuned-sst-2-english.

Themes identify common complaints and praise.

### 🧪 **A/B Testing: Language Filtering Strategy**

We conducted an experiment to identify the best method for handling multi-lingual data (English vs. Amharic/Other).

**Method A: langdetect Library (AI-based)**

* **Approach:** Used Google's language detection library to strictly identify English text.
* **Result:** Failed (53% retention).
* **Review:** The library was overly aggressive, often misclassifying short, valid reviews (e.g., "Good", "Nice app", "5 stars", "Wow") as "unknown" or non-English due to insufficient text for confidence. This caused nearly 50% dataset loss.

**Method B: Regex Filtering (Rule-based)**

* **Approach:** Targeted Ethiopic Unicode characters (\u1200-\u137F) to remove Amharic text while retaining English content.
* **Result:** Success (96% retention).
* **Review:** This method effectively removed Amharic noise while preserving short, high-value English feedback.

**Verdict:** Method B (Regex) was adopted for the final data preprocessing pipeline.

### 📊 Key Findings

Data retention: custom regex filtering retained ninety six percent of reviews compared to fifty three percent with standard language detection.

Pain points: frequent mentions of update, working, and login suggest stability issues after updates.

Drivers: positive sentiment is tied strongly to speed and ease of use.

🔜 Next Steps

Task 3: design a PostgreSQL database schema and load enriched data.

Task 4: build the final dashboard and comprehensive report.
