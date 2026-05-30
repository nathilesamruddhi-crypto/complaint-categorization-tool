"""
Text Preprocessing Module
Handles text cleaning and normalization for complaint analysis
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ===== NLTK DATA SETUP =====
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords')

# ===== INITIALIZE PREPROCESSOR =====
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """
    Clean and normalize complaint text
    
    Steps:
    1. Convert to lowercase
    2. Remove special characters and numbers
    3. Remove extra whitespace
    4. Remove stopwords
    5. Apply stemming
    
    Args:
        text (str): Raw complaint text
        
    Returns:
        str: Cleaned and normalized text
    """
    
    if not isinstance(text, str):
        text = str(text)
    
    # Step 1: Convert to lowercase
    text = text.lower()
    
    # Step 2: Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Step 3: Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Step 4: Remove special characters, numbers, and keep only alphabetic characters and spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Step 5: Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 6: Split into words
    words = text.split()
    
    # Step 7: Remove stopwords and apply stemming
    cleaned_words = []
    for word in words:
        if word not in stop_words and len(word) > 2:  # Keep words longer than 2 chars
            stemmed_word = stemmer.stem(word)
            cleaned_words.append(stemmed_word)
    
    # Step 8: Join back into string
    cleaned_text = " ".join(cleaned_words)
    
    return cleaned_text


def get_text_stats(text):
    """
    Get statistics about the text
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Statistics about the text
    """
    return {
        "original_length": len(text),
        "original_words": len(text.split()),
        "cleaned_length": len(clean_text(text)),
        "cleaned_words": len(clean_text(text).split())
    }


def batch_clean_text(texts):
    """
    Clean multiple texts at once
    
    Args:
        texts (list): List of text strings
        
    Returns:
        list: List of cleaned texts
    """
    return [clean_text(text) for text in texts]


if __name__ == "__main__":
    # Test the preprocessing
    test_complaints = [
        "I was charged twice for the same order without my consent!!!",
        "The product arrived completely damaged and broken. Very disappointed!",
        "Cannot login to my account. Password reset email not working.",
        "My delivery is 5 days late. Where is my package??? Contact support!"
    ]
    
    print("=" * 60)
    print("TEXT PREPROCESSING TEST")
    print("=" * 60)
    
    for i, complaint in enumerate(test_complaints, 1):
        cleaned = clean_text(complaint)
        stats = get_text_stats(complaint)
        
        print(f"\nComplaint {i}:")
        print(f"Original:  {complaint}")
        print(f"Cleaned:   {cleaned}")
        print(f"Stats:     Words: {stats['original_words']} → {stats['cleaned_words']}")
