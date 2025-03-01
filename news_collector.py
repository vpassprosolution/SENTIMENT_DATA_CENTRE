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
    # Trying "XAUUSD" instead of "USDXAU"
    url = f"https://metals-api.com/api/latest?access_key={METALS_API_KEY}&base=USD&symbols=XAUUSD"
    
    try:
        response = requests.get(url)
        data = response.json()

        # Print full API response for debugging
        print(f"🔍 Metals-API Response: {json.dumps(data, indent=2)}")

        # Check if request was successful
        if data.get("success") and "rates" in data and "XAUUSD" in data["rates"]:
            gold_price = round(float(data["rates"]["XAUUSD"]), 2)
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
    # Fetch Gold Price from Metals-API
    gold_price = fetch_gold_price()
    if gold_price:
        prices["gold"] = gold_price
    # Fetch other market prices from Yahoo Finance
    for instrument, symbol in MARKET_SYMBOLS.items():
        if instrument == "gold":
            continue
        try:
            stock = yf.Ticker(symbol)
            latest_price = stock.history(period="1d")["Close"].iloc[-1]
            prices[instrument] = round(float(latest_price), 2)
            print(f"✅ {instrument} Price: {prices[instrument]}")
        except Exception as e:
            print(f"⚠️ Failed to fetch price for {instrument}: {e}")
    return prices

# Function to predict Bullish/Bearish trends based on market prices
def predict_price_trends(market_prices):
    print("\n🤖 Predicting Market Trends...\n")
    predictions = {}
    for instrument, price in market_prices.items():
        try:
            stock = yf.Ticker(MARKET_SYMBOLS[instrument])
            history = stock.history(period="2d")  # Get last 2 days
            if len(history) < 2:
                print(f"⚠️ Not enough data for {instrument}")
                continue
            prev_price = history["Close"].iloc[-2]
            current_price = history["Close"].iloc[-1]
            if current_price > prev_price:
                trend = "Bullish"
                confidence = 85.0
            else:
                trend = "Bearish"
                confidence = 85.0
            predictions[instrument] = {"trend": trend, "confidence": confidence}
            print(f"✅ {instrument} Prediction: {trend} (Confidence: {confidence}%)")
        except Exception as e:
            print(f"⚠️ Failed to predict trend for {instrument}: {e}")
    return predictions

# Function to generate AI Trade Recommendations using sentiment and predictions
def generate_trade_recommendations(price_predictions, news_data):
    print("\n📊 Generating AI Trade Recommendations...\n")
    recommendations = {}
    for instrument, prediction in price_predictions.items():
        trend = prediction["trend"]
        confidence = prediction["confidence"]
        latest_sentiment = "Neutral"
        for news in news_data:
            if news["instrument"] == instrument:
                latest_sentiment = news["sentiment"]
                break
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
