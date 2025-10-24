Prompt: okay for this subject : "AI in the public eye" propose to me some start up code and project plan for this purpose with detailed steps 

Response:
Perfect choice 🎯 — **“AI in the Public Eye”** is an *excellent portfolio project*.
It blends **data engineering**, **FastAPI**, **NLP/sentiment analysis**, **dashboarding (Next.js)**, and **DevOps deployment**, all under your $15 budget.

Let’s design it from scratch with a **clear architecture**, **step-by-step roadmap**, and **starter FastAPI code** so you can begin right away.

---

## 🌍 Project Concept: “AI in the Public Eye”

**Goal:**
Track how people *talk about AI* on Reddit — across tech, news, and future-related communities — and visualize trends and sentiment over time.

You’ll:

1. Scrape Reddit posts & comments from selected subreddits.
2. Analyze text to detect **AI-related mentions** (keywords, sentiment).
3. Store results in a database.
4. Expose APIs (FastAPI).
5. Build a **Next.js dashboard** to visualize:

   * Mentions of “AI”, “GPT”, “OpenAI”, “automation”, etc.
   * Positive vs. negative sentiment.
   * Trending topics over time.

---

## 🧠 1. Architecture Overview

```text
                 ┌────────────────────────────┐
                 │      Next.js Dashboard     │
                 │  (Trends, Sentiment, Tags) │
                 └───────────┬────────────────┘
                             │ REST API
                             ▼
                 ┌────────────────────────────┐
                 │         FastAPI API         │
                 │  /fetch, /analyze, /stats   │
                 └───────────┬────────────────┘
                             │
                             ▼
                 ┌────────────────────────────┐
                 │ PostgreSQL (Neon or Docker)│
                 │   posts, comments, scores   │
                 └───────────┬────────────────┘
                             │
                             ▼
                 ┌────────────────────────────┐
                 │ Reddit API Scraper         │
                 │  (aiohttp + PRAW)          │
                 └────────────────────────────┘
```

---

## 📦 2. Tech Stack

| Component             | Tool                                   |
| --------------------- | -------------------------------------- |
| Backend               | FastAPI                                |
| Data source           | Reddit API (via `PRAW` or `asyncpraw`) |
| NLP / Sentiment       | `TextBlob` or `VADER` (lightweight)    |
| DB                    | PostgreSQL (free-tier Neon.tech)       |
| Frontend              | Next.js + Tailwind + Recharts          |
| Deployment            | Render / Railway (free)                |
| CI/CD                 | GitHub Actions                         |
| Kubernetes (optional) | Local demo with Minikube               |

---

## 📅 3. Step-by-Step Project Plan

### 🧩 Phase 1: Setup & Scraping

1. Create Reddit app → get `CLIENT_ID`, `CLIENT_SECRET`, etc.
2. Set up FastAPI app + requirements.
3. Implement endpoints to:

   * Fetch recent posts from target subreddits.
   * Store data (title, score, url, date, subreddit).
   * Filter for AI-related keywords.

**Subreddits:**
`r/Futurology`, `r/worldnews`, `r/technology`, `r/MachineLearning`, `r/artificial`

---

### 🧠 Phase 2: Sentiment & Analysis

1. Use VADER (`nltk.sentiment.vader`) to classify sentiment (pos/neg/neu).
2. Store analysis results (keyword, sentiment, date).
3. Create endpoints to:

   * `/api/stats/daily`
   * `/api/sentiment`
   * `/api/top_keywords`

---

### 📊 Phase 3: Dashboard (Next.js)

1. Call the FastAPI endpoints to show:

   * Line chart: Mentions per day.
   * Bar chart: Average sentiment over time.
   * Word cloud: Top keywords.
2. Add filters by subreddit or date range.

---

### 🚀 Phase 4: Deployment

