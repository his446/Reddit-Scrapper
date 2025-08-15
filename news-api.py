from newsapi import NewsApiClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY", "")
client = NewsApiClient(api_key=API_KEY)

news = client.get_everything(
    q="economy",
    from_param='2025-08-14',
    to='2025-08-14',
    language="en",
    sort_by='popularity'
    
)
with open("news_results.json", "w", encoding="utf-8") as f:
    json.dump(news, f, indent=4, ensure_ascii=False)

print("Results saved to news_results.json")