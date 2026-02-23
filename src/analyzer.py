from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import pandas as pd
import json
import sys
import os
import torch

CACHE_DIR = "/runpod-volume/huggingface-cache"
MODEL_NAME = "Qwen/Qwen3-8B"


# ==========================================
# SAFE MODEL RESOLVER (FIXED)
# ==========================================
def resolve_model_path(model_name):
    """
    Ensures model exists locally.
    If missing → downloads automatically.
    """
    try:
        print(f"🔍 Checking model cache: {model_name}", file=sys.stderr)

        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=CACHE_DIR,
            local_files_only=False,   # IMPORTANT: auto download if missing
            resume_download=True
        )

        print(f"✅ Model ready at: {model_path}", file=sys.stderr)
        return model_path

    except Exception as e:
        raise RuntimeError(f"Failed to resolve model: {str(e)}")


def review_analyzer(CSV_FILE):

    # ==========================================
    # 1. LOAD DATA
    # ==========================================
    print(f"📂 Loading {CSV_FILE}...")

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load CSV: {str(e)}"}))
        sys.exit(1)

    potential_cols = ['review', 'text', 'content', 'body', 'comment', 'feedback']
    text_col = next(
        (c for c in df.columns if any(p in c.lower() for p in potential_cols)),
        None
    )

    if not text_col:
        print(json.dumps({"error": "No text column found in CSV"}))
        sys.exit(1)

    if len(df) > 1000:
        df = df.sample(1000)

    combined_text = "\n".join(df[text_col].astype(str).tolist())[:15000]

    # ==========================================
    # 2. PROMPT
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
    # 3. LOAD MODEL (FIXED)
    # ==========================================
    try:
        model_path = resolve_model_path(MODEL_NAME)

        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )

        messages = [{"role": "user", "content": prompt}]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )

        inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            do_sample=True,
        )

        output_ids = generated_ids[0][len(inputs.input_ids[0]):]
        output = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        # clean markdown
        if output.startswith("```"):
            output = output.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(output)
        print(json.dumps(parsed, indent=2))
        return parsed

    except json.JSONDecodeError as e:
        err = {
            "error": "Invalid JSON output",
            "details": str(e),
            "raw_output": output if "output" in locals() else None
        }
        print(json.dumps(err))
        return err

    except Exception as e:
        err = {
            "error": "Model failed",
            "details": str(e)
        }
        print(json.dumps(err))
        return err