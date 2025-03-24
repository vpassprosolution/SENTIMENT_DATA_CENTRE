import requests
from database import save_macro_data_to_db

TRADINGECONOMICS_API = "0feda09f7305492:q7z83h8t87sjt2y"

def fetch_macro_data_from_api():
    print("\n🌐 Fetching macroeconomic indicators from TradingEconomics API...\n")

    indicators = {
        "GDP Growth": "United States GDP Growth Rate",
        "Inflation Rate": "United States Inflation Rate",
        "Unemployment Rate": "United States Unemployment Rate",
        "Interest Rate (Fed)": "United States Interest Rate",
        "Retail Sales (MoM)": "United States Retail Sales MoM",
        "Industrial Production": "United States Industrial Production"
    }

    base_url = "https://api.tradingeconomics.com/historical/country/united states/indicator"
    headers = {"Accept": "application/json"}
    macro_data = []

    for label, indicator in indicators.items():
        url = f"{base_url}/{indicator.replace(' ', '%20')}?c={TRADINGECONOMICS_API}&format=json"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                latest = data[0]
                value = latest["Value"]
                unit = "%"  # Most are %, you can adjust later if needed
                print(f"✅ {label}: {value} {unit}")

                macro_data.append({
                    "indicator": label,
                    "value": str(value),
                    "unit": unit,
                    "country": "USA",
                    "source": "TradingEconomics API"
                })
            else:
                print(f"⚠️ No data for {label}")
        except Exception as e:
            print(f"⚠️ Error fetching {label}: {e}")

    if macro_data:
        save_macro_data_to_db(macro_data)
        print("✅ All macroeconomic data saved.")
    else:
        print("⚠️ No macroeconomic data was collected.")
