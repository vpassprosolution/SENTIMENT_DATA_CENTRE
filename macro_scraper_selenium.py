import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database import save_macro_data_to_db
import time

def scrape_macro_data():
    print("\n🤖 Scraping macroeconomic data...")  # Confirm function is triggered

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Start the Chrome browser
    driver = uc.Chrome(options=options)
    print("✅ Headless Chrome started...")  # Confirm the browser has started

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
        print(f"✅ Scraping {item['name']}...")  # Confirm which item we are scraping

        try:
            # Try loading the page and wait for 10 seconds for the value element to appear
            driver.get(item["url"])
            print(f"✅ Loaded {item['name']} URL...")  # Confirm URL was loaded

            # Wait until the macro value element is loaded
            value_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "datatable-item-value"))
            )
            value = value_element.text.strip()
            print(f"✅ Scraped value for {item['name']}: {value}")  # Print the scraped value

            # Add data to macro_data list
            macro_data.append({
                "indicator": item["name"],
                "value": value,
                "unit": item["unit"],
                "country": "USA",
                "source": "TradingEconomics"
            })

        except Exception as e:
            print(f"⚠️ Failed to scrape {item['name']}: {e}")  # Log the error if it occurs

    # Close the browser after scraping
    driver.quit()

    if macro_data:
        print(f"✅ Saving {len(macro_data)} macro indicators to the database...")  # Debugging line
        save_macro_data_to_db(macro_data)
    else:
        print("⚠️ No macro data was collected.")
