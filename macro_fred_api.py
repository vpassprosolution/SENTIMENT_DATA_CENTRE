import requests
from database import save_macro_data_to_db
from database import connect_db


FRED_API_KEY = "d3d8486d9bbc4abe1f05678dd6d08301"

INDICATOR_SERIES = {
    "GDP Growth": "GDP",
    "Inflation Rate": "CPIAUCNS",
    "Unemployment Rate": "UNRATE",
    "Interest Rate (Fed)": "FEDFUNDS",
    "Retail Sales (MoM)": "RSXFS",
    "Industrial Production": "INDPRO"
}

def save_macro_data_to_db(macro_data):
    conn = connect_db()  
    cursor = conn.cursor()

    # ✅ Delete old macroeconomic data before inserting new
    cursor.execute("DELETE FROM macro_data")

    # ✅ Insert new macroeconomic data
    for entry in macro_data:
        cursor.execute("""
            INSERT INTO macro_data (indicator, value, unit, country, source)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            entry["indicator"],
            entry["value"],
            entry["unit"],
            entry["country"],
            entry["source"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Macro data updated: old data deleted, new data saved.")

def fetch_macro_data_from_api():
    print("\n🌐 Fetching macroeconomic indicators from FRED API...\n")
    macro_data = []

    for label, series_id in INDICATOR_SERIES.items():
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if "observations" in data and len(data["observations"]) > 0:
                latest = data["observations"][-1]
                value = latest.get("value", "N/A")
                print(f"✅ {label}: {value}")

                macro_data.append({
                    "indicator": label,
                    "value": value,
                    "unit": "%",
                    "country": "USA",
                    "source": "FRED API"
                })
            else:
                print(f"⚠️ No data found for {label}")
        except Exception as e:
            print(f"⚠️ Error fetching {label}: {e}")

    if macro_data:
        save_macro_data_to_db(macro_data)
        print("✅ All macroeconomic data saved to database.")
    else:
        print("⚠️ No macroeconomic data was collected.")