1. Dockerize both FastAPI & Next.js apps.
2. Push to GitHub.
3. Add GitHub Actions → deploy automatically to Render or Railway.
4. Add free Neon PostgreSQL database.
5. (Optional) Deploy locally on Minikube to show K8s manifests in portfolio.

---

## ⚙️ 4. Starter FastAPI Code

`main.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
import asyncpraw
import os
import asyncpg
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

app = FastAPI(title="AI in the Public Eye")

# Reddit credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = "AI-Trend-Tracker/0.1"

# DB connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Target subreddits and keywords
TARGET_SUBS = ["Futurology", "worldnews", "technology", "MachineLearning", "artificial"]
KEYWORDS = ["AI", "artificial intelligence", "GPT", "OpenAI", "automation", "machine learning"]

@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.connect(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/api/fetch")
async def fetch_data():
    reddit = asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    analyzer = SentimentIntensityAnalyzer()
    total_saved = 0

    for sub in TARGET_SUBS:
        subreddit = await reddit.subreddit(sub)
        async for post in subreddit.hot(limit=20):
            title = post.title.lower()
            if any(k.lower() in title for k in KEYWORDS):
                sentiment = analyzer.polarity_scores(title)["compound"]
                await app.state.db.execute("""
                    INSERT INTO posts (id, title, subreddit, score, sentiment, created_utc)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (id) DO NOTHING;
                """, post.id, post.title, sub, post.score, sentiment, datetime.utcfromtimestamp(post.created_utc))
                total_saved += 1
    return {"message": f"Fetched and saved {total_saved} posts."}

@app.get("/api/stats/daily")
async def get_daily_stats():
    query = """
    SELECT DATE(created_utc) as date,
           COUNT(*) as mentions,
           AVG(sentiment) as avg_sentiment
    FROM posts
    GROUP BY DATE(created_utc)
    ORDER BY date DESC;
    """
    rows = await app.state.db.fetch(query)
    return [dict(r) for r in rows]
```

---

## 🗄️ 5. Database Setup (PostgreSQL)

Create a table:

```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    title TEXT,
    subreddit TEXT,
    score INT,
    sentiment FLOAT,
    created_utc TIMESTAMP
);
```

---

## 🧰 6. Docker Setup

`Dockerfile`

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🚦 7. requirements.txt

```
fastapi
uvicorn
asyncpraw
asyncpg
nltk
python-dotenv
```

---

## ☁️ 8. Deployment Plan (Free / Low-cost)

* **Backend:** Deploy FastAPI on **Render** (free).
* **Database:** Use **Neon.tech** PostgreSQL (free tier).
* **Frontend:** Deploy Next.js on **Vercel** (free).
* **CI/CD:** GitHub Actions to auto-deploy on push.
* **Kubernetes:** Optional — use Minikube locally to showcase YAML manifests.

---

## 🧩 9. Next.js Dashboard Ideas

Visuals you can implement easily:

* `/api/stats/daily` → line chart (mentions/day, average sentiment).
* `/api/fetch` → trigger data refresh button.
* `/api/top_keywords` → show top co-occurring words (add later using `collections.Counter`).

Libraries: `Recharts`, `Tremor UI`, or `Chart.js`.

---

## 🎓 10. Portfolio-Ready Additions

✅ Architecture diagram in README
✅ “Deploy with Docker” section
✅ CI/CD workflow badge
✅ Screenshots of dashboard
✅ Optional: Show how you scaled it on Minikube

---

Would you like me to generate next:

* the **Next.js dashboard starter code**, or
* the **Kubernetes + GitHub Actions CI/CD setup** for this project?

(You can then pick which part to work on first.)


okay following this structure generate a startup code for each file

