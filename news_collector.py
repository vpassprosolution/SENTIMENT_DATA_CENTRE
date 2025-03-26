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
import psycopg2  # ✅ Add this line
from settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from macro_fred_api import fetch_macro_data_from_api

# ✅ Consistent format for instruments (e.g., "eur/usd" → "eur-usd")
def format_instrument_name(instrument):
    return instrument.lower().replace("/", "-")


# Ensure vader_lexicon is downloaded
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# ✅ Strong financial keywords to filter relevant news
FINANCIAL_KEYWORDS = [
    "central bank", "economic", "commodities", "stocks",
    "war", "wars", "bitcoin", "eth", "inflation", "risk sentiment"
]





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

# ✅ New Function: Filter only financial news
def is_financial_news(title, description, instrument):
    text = (title + " " + description).lower()
    has_financial_term = any(keyword in text for keyword in FINANCIAL_KEYWORDS)
    
    # Check if instrument is clearly mentioned
    instrument_keywords = {
        "gold": ["gold", "xauusd"],
        "bitcoin": ["bitcoin", "btc"],
        "ethereum": ["ethereum", "eth"],
        "dow jones": ["dow", "dji"],
        "nasdaq": ["nasdaq", "ixic"],
        "eur/usd": ["eurusd", "eur/usd", "euro dollar"],
        "gbp/usd": ["gbpusd", "gbp/usd", "pound dollar"]
    }

    relevant = any(word in text for word in instrument_keywords.get(instrument, []))

    return has_financial_term and relevant

# ✅ Function to Delete Old Data from All 5 Tables
def delete_old_news():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        print("🗑️ Deleting old data...")

        cursor.execute("DELETE FROM news_articles;")
        print("✅ Deleted: news_articles")

        cursor.execute("DELETE FROM news_risks;")
        print("✅ Deleted: news_risks")

        cursor.execute("DELETE FROM price_predictions;")
        print("✅ Deleted: price_predictions")

        cursor.execute("DELETE FROM trade_recommendations;")
        print("✅ Deleted: trade_recommendations")

        cursor.execute("DELETE FROM market_prices;")
        print("✅ Deleted: market_prices")

        cursor.execute("DELETE FROM macro_data;")
        print("✅ Deleted: macro_data")

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ All old data deleted and committed.")

    except Exception as e:
        print(f"⚠️ Error deleting old data: {e}")



# Function to fetch news from NewsAPI
def fetch_newsapi_news():
    url = "https://newsapi.org/v2/everything"
    news_data = []

    for instrument, keyword in INSTRUMENTS.items():
        if instrument == "gold":
            # Updated Gold keywords to include "gold trump" and "gold usd"
            keyword = "gold price OR gold market OR XAUUSD OR gold trading OR gold trump OR gold usd"
        elif instrument == "eur/usd":
            keyword = "eur/usd OR euro dollar OR EURUSD"
        elif instrument == "gbp/usd":
            keyword = "gbp/usd OR pound dollar OR GBPUSD"

        filtered_articles = []
        page = 1

        while len(filtered_articles) < 3 and page <= 3:  # Retry up to 3 pages max
            params = {
                "q": keyword,
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "page": page
            }

            response = requests.get(url, params=params)
            print(f"\n🔎 NewsAPI Response for {instrument} (Page {page}): {response.status_code}")

            if response.status_code == 200:
                articles = response.json().get("articles", [])

                for article in articles:
                    title = article.get("title") or "No Title"
                    description = article.get("description") or "No Description"

                    print(f"DEBUG: Title: {title}")
                    print(f"DEBUG: Description: {description}")

                    sentiment = analyze_sentiment(title + " " + description)

                    if is_financial_news(title, description, instrument) and sentiment != "Neutral":
                        filtered_articles.append({
                            "source": "NewsAPI",
                            "instrument": instrument,
                            "title": title,
                            "description": description,
                            "url": article.get("url", "#"),
                            "published_at": article.get("publishedAt", "N/A"),
                            "sentiment": sentiment
                        })

                    if len(filtered_articles) == 3:
                        break

                page += 1
                time.sleep(1)  # Prevent rate limit

            elif response.status_code == 429:
                print("🛑 NewsAPI Rate Limit Reached! Waiting 10 minutes before retrying...")
                time.sleep(600)
                continue

            else:
                print(f"⚠️ Failed to fetch NewsAPI data for {instrument}. Status Code: {response.status_code}")
                break

        # Final fallback if less than 3 were collected
        if len(filtered_articles) < 3:
            print(f"⚠️ WARNING: Only found {len(filtered_articles)} news for {instrument}!")
        else:
            print(f"✅ {instrument}: 3 news collected.")

        news_data.extend(filtered_articles)
        time.sleep(2)  # Additional pause between instruments

    return news_data




# Function to fetch Gold (XAU/USD) price from Metals-API
def fetch_gold_price():
    print("\n📈 Fetching Gold (XAU/USD) price from Metals-API...\n")
    
    url = f"https://metals-api.com/api/latest?access_key={METALS_API_KEY}&base=USD&symbols=XAU"

    try:
        response = requests.get(url)
        data = response.json()
        print(f"🔍 Metals-API Response: {json.dumps(data, indent=2)}")

        if data.get("success") and "rates" in data and "XAU" in data["rates"]:
            gold_price_per_ounce = float(data["rates"]["XAU"])
            gold_price = round((1 / gold_price_per_ounce), 2)
            
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

    gold_price = fetch_gold_price()
    if gold_price:
        prices["XAUUSD"] = gold_price  
    else:
        print("⚠️ Warning: Gold price not available.")

    for instrument, symbol in MARKET_SYMBOLS.items():
        if instrument.lower() == "gold" or symbol == "XAUUSD=X":  
            continue
        try:
            stock = yf.Ticker(symbol)
            latest_price = stock.history(period="1d")["Close"].iloc[-1]
            prices[instrument] = round(float(latest_price), 2)
            print(f"✅ {instrument} Price: {prices[instrument]}")
        except Exception as e:
            print(f"⚠️ Failed to fetch price for {instrument}: {e}")

    return prices

