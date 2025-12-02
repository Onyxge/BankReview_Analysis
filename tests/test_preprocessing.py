import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../script')))
from script.preprocessing import ReviewPreprocessor  # Import your actual class

# --- FIXTURES (Setup data for tests) ---
@pytest.fixture
def sample_raw_data():
    """Creates a small DataFrame with messy data for testing."""
    data = {
        'review_text': [
            "Good app!",  # Valid English
            "  Bad UI  ",  # Needs trimming
            "ሰላም",  # Amharic (Should be removed)
            "",  # Empty (Should be removed)
            None,  # Null (Should be removed)
            "Great service"  # Valid
        ],
        'review_date': [
            "2023-10-01 12:30:00",  # Needs normalization
            "2023-10-02",
            "2023-10-03",
            "2023-10-04",
            "2023-10-05",
            "invalid_date"  # Should be handled gracefully
        ],
        'bank_name': ['CBE'] * 6,
        'rating': [5, 1, 3, 4, 2, 5],
        'source': ['Google Play'] * 6
    }
    return pd.DataFrame(data)


# --- TESTS ---

def test_column_renaming(sample_raw_data):
    """Test 1: Does it rename columns correctly?"""
    # Initialize preprocessor with our fake data
    processor = ReviewPreprocessor()
    processor.df = sample_raw_data.copy()

    # Run the rename step manually
    processor.prepare_final_output()

    # Assert (Check results)
    assert 'review' in processor.df.columns
    assert 'date' in processor.df.columns
    assert 'bank' in processor.df.columns
    assert 'review_text' not in processor.df.columns  # Old name should be gone


def test_clean_text_basic(sample_raw_data):
    """Test 2: Does it remove whitespace?"""
    processor = ReviewPreprocessor()
    processor.df = sample_raw_data.copy()

    # Run cleaning
    processor.clean_text()

    # Check the "  Bad UI  " row
    # (We filter rows, so we need to find it by value)
    clean_reviews = processor.df['review_text'].tolist()
    assert "Bad UI" in clean_reviews  # Should be trimmed
    assert "  Bad UI  " not in clean_reviews


def test_remove_amharic(sample_raw_data):
    """Test 3: Does it filter out non-English (Amharic)?"""
    processor = ReviewPreprocessor()
    processor.df = sample_raw_data.copy()

    # Run cleaning (which includes language filtering)
    processor.clean_text()

    # The Amharic text "ሰላም" should be GONE
    # Note: langdetect might fail on very short text, but let's see if regex/langdetect catches it
    clean_reviews = processor.df['review_text'].tolist()

    # Check that "ሰላም" is NOT in the cleaned list
    # (If using Regex method, this will pass 100%. If using Langdetect, it might be tricky on 1 word)
    assert not any("ሰላም" in r for r in clean_reviews)


def test_remove_empty_rows(sample_raw_data):
    """Test 4: Does it remove empty/null reviews?"""
    processor = ReviewPreprocessor()
    processor.df = sample_raw_data.copy()

    original_count = len(processor.df)
    processor.clean_text()
    final_count = len(processor.df)

    # We started with 6 rows.
    # We expect to lose: "" (Empty), None (Null), "ሰላም" (Amharic)
    # Remaining should be: "Good app!", "Bad UI", "Great service" = 3
    assert final_count < original_count
    assert final_count == 3


def test_date_normalization(sample_raw_data):
    """Test 5: Are dates converted to YYYY-MM-DD?"""
    processor = ReviewPreprocessor()
    processor.df = sample_raw_data.copy()

    processor.normalize_dates()

    # Check the first valid date
    first_date = processor.df['review_date'].iloc[0]

    # It should be a date object or string '2023-10-01' (depending on implementation)
    # Our script converts to datetime.date object
    assert str(first_date) == "2023-10-01"