ai-public-eye/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── reddit.py
│   │   ├── news.py
│   │   ├── hn.py
│   ├── services/
│   │   ├── scraper.py       # reusable scraping functions
│   │   ├── sentiment.py     # text analysis (VADER/TextBlob)
│   ├── db/
│   │   ├── mongo.py         # MongoDB connection
│   └── models/
│       ├── article.py
│       ├── post.py
│
├── frontend/
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── trends.tsx
│   ├── components/
│   │   ├── sentimentChart.tsx
│   │   ├── sourceStats.tsx
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│
├── .github/workflows/
│   ├── deploy.yml
│
└── README.md

Nice — below is a **starter code scaffold** for the whole project structure you asked for. It’s minimal, runnable, and focused on getting you from zero → working prototype quickly. I kept the code pragmatic (simple sync scrapers wrapped by FastAPI endpoints) so you can iterate fast and add async/Celery later.

> **How to use:** copy each file into the matching path in your repo. I included comments and TODOs where you’ll want to add secrets or tweak behavior.

---

# Backend

## `backend/main.py`

```python
# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routes import reddit, news, hn
from db.mongo import connect_db, close_db

app = FastAPI(title="AI in the Public Eye - API", version="0.1")

# Allow frontend local dev (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(reddit.router, prefix="/api/reddit", tags=["reddit"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(hn.router, prefix="/api/hn", tags=["hackernews"])

@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
```

---

## `backend/routes/reddit.py`

```python
# backend/routes/reddit.py
from fastapi import APIRouter, HTTPException
from services.scraper import fetch_reddit_posts
from typing import List
from models.post import PostIn

router = APIRouter()

@router.get("/fetch", response_model=dict)
def trigger_fetch(limit: int = 25):
    """
    Fetch recent posts from configured subreddits containing AI keywords.
    """
    try:
        saved = fetch_reddit_posts(limit=limit)
        return {"message": "OK", "saved": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## `backend/routes/news.py`

```python
# backend/routes/news.py
from fastapi import APIRouter, HTTPException
from services.scraper import fetch_news_rss
from typing import List

router = APIRouter()

