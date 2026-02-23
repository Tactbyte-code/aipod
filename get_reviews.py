import os
import pandas as pd
from google_play_scraper import Sort, reviews, search

def download_reviews(keyword, num_apps=1, count_per_app=1000):
    """
    Searches for apps by keyword and downloads reviews.
    
    Args:
        keyword (str): The category or search term (e.g., "fitness", "finance").
        num_apps (int): Number of apps to scrape (default 5).
        count_per_app (int): Max reviews per app to avoid infinite scraping.
        
    Returns:
        str: The path to the saved CSV file.
    """
    
    # 1. Setup data folder
    if not os.path.exists('data'):
        os.makedirs('data')

    print(f"🔎 Searching for top {num_apps} apps in: '{keyword}'...")

    # 2. Search for apps
    try:
        app_results = search(
            keyword,
            lang="en",
            country="us",
            n_hits=num_apps
        )
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return None

    all_reviews = []

    # 3. Loop through found apps
    for index, app in enumerate(app_results):
        app_id = app['appId']
        print(f"   ({index + 1}/{num_apps}) Scraping: {app.get('title', app_id)}...")
        
        try:
            # We use 'reviews' instead of 'reviews_all' to allow a limit
            # If you want ALL reviews, replace this block with your original 'reviews_all' code
            result, _ = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=count_per_app 
            )
            
            # Tag reviews with App ID
            for r in result:
                r['app_id'] = app_id
                r['app_title'] = app.get('title')
            
            all_reviews.extend(result)
            print(f"      ✅ Got {len(result)} reviews")
            
        except Exception as e:
            print(f"      ⚠️ Skipping {app_id}: {e}")

    # 4. Save to CSV
    if all_reviews:
        filename = f"data/{keyword.replace(' ', '_')}_reviews.csv"
        df = pd.DataFrame(all_reviews)
        df.to_csv(filename, index=False)
        
        print("\n" + "="*40)
        print(f"🎉 DONE! Collected {len(all_reviews)} reviews.")
        print(f"📂 Saved to: {filename}")
        print("="*40)
        return filename
    else:
        print("❌ No reviews were collected.")
        return None