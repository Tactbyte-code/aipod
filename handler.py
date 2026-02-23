import runpod
from get_reviews import download_reviews
from filter_negative import filter_negative_reviews
from analyzer import review_analyzer
import json


def handler(job):
    job_input = job["input"]  # Access the input from the request

    # Add your custom code here to process the input
    # TEST MODE — skip processing
    # TEST MODE
    if job_input.get("test", False):
        with open("test_data.json", "r") as f:
            return json.load(f)


    query = job["input"]["prompt"]
    csv_path = download_reviews(query, num_apps=3, count_per_app=200)

    OUTPUT_PATH = "data/negative_reviews.csv"

    filter_negative_reviews(csv_path, OUTPUT_PATH)
    result = review_analyzer(OUTPUT_PATH)
    return result

runpod.serverless.start({"handler": handler})  # Required