@router.get("/fetch", response_model=dict)
def fetch_news(q: str = "Artificial Intelligence", limit: int = 20):
    """
    Fetch news articles via Google News RSS (or configured news API).
    """
    try:
        saved = fetch_news_rss(query=q, limit=limit)
        return {"message": "OK", "saved": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## `backend/routes/hn.py`

```python
# backend/routes/hn.py
from fastapi import APIRouter, HTTPException
from services.scraper import fetch_hackernews_ai
router = APIRouter()

@router.get("/fetch", response_model=dict)
def fetch_hn(limit: int = 50):
    """
    Fetch Hacker News top stories and filter those mentioning AI keyword(s).
    """
    try:
        saved = fetch_hackernews_ai(limit=limit)
        return {"message": "OK", "saved": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## `backend/services/scraper.py`

```python
# backend/services/scraper.py
import os
import time
from typing import List, Dict
from datetime import datetime
import requests
import feedparser
from textblob import TextBlob
from models.post import PostIn
from db.mongo import save_post, save_article

# PRAW optional (if you prefer oauth)
try:
    import praw
except Exception:
    praw = None

# settings
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ai-public-eye/0.1")
TARGET_SUBS = os.getenv("TARGET_SUBS", "artificial+MachineLearning+Futurology+technology").split("+")

KEYWORDS = ["ai", "gpt", "openai", "artificial intelligence", "machine learning", "deep learning", "automation"]


def text_mentions_ai(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    return any(k in t for k in KEYWORDS)


def sentiment_score(text: str) -> float:
    if not text:
        return 0.0
    return TextBlob(text).sentiment.polarity


# ---------- Reddit (using PRAW if available) ----------
def fetch_reddit_posts(limit: int = 25) -> int:
    """
    Fetch posts from the target subreddits. Save those which mention AI keywords.
    Returns number saved.
    """
    if not praw:
        raise RuntimeError("praw library is not installed. install praw or change scraper to use requests.")
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    saved = 0
    for sub in TARGET_SUBS:
        try:
            subreddit = reddit.subreddit(sub)
            for post in subreddit.hot(limit=limit):
                if text_mentions_ai(post.title or "") or text_mentions_ai(getattr(post, "selftext", "") or ""):
                    doc = {
                        "id": post.id,
                        "source": "reddit",
                        "subreddit": sub,
                        "title": post.title,
                        "body": getattr(post, "selftext", ""),
                        "score": post.score,
                        "url": post.url,
                        "created_utc": datetime.utcfromtimestamp(post.created_utc),
                        "sentiment": sentiment_score(post.title or post.selftext or "")
                    }
                    save_post(doc)
                    saved += 1
        except Exception:
            # continue for robustness
            continue
    return saved


# ---------- News via Google News RSS ----------
def fetch_news_rss(query: str = "Artificial Intelligence", limit: int = 20) -> int:
    """
    Uses Google News search RSS to fetch news items about query.
    """
    q = query.replace(" ", "+")
    feed_url = f"https://news.google.com/rss/search?q={q}"
    d = feedparser.parse(feed_url)
    saved = 0
    for entry in d.entries[:limit]:
        title = entry.get("title", "")
        summary = entry.get("summary", "") or entry.get("description", "")
        if text_mentions_ai(title) or text_mentions_ai(summary):
            doc = {
                "source": "news",
                "title": title,
                "body": summary,
                "url": entry.get("link"),
                "published": entry.get("published"),
                "sentiment": sentiment_score(title + " " + summary)
            }
            save_article(doc)
            saved += 1
    return saved


# ---------- Hacker News ----------
def fetch_hackernews_ai(limit: int = 50) -> int:
    top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = requests.get(top_url, timeout=10).json()[:limit]
    saved = 0
    for item_id in ids:
        it = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=10).json()
        title = it.get("title", "")
        if text_mentions_ai(title):
            doc = {
                "source": "hackernews",
                "title": title,
                "url": it.get("url"),
                "score": it.get("score"),
                "time": datetime.utcfromtimestamp(it.get("time", time.time())),
                "sentiment": sentiment_score(title)
            }
            save_article(doc)
            saved += 1
    return saved
```

---

## `backend/services/sentiment.py`

```python
# backend/services/sentiment.py
from textblob import TextBlob
from typing import Dict

def analyze_text(text: str) -> Dict[str, float]:
    """
    Return a simple sentiment dict with polarity (-1 .. 1) and subjectivity
    """
    if not text:
        return {"polarity": 0.0, "subjectivity": 0.0}
    tb = TextBlob(text)
    return {"polarity": tb.sentiment.polarity, "subjectivity": tb.sentiment.subjectivity}
```

---

## `backend/db/mongo.py`

```python
# backend/db/mongo.py
import os
import motor.motor_asyncio
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "ai_public_eye")

client = None
db = None

async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    # create indexes
    await db.posts.create_index("id", unique=True, sparse=True)
    await db.articles.create_index("url", unique=True, sparse=True)
    print("Connected to MongoDB")

async def close_db():
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")

# synchronous wrappers for simple scripts (they use asyncio.run)
import asyncio

def save_post(post: dict):
    """Save reddit-style post into 'posts' collection"""
    # ensure created timestamp
    if "created_utc" not in post:
        post["created_utc"] = datetime.utcnow()
    async def _save():
        await db.posts.update_one({"id": post.get("id")}, {"$set": post}, upsert=True)
    return asyncio.get_event_loop().run_until_complete(_save())

def save_article(article: dict):
    if "published" not in article:
        article["published"] = datetime.utcnow().isoformat()
    async def _save():
        await db.articles.update_one({"url": article.get("url")}, {"$set": article}, upsert=True)
    return asyncio.get_event_loop().run_until_complete(_save())
