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

# ✅ NEW FUNCTION: Save macroeconomic data
def save_macro_data_to_db(data_list):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    # ✅ Create macro_data table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_data (
            id SERIAL PRIMARY KEY,
            indicator TEXT,
            value TEXT,
            unit TEXT,
            country TEXT,
            source TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    for data in data_list:
        cursor.execute("""
            INSERT INTO macro_data (indicator, value, unit, country, source)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["indicator"],
            data["value"],
            data["unit"],
            data["country"],
            data["source"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Macroeconomic data saved to PostgreSQL database.")

# Existing function: save news articles
def save_news_to_db(news_list):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for news in news_list:
        instrument = news["instrument"].replace("/", "-")
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

# Save real-time prices
def save_prices_to_db(prices):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    for instrument, price in prices.items():
        if instrument == "XAUUSD":
            instrument = "gold"
        else:
            instrument = instrument.replace("/", "-")

        cursor.execute("""
            INSERT INTO market_prices (instrument, price, timestamp)
            VALUES (%s, %s, NOW())
        """, (instrument, float(price)))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Market prices saved to PostgreSQL database.")

# Save AI price predictions
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

# Save trade recommendations
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

# Save AI risk analysis
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

# ✅ Save Fed Events (e.g., Fed Meetings)
def save_macro_events_to_db(events):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_events (
            id SERIAL PRIMARY KEY,
            event_name TEXT,
            event_date DATE,
            source TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    for event in events:
        cursor.execute("""
            INSERT INTO macro_events (event_name, event_date, source)
            VALUES (%s, %s, %s)
        """, (
            event["event_name"],
            event["event_date"],
            event["source"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Fed events saved to PostgreSQL database.")
