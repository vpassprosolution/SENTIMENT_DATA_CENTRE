import psycopg2
from settings import POSTGRESQL_URL

# Function to connect to PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(POSTGRESQL_URL)
        print("✅ Connected to Railway PostgreSQL database.")
        return conn
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        return None

# Function to save news data to the database
def save_news_to_db(news_list):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for news in news_list:
        instrument = news["instrument"].replace("/", "-")  # Convert '/' to '-'
        cursor.execute("""
            INSERT INTO news_articles (source, instrument, title, description, url, published_at, sentiment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            news["source"],
            instrument,
            news["title"],
            news["description"],
            news["url"],
            news["published_at"],
            news["sentiment"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ News data (with sentiment) saved to PostgreSQL database.")

# ✅ Function to save real-time prices to the database (Fix for Gold/XAUUSD)
def save_prices_to_db(prices):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for instrument, price in prices.items():
        # ✅ Convert "XAUUSD" to "gold" before saving
        if instrument == "XAUUSD":
            instrument = "gold"
        else:
            instrument = instrument.replace("/", "-")  # Convert '/' to '-'

        cursor.execute("""
            INSERT INTO market_prices (instrument, price, timestamp)
            VALUES (%s, %s, NOW())
        """, (instrument, float(price)))  # Ensure price is stored as a Python float

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Market prices saved to PostgreSQL database.")

# ✅ Function to save AI price predictions to the database (Fix for Gold/XAUUSD)
def save_price_predictions_to_db(predictions):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for instrument, prediction in predictions.items():
        if instrument == "XAUUSD":
            instrument = "gold"
        else:
            instrument = instrument.replace("/", "-")

        cursor.execute("""
            INSERT INTO price_predictions (instrument, trend, confidence, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (
            instrument,
            prediction["trend"],
            prediction["confidence"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ AI Price Predictions saved to PostgreSQL database.")

# ✅ Function to save AI-generated Buy/Sell/Hold recommendations (Fix for Gold/XAUUSD)
def save_trade_recommendations_to_db(recommendations):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for instrument, recommendation in recommendations.items():
        if instrument == "XAUUSD":
            instrument = "gold"
        else:
            instrument = instrument.replace("/", "-")

        cursor.execute("""
            INSERT INTO trade_recommendations (instrument, recommendation, confidence, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (
            instrument,
            recommendation["action"],
            recommendation["confidence"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ AI Trade Recommendations saved to PostgreSQL database.")

# ✅ Function to save AI-detected risks from financial news to the database (Fix for Gold/XAUUSD)
def save_news_risks_to_db(risks):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for instrument, risk in risks.items():
        if instrument == "XAUUSD":
            instrument = "gold"
        else:
            instrument = instrument.replace("/", "-")

        cursor.execute("""
            INSERT INTO news_risks (instrument, risk_level, risk_reason, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (
            instrument,
            risk["risk_level"],
            risk["risk_reason"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ AI Risk Analysis saved to PostgreSQL database.")