```

> **Note:** `save_post` and `save_article` are synchronous wrappers that call into the async motor client for simplicity. In production, refactor to fully async.

---

## `backend/models/post.py`

```python
# backend/models/post.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostIn(BaseModel):
    id: Optional[str]
    source: str
    subreddit: Optional[str]
    title: str
    body: Optional[str]
    score: Optional[int]
    url: Optional[str]
    created_utc: Optional[datetime]
    sentiment: Optional[float]
```

---

## `backend/models/article.py`

```python
# backend/models/article.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleIn(BaseModel):
    source: str
    title: str
    body: Optional[str]
    url: Optional[str]
    published: Optional[str]
    sentiment: Optional[float]
```

---

# Frontend (Next.js + TypeScript)

> Minimal front-end that calls backend endpoints and renders basic charts. You’ll need to `npm install` packages listed in README.

## `frontend/pages/index.tsx`

```tsx
// frontend/pages/index.tsx
import React from "react";
import Link from "next/link";

export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold mb-4">AI in the Public Eye</h1>
      <p className="mb-6">Dashboard prototype. Use the links below to fetch data from sources and view visualizations.</p>
      <div className="space-x-4">
        <a className="btn" href="/trends">View Trends</a>
        <button
          onClick={async () => {
            await fetch("/api/proxy/reddit/fetch");
            alert("Triggered reddit fetch (proxied)");
          }}
          className="btn"
        >
          Fetch Reddit Now
        </button>
      </div>
      <style jsx>{`
        .btn { padding: 8px 12px; background: #0ea5e9; color: white; border-radius: 6px; }
      `}</style>
    </main>
  );
}
```

---

## `frontend/pages/trends.tsx`

```tsx
// frontend/pages/trends.tsx
import React, { useEffect, useState } from "react";
import SentimentChart from "../components/sentimentChart";
import SourceStats from "../components/sourceStats";

