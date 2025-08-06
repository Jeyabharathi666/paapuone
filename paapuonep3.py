from playwright.sync_api import sync_playwright
from datetime import datetime
import google_sheets  # assumes you have this module ready like in your Economic Times script
import time
URL = ["https://chartink.com/screener/copy-bearish-engulifing-see-after-3-15-pm-for-next-day-trade-5168",
       "https://chartink.com/screener/copy-bearish-maribozu-337",
       "https://chartink.com/screener/copy-yesterday-and-today-ema3-without-open-high-bearish-55",
       "https://chartink.com/screener/copy-bearish-engulfing-moderate-478",
       "https://chartink.com/screener/agp-bearong-2",
       "https://chartink.com/screener/shesha-bearish1",
       "https://chartink.com/screener/agp-shesha-bearish-2",
       "https://chartink.com/screener/one-rupee-sidh-f-0-sell",
       "https://chartink.com/screener/copy-f-o-weak-stocks-2",
       "https://chartink.com/screener/svp2-closing-3-up-since-3-days",
       "https://chartink.com/screener/copy-copy-how-to-find-future-and-option-stocks-buy-entry-future-3",
       "https://chartink.com/screener/copy-stocks-in-downtrend-1959",
       "https://chartink.com/screener/copy-super-bearish-f-0-rsp-114",
       "https://chartink.com/screener/copy-w6-f-o-2",
       "https://chartink.com/screener/copy-1week-sell-twist"]
       
sheet_id = "1h57GGy1883PE9MgqGg3oD7tyQqU3NxuTJwSwDnYOcZk"
worksheet_name = ["p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15"]

def scrape_chartink(URL, worksheet_name):
    print(f"🚀 Starting Chartink scrape for {worksheet_name}...")
    print(f"🌐 Loading: {URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(URL)

        print("📊 Waiting for table to load...")
        page.wait_for_selector("table.table-striped.scan_results_table tbody tr", timeout=15000)
        time.sleep(3)  # allow time for AJAX rows to load

        page.screenshot(path=f"{worksheet_name}_debug.png", full_page=True)

        table_rows = page.query_selector_all("table.table-striped.scan_results_table tbody tr")
        print(f"📥 Extracted {len(table_rows)} rows. Updating Google Sheet...")

        headers = ["Sr", "Stock Name", "Symbol", "Links", "Change", "Price", "Volume"]
        rows = []
        for row in table_rows:
            cells = row.query_selector_all("td")
            row_data = [cell.inner_text().strip() for cell in cells]
            rows.append(row_data)

        # Update Sheet
        google_sheets.update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows)

        # Add Timestamp
        now = datetime.now().strftime("Last updated on: %Y-%m-%d %H:%M:%S")
        google_sheets.append_footer(sheet_id, worksheet_name, [now])

        browser.close()
        print(f"✅ Google Sheet '{worksheet_name}' updated.")


for i in URL:
    scrape_chartink(i,worksheet_name[URL.index(i)])
    print(worksheet_name[URL.index(i)]," updated")
