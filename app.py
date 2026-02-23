from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from get_reviews import download_reviews
from filter import filter_negative_reviews
from analyzer import review_analyzer
import json


app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # 👈 Allow these frontend URLs
    allow_credentials=True,
    allow_methods=["*"],      # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],      # Allow all headers
)

@app.get("/search")
def read_root(q: str | None = None):
    csv_path = download_reviews(q, num_apps=3, count_per_app=200)

    OUTPUT_PATH = "data/negative_reviews.csv"

    filter_negative_reviews(csv_path, OUTPUT_PATH)
    result = review_analyzer(OUTPUT_PATH)
    return result