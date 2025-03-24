import requests
from bs4 import BeautifulSoup
from database import save_macro_data_to_db
from database import save_macro_events_to_db
from datetime import datetime

# ✅ Helper function to extract value from TradingEconomics
def get_indicator_from_te(url, indicator_name, unit):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ This class usually contains the value
        value_div = soup.find("div", class_="pull-left")
        value = value_div.text.strip() if value_div else "N/A"

        print(f"✅ {indicator_name}: {value} {unit}")
        return {
            "indicator": indicator_name,
            "value": value,
            "unit": unit,
            "country": "USA",
            "source": "TradingEconomics"
        }
    except Exception as e:
        print(f"⚠️ Error scraping {indicator_name}: {e}")
        return None

# ✅ Main scraper function
def scrape_macro_data():
    print("\n🌐 Scraping macroeconomic indicators from TradingEconomics...\n")
    macro_data = []

    urls = [
        {
            "url": "https://tradingeconomics.com/united-states/gdp-growth",
            "indicator": "GDP Growth",
            "unit": "%"
        },
        {
            "url": "https://tradingeconomics.com/united-states/inflation-cpi",
            "indicator": "Inflation Rate",
            "unit": "%"
        },
        {
            "url": "https://tradingeconomics.com/united-states/unemployment-rate",
            "indicator": "Unemployment Rate",
            "unit": "%"
        },
        {
            "url": "https://tradingeconomics.com/united-states/interest-rate",
            "indicator": "Interest Rate (Fed)",
            "unit": "%"
        },
        {
            "url": "https://tradingeconomics.com/united-states/retail-sales",
            "indicator": "Retail Sales (MoM)",
            "unit": "%"
        },
        {
            "url": "https://tradingeconomics.com/united-states/industrial-production",
            "indicator": "Industrial Production",
            "unit": "%"
        }
    ]

    for item in urls:
        result = get_indicator_from_te(item["url"], item["indicator"], item["unit"])
        if result:
            macro_data.append(result)

    if macro_data:
        save_macro_data_to_db(macro_data)
    else:
        print("⚠️ No macroeconomic data was scraped.")
    scrape_fed_meeting_date()

def scrape_fed_meeting_date():
    print("\n📅 Scraping next Fed meeting date...\n")
    try:
        url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Find the first meeting table row
        meeting_table = soup.find("table", {"class": "fomc-meeting-calendars"})
        rows = meeting_table.find_all("tr")[1:]  # skip header

        next_event = None
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 1:
                date_text = cells[0].get_text(strip=True)
                try:
                    event_date = datetime.strptime(date_text, "%B %d-%d, %Y")
                except:
                    try:
                        event_date = datetime.strptime(date_text, "%B %d, %Y")
                    except:
                        continue

                next_event = {
                    "event_name": "FOMC Meeting",
                    "event_date": event_date.date(),
                    "source": "FederalReserve.gov"
                }
                break

        if next_event:
            save_macro_events_to_db([next_event])
        else:
            print("⚠️ No Fed meeting date found.")

    except Exception as e:
        print(f"⚠️ Error scraping Fed calendar: {e}")
