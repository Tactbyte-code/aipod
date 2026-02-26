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

    # Define the CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': '*',  # Allows all origins
        'Access-Control-Allow-Methods': 'POST, OPTIONS', # Specifies allowed methods
        'Access-Control-Allow-Headers': 'Content-Type, Authorization', # Specifies allowed headers
    }

    # Return the result as a dictionary, which RunPod converts to a JSON response
    # The 'headers' key adds the CORS headers to the HTTP response
    return {
        'statusCode': 200,
        'body': result,
        'headers': cors_headers
    }


runpod.serverless.start({"handler": handler})  # Required