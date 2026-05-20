import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')

stemmer = PorterStemmer()

stop_words = set(stopwords.words('english'))

def clean_text(text):

    # Convert lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^a-zA-Z]', ' ', text)

    # Split words
    words = text.split()

    # Remove stopwords
    words = [word for word in words if word not in stop_words]

    # Stemming
    words = [stemmer.stem(word) for word in words]

    return " ".join(words)