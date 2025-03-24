import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from database import save_macro_data_to_db
import time

def scrape_macro_data():
    print("\n🤖 Launching headless browser to scrape macroeconomic data...\n")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options)

    indicators = [
        {"name": "GDP Growth", "url": "https://tradingeconomics.com/united-states/gdp-growth", "unit": "%"},
        {"name": "Inflation Rate", "url": "https://tradingeconomics.com/united-states/inflation-cpi", "unit": "%"},
        {"name": "Unemployment Rate", "url": "https://tradingeconomics.com/united-states/unemployment-rate", "unit": "%"},
        {"name": "Interest Rate (Fed)", "url": "https://tradingeconomics.com/united-states/interest-rate", "unit": "%"},
        {"name": "Retail Sales (MoM)", "url": "https://tradingeconomics.com/united-states/retail-sales", "unit": "%"},
        {"name": "Industrial Production", "url": "https://tradingeconomics.com/united-states/industrial-production", "unit": "%"},
    ]

    macro_data = []

    for item in indicators:
        try:
            driver.get(item["url"])
            time.sleep(5)  # Wait for page to load JS

            value_element = driver.find_element(By.CLASS_NAME, "datatable-item-value")
            value = value_element.text.strip()

            print(f"✅ {item['name']}: {value} {item['unit']}")

            macro_data.append({
                "indicator": item["name"],
                "value": value,
                "unit": item["unit"],
                "country": "USA",
                "source": "TradingEconomics"
            })
        except Exception as e:
            print(f"⚠️ Failed to scrape {item['name']}: {e}")

    driver.quit()

    if macro_data:
        save_macro_data_to_db(macro_data)
        print("✅ All macro data saved.")
    else:
        print("⚠️ No macro data was collected.")
