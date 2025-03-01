import requests
import json
import time
import os
from datetime import datetime
from settings import NEWS_API_KEY, GNEWS_API_KEY, INSTRUMENTS, MARKET_SYMBOLS, METALS_API_KEY
from database import save_news_to_db, save_prices_to_db, save_price_predictions_to_db, save_trade_recommendations_to_db, save_news_risks_to_db
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import yfinance as yf
import nltk

# Ensure vader_lexicon is downloaded
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Function to analyze sentiment of a news article
def analyze_sentiment(text):
    if not text:
        return "Neutral"
    
    sentiment_score = sia.polarity_scores(text)["compound"]
    if sentiment_score >= 0.3:
        return "Bullish"
    elif sentiment_score <= -0.3:
        return "Bearish"
    else:
        return "Neutral"

# Function to fetch news from NewsAPI
def fetch_newsapi_news():
    url = "https://newsapi.org/v2/everything"
    news_data = []
    for instrument, keyword in INSTRUMENTS.items():
        params = {
            "q": keyword,
            "apiKey": NEWS_API_KEY,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }
        response = requests.get(url, params=params)
        print(f"\n🔎 NewsAPI Response for {instrument}: {response.status_code}")
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            for article in articles:
                sentiment = analyze_sentiment(article.get("title", "") + " " + article.get("description", ""))
                news_data.append({
                    "source": "NewsAPI",
                    "instrument": instrument,
                    "title": article.get("title", "No Title"),
                    "description": article.get("description", "No Description"),
                    "url": article.get("url", "#"),
                    "published_at": article.get("publishedAt", "N/A"),
                    "sentiment": sentiment
                })
        elif response.status_code == 429:
            print("🛑 NewsAPI Rate Limit Reached! Waiting 10 minutes before retrying...")
            time.sleep(600)
            return fetch_newsapi_news()
        else:
            print(f"⚠️ Failed to fetch NewsAPI data for {instrument}. Status Code: {response.status_code}")
        time.sleep(10)
    return news_data

# Function to fetch Gold (XAU/USD) price from Metals-API
def fetch_gold_price():
    print("\n📈 Fetching Gold (XAU/USD) price from Metals-API...\n")
    
    # Using "XAU" as the correct Metals-API symbol
    url = f"https://metals-api.com/api/latest?access_key={METALS_API_KEY}&base=USD&symbols=XAU"

    try:
        response = requests.get(url)
        data = response.json()

        # Print full API response for debugging
        print(f"🔍 Metals-API Response: {json.dumps(data, indent=2)}")

        # Validate response and extract the correct Gold price
        if data.get("success") and "rates" in data and "XAU" in data["rates"]:
            gold_price_per_ounce = float(data["rates"]["XAU"])
            gold_price = round((1 / gold_price_per_ounce), 2)  # Convert XAU to USD

            print(f"✅ Gold (XAU/USD) Price (Formatted): {gold_price}")
            return gold_price
        else:
            print(f"⚠️ Failed to fetch Gold price. API Response: {data}")
            return None
    except Exception as e:
        print(f"⚠️ Error fetching Gold price: {e}")
        return None

# Function to fetch real-time market prices
def fetch_market_prices():
    print("\n📈 Fetching real-time market prices...\n")
    prices = {}

    # Fetch Gold Price from Metals-API (ONLY)
    gold_price = fetch_gold_price()
    if gold_price:
        prices["XAUUSD"] = gold_price  # Store Gold price as XAUUSD
    else:
        print("⚠️ Warning: Gold price not available.")

    # Fetch other market prices from Yahoo Finance (EXCLUDING Gold)
    for instrument, symbol in MARKET_SYMBOLS.items():
        if instrument == "gold" or symbol == "XAUUSD=X":  # Skip Gold
            continue
        try:
            stock = yf.Ticker(symbol)
            latest_price = stock.history(period="1d")["Close"].iloc[-1]
            prices[instrument] = round(float(latest_price), 2)
            print(f"✅ {instrument} Price: {prices[instrument]}")
        except Exception as e:
            print(f"⚠️ Failed to fetch price for {instrument}: {e}")

    return prices

# Main function to collect and store financial data
def collect_financial_data():
    print("\n🚀 Fetching latest financial news, market prices, and AI predictions...\n")
    
    # Fetch News and Sentiment
    news_list = fetch_newsapi_news()
    save_news_to_db(news_list)
    
    # Detect Risks from News
    news_risks = detect_risks_from_news(news_list)
    save_news_risks_to_db(news_risks)
    
    # Fetch Market Prices
    market_prices = fetch_market_prices()
    save_prices_to_db(market_prices)
    
    # Generate AI Price Predictions
    price_predictions = predict_price_trends(market_prices)
    save_price_predictions_to_db(price_predictions)
    
    # Generate AI Trade Recommendations
    trade_recommendations = generate_trade_recommendations(price_predictions, news_list)
    save_trade_recommendations_to_db(trade_recommendations)

    print("✅ Data collection complete. Waiting for next update.")

if __name__ == "__main__":
    while True:
        collect_financial_data()
        print("⏳ Waiting 2 hours before next fetch...\n")
        time.sleep(7200)
