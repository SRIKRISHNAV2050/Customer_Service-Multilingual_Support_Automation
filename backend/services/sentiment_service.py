"""
Sentiment and CSAT prediction service.

- For fast feedback, use a lightweight local model or heuristics.
- For higher accuracy, use a small fine-tuned transformer or an LLM prompt.
- Output: continuous sentiment score [-1, 1] and discrete label.
"""

from textblob import TextBlob

def analyze_sentiment(text: str, locale: str = "en_IN") -> float:
    """
    Return a polarity score in [-1.0, 1.0].
    Note: TextBlob works best for English; for Indian languages consider translation + model.
    """
    if not text:
        return 0.0
    tb = TextBlob(text)
    return tb.sentiment.polarity