# ✅ Function to Predict Market Trends (Fix for Gold/XAUUSD)
def predict_price_trends(market_prices):
    print("\n🤖 Predicting Market Trends...\n")
    predictions = {}

    for instrument, price in market_prices.items():
        try:
            # ✅ Convert "XAUUSD" to "gold" for consistency
            if instrument == "XAUUSD":
                instrument = "gold"

            # ✅ Special handling for Gold (XAU/USD) since it is not available in Yahoo Finance
            if instrument == "gold":
                prev_price = price  # Use the current price as previous price (no historical data)
                current_price = price  # Keep the same for now

            else:
                # ✅ Fetch historical data from Yahoo Finance for other instruments
                stock = yf.Ticker(MARKET_SYMBOLS.get(instrument, instrument))
                history = stock.history(period="2d")  # Get last 2 days of data

                if len(history) < 2:
                    print(f"⚠️ Not enough data for {instrument}")
                    continue

                prev_price = history["Close"].iloc[-2]
                current_price = history["Close"].iloc[-1]

            # ✅ Compare price to determine trend
            trend = "Bullish" if current_price > prev_price else "Bearish"
            confidence = 85.0  # Static confidence level

            predictions[instrument] = {"trend": trend, "confidence": confidence}
            print(f"✅ {instrument} Prediction: {trend} (Confidence: {confidence}%)")

        except Exception as e:
            print(f"⚠️ Failed to predict trend for {instrument}: {e}")

    return predictions


# Function to detect risks in financial news
def detect_risks_from_news(news_data):
    print("\n⚠️ Detecting Market Risks from News...\n")
    risks = {}
    risk_keywords = {
        "market crash": "High",
        "recession": "High",
        "economic downturn": "High",
        "inflation": "Medium",
        "regulation": "Medium",
        "interest rate hike": "Medium",
        "volatility": "Low",
        "uncertainty": "Low"
    }
    for news in news_data:
        instrument = news["instrument"]
        title = news["title"].lower()
        description = news["description"].lower()
        combined_text = f"{title} {description}"
        detected_risk = None
        risk_level = "Low"
        for keyword, level in risk_keywords.items():
            if keyword in combined_text:
                detected_risk = keyword
                risk_level = level
                break
        if detected_risk:
            risks[instrument] = {
                "risk_level": risk_level,
                "risk_reason": detected_risk
            }
            print(f"⚠️ {instrument} Risk: {risk_level} due to {detected_risk}")
    return risks

# ✅ Function to Generate AI Trade Recommendations
def generate_trade_recommendations(price_predictions, news_data):
    print("\n📊 Generating AI Trade Recommendations...\n")
    recommendations = {}

    if not price_predictions:
        print("⚠️ No price predictions found.")
        return recommendations

    print(f"🧠 Found {len(price_predictions)} price predictions.")
    print(f"📰 Found {len(news_data)} news articles.")

    for instrument, prediction in price_predictions.items():
        trend = prediction["trend"]
        confidence = prediction["confidence"]
        latest_sentiment = "Neutral"

        print(f"🔍 Checking sentiment for: {instrument} | Trend: {trend}")

        for news in news_data:
            if news.get("instrument") == instrument:
                latest_sentiment = news.get("sentiment", "Neutral")
                print(f"🗞️ Matched news: {news['title']} → Sentiment: {latest_sentiment}")
                break

        # Determine trade action
        if trend == "Bullish" and latest_sentiment == "Bullish":
            action = "BUY"
            confidence = 90.0
        elif trend == "Bearish" and latest_sentiment == "Bearish":
            action = "SELL"
            confidence = 90.0
        else:
            action = "HOLD"
            confidence = 70.0

        recommendations[instrument] = {"action": action, "confidence": confidence}
        print(f"✅ {instrument} Trade Recommendation: {action} (Confidence: {confidence}%)")

    return recommendations



# ✅ Main function to collect and store financial data
def collect_financial_data():
    print("\n🚀 Fetching latest financial news, market prices, and AI predictions...\n")
    
    # ✅ Step 1: Delete Old News Before Storing New Data
    delete_old_news()
    
    # ✅ Step 2: Fetch Latest News
    news_list = fetch_newsapi_news()
    save_news_to_db(news_list)

    # ✅ Step 3: Analyze Risks from News
    news_risks = detect_risks_from_news(news_list)
    save_news_risks_to_db(news_risks)

    # ✅ Step 4: Fetch Real-Time Market Prices
    market_prices = fetch_market_prices()
    save_prices_to_db(market_prices)

    # ✅ Step 5: Predict Market Trends
    price_predictions = predict_price_trends(market_prices)
    save_price_predictions_to_db(price_predictions)

    # ✅ Step 6: Generate AI Trade Recommendations
    trade_recommendations = generate_trade_recommendations(price_predictions, news_list)
    save_trade_recommendations_to_db(trade_recommendations)
    # ✅ Step 7: Scrape and Save Macroeconomic Data
    fetch_macro_data_from_api()  # 


    print("✅ Data collection complete. Waiting for next update.")


# ✅ Run the Script Every 2 Hours
if __name__ == "__main__":
    while True:
        collect_financial_data()
        print("⏳ Waiting 2 hours before next fetch...\n")
        time.sleep(14400)

