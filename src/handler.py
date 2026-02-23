import runpod
import json
import os
from get_reviews import download_reviews
from filter_negative import filter_negative_reviews
from analyzer import review_analyzer


OUTPUT_PATH = "data/negative_reviews.csv"


def handler(job):
    job_input = job["input"]  # Access the input from the request

    # TEST MODE — skip processing
    if job_input.get("test", False):
        with open("test_data.json", "r") as f:
            return json.load(f)

    query = job_input["prompt"]

    os.makedirs("data", exist_ok=True)

    csv_path = download_reviews(query, num_apps=3, count_per_app=200)

    filter_negative_reviews(csv_path, OUTPUT_PATH)

    result = review_analyzer(OUTPUT_PATH)
    return result


runpod.serverless.start({"handler": handler})  # Required