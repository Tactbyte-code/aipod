import ollama
import pandas as pd
import json
import sys


def review_analyzer(CSV_FILE):
    # Specific model optimized for JSON/Coding
    MODEL_NAME = "qwen3:8b"
    # If you don't have qwen3:8b, run: 'ollama pull qwen3:8b'
    # You can also use 'mistral' or 'qwen2.5:7b'

    # ==========================================
    # 1. LOAD DATA
    # ==========================================
    print(f"📂 Loading {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load CSV: {str(e)}"}))
        sys.exit(1)

    # Smart column detection
    potential_cols = ['review', 'text', 'content', 'body', 'comment', 'feedback']
    text_col = next((c for c in df.columns if any(p in c.lower() for p in potential_cols)), None)

    if not text_col:
        print(json.dumps({"error": "No text column found in CSV"}))
        sys.exit(1)

    # Prepare text (sampled & truncated for speed)
    if len(df) > 1000:
        df = df.sample(1000)

    # Combine text (limit to ~15k chars for local context window)
    combined_text = "\n".join(df[text_col].astype(str).tolist())[:15000]

    # ==========================================
    # 2. DEFINE JSON SCHEMA PROMPT
    # ==========================================
    prompt = f"""
    You are an API that analyzes app reviews.
    Analyze the following text and return ONLY a JSON object.
    Do not include markdown formatting.

    TEXT TO ANALYZE:
    '''
{combined_text}
    '''

    REQUIRED JSON STRUCTURE:
{{
    "summary": "A 2-sentence executive summary of the reviews.",
    "pain_points": [
        {{
            "issue": "Short title of the problem",
            "frequency": "High/Medium/Low",
            "example_quote": "A direct quote from the text"
        }}
    ],
    "actions": [
        "Specific action step 1",
        "Specific action step 2",
        "Specific action step 3"
    ],
    "details": "A deeper paragraph explaining the context of the pain points and user sentiment."
}}
    """

    # ==========================================
    # 3. RUN LOCAL MODEL
    # ==========================================
    print(f"🧠 Processing with {MODEL_NAME}...", file=sys.stderr)  # Log to stderr so it doesn't break JSON stdout

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prompt}],
            format='json',  # 👈 CRITICAL: Forces valid JSON output
        )

        # Extract the JSON string
        json_output = response['message']['content']

        # Parse and re-dump to ensure it is minified/valid before printing
        parsed_json = json.loads(json_output)
        print(json.dumps(parsed_json, indent=2))
        return parsed_json

    except Exception as e:
        error_result = {
            "error": "Model failed to generate valid JSON",
            "details": str(e)
        }
        print(json.dumps(error_result))
        return error_result