export default function Trends() {
  const [stats, setStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await fetch("/api/proxy/stats/daily");
        const json = await res.json();
        setStats(json);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Trends</h1>
      {loading ? <p>Loading...</p> : (
        <>
          <SentimentChart data={stats} />
          <SourceStats />
        </>
      )}
    </main>
  );
}
```

---

## `frontend/components/sentimentChart.tsx`

```tsx
// frontend/components/sentimentChart.tsx
import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function SentimentChart({ data = [] }: { data: any[] }) {
  const chartData = (data || []).map((d: any) => ({
    date: d.date || d._id?.date || "",
    mentions: Number(d.mentions) || 0,
    avg_sentiment: Number(d.avg_sentiment) || 0
  })).reverse();

  return (
    <div style={{ width: "100%", height: 300 }}>
      <h2 className="text-lg font-semibold mb-2">Mentions & Sentiment over time</h2>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" orientation="left" />
          <YAxis yAxisId="right" orientation="right" domain={[-1, 1]} />
          <Tooltip />
          <Line yAxisId="left" type="monotone" dataKey="mentions" stroke="#8884d8" />
          <Line yAxisId="right" type="monotone" dataKey="avg_sentiment" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## `frontend/components/sourceStats.tsx`

```tsx
// frontend/components/sourceStats.tsx
import React, { useEffect, useState } from "react";

export default function SourceStats() {
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    async function load() {
      const res = await fetch("/api/proxy/source/summary");
      const json = await res.json();
      setStats(json);
    }
    load();
  }, []);

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold">Source Summary</h3>
      <pre>{JSON.stringify(stats, null, 2)}</pre>
    </div>
  );
}
```

> **Note:** For local development it’s convenient to add a Next.js API route that proxies requests to your backend (`/api/proxy/*`) to avoid CORS or to configure CORS on backend (we already do allow frontend origin in `main.py`). I left proxy endpoints referenced above as an exercise to wire in your Next.js app.

---

# Kubernetes manifests

## `k8s/deployment.yaml`

```yaml
# k8s/deployment.yaml - example for backend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-public-eye-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-backend
  template:
    metadata:
      labels:
        app: ai-backend
    spec:
      containers:
        - name: backend
          image: your-dockerhub-username/ai-public-eye-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: MONGO_URI
              valueFrom:
                secretKeyRef:
                  name: mongo-secret
                  key: mongo-uri
            - name: REDDIT_CLIENT_ID
              valueFrom:
                secretKeyRef:
                  name: reddit-secret
                  key: client_id
            - name: REDDIT_CLIENT_SECRET
              valueFrom:
                secretKeyRef:
                  name: reddit-secret
                  key: client_secret
```

---

## `k8s/service.yaml`

```yaml
# k8s/service.yaml - exposes backend within cluster / loadbalancer
apiVersion: v1
kind: Service
metadata:
  name: ai-backend-svc
spec:
  type: NodePort
  selector:
    app: ai-backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
      nodePort: 30080
```

---

# GitHub Actions (CI)

## `.github/workflows/deploy.yml`

```yaml
# .github/workflows/deploy.yml - template CI workflow
name: CI - Test & Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt

      - name: Run backend lint (optional)
        run: |
          echo "No tests configured - add your tests here"

  build-and-push-docker:
    runs-on: ubuntu-latest
    needs: lint-and-test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push backend image
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/ai-public-eye-backend:latest
          context: ./backend
```

> **Note:** This workflow pushes Docker images to Docker Hub. To auto-deploy to services like Render/Fly/Vercel, add provider-specific deploy steps and secrets. Keep secrets safe in GitHub repo settings.

---

# README.md (starter)

```md
# AI in the Public Eye

Prototype project that collects public mentions of "AI" from multiple sources (Reddit, Google News RSS, Hacker News), runs simple sentiment analysis, stores results in MongoDB, and exposes endpoints for a Next.js dashboard.

## Quickstart (local)

### Prereqs
- Python 3.11+
- Node 18+
- MongoDB (local) or Mongo Atlas
- Docker (optional)

### Backend
1. Copy `.env` values:
```

MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_public_eye
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=ai-public-eye/0.1

````
2. Install deps:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
````

### Frontend

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

## Endpoints

* `GET /api/reddit/fetch` — trigger reddit fetch
* `GET /api/news/fetch` — fetch news rss
* `GET /api/hn/fetch` — fetch hackernews top stories
* `GET /api/stats/daily` — (TODO) you can add aggregation endpoint returning daily stats

## Deployment

* Dockerize backend & frontend (Dockerfiles)
* Use GitHub Actions to build and push images
* Use Render / Fly / Vercel (free tiers) to host frontend/backend and Neon or Mongo Atlas for DB

## Next steps

* Move scrapers to async or background worker (Celery/RQ)
* Add more robust NLP (spaCy / transformers)
* Add authentication for dashboard
* Add Kubernetes manifests for prod demo

```

---

# `backend/requirements.txt` (add)
```

fastapi
uvicorn[standard]
praw
requests
feedparser
textblob
motor
python-dotenv

```

> After installing `textblob`, run `python -m textblob.download_corpora` locally if needed (or `nltk` downloads if you switch to `vader`).

---

## Final notes & suggestions
- I purposely kept scrapers simple so you can get a working MVP quickly. For production-readiness:
  - Move scrapers into background workers (Celery + Redis) or Kubernetes CronJobs.
  - Make DB operations fully async and robust with retries.
  - Add rate-limiting and exponential backoff when calling APIs.
- For cost control (≤ $15/month):
  - Use free tiers: Vercel for frontend, Render or Fly for backend free plan, Neon/Free Mongo Atlas for DB.
  - Keep scrapes infrequent (hourly or daily) to avoid API limits and compute time.

---

If you want, I can now:
- generate `Dockerfile`s for backend & frontend,
- add a Next.js API proxy for `/api/proxy/*` calls to your FastAPI backend,
- or create a ready-to-use `docker-compose.yml` to run everything locally.

Which of those would you like next?
```
