import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

# Ensure VADER lexicon is downloaded (safe to run multiple times)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def filter_negative_reviews(input_file, output_file, threshold=-0.5):
    """
    Reads a CSV of reviews, filters for strong negative sentiment using VADER,
    and saves the result to a new CSV.

    Args:
        input_file (str): Path to the source CSV (must have 'content' column).
        output_file (str): Path where the filtered CSV will be saved.
        threshold (float): Compound score cutoff (default -0.5 for strong negative).
    
    Returns:
        int: The number of negative reviews found.
    """
    
    # 1. Validation
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        return 0

    print(f"📂 Loading {input_file}...")
    
    try:
        df = pd.read_csv(input_file, encoding="utf-8", engine="python")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return 0

    # Check for required column (flexible check)
    text_col = None
    for col in ['content', 'review', 'text', 'body']:
        if col in df.columns:
            text_col = col
            break
            
    if not text_col:
        print(f"❌ Error: Could not find review text column in {df.columns}")
        return 0

    # 2. Pre-processing
    print(f"   Total rows: {len(df)}")
    df[text_col] = df[text_col].fillna("").astype(str)

    # 3. Sentiment Analysis
    print("   Running VADER analysis...")
    sia = SentimentIntensityAnalyzer()
    
    # Calculate scores
    # We use a lambda for speed and simplicity
    df['compound'] = df[text_col].apply(lambda x: sia.polarity_scores(x)['compound'])

    # 4. Filtering
    negative_df = df[df['compound'] <= threshold].copy()
    count = len(negative_df)
    
    print(f"   Found {count} strong negative reviews (Score <= {threshold})")

    # 5. Save Output
    # We only keep the text column to save space, as requested
    final_df = negative_df[[text_col]]
    final_df.to_csv(output_file, index=False)
    
    print(f"✅ Saved to: {output_file}")
    return count