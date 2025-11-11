from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    USER_AGENT: str
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "news"
    NEWSAPI_KEY: str
    TARGET_SUBS: str = 'Futurology+worldnews+technology+MachineLearning+artificial'
    KEYWORDS: str = "ai+artificial intelligence+machine learning+ml+deep learning+gpt+openai+chatgpt+llm+neural network"

    class Config:
        env_file = ".env"
        extra="ignore"


settings = Settings()
