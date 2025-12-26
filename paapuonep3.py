from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import google_sheets
import time

URLS = [
    "https://chartink.com/screener/copy-bearish-engulifing-see-after-3-15-pm-for-next-day-trade-5168",
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
    "https://chartink.com/screener/copy-copy-super-bearish-f-0-rsp-17",
    "https://chartink.com/screener/copy-w6-f-o-2",
    "https://chartink.com/screener/copy-1week-sell-twist",
    "https://chartink.com/screener/copy-weekly-bollinger-sell-3"
]

sheet_id = "1h57GGy1883PE9MgqGg3oD7tyQqU3NxuTJwSwDnYOcZk"
worksheet_names = ["p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15","p16"]

def scrape_chartink(url, worksheet_name):
    print(f"\n🚀 Starting scrape for '{worksheet_name}'")
    print(f"🌐 Loading URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        headers = ["Sr", "Stock Name", "Symbol", "Links", "Change", "Price", "Volume"]

        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(3)

            if page.is_visible("text='No records found'"):
                print(f"⚠️ No records found at {url}. Writing blank space.")
                rows = [[""]]
            else:
                try:
                    page.wait_for_selector("div.relative table tbody tr", timeout=60000)
                    table_rows = page.query_selector_all("div.relative table tbody tr")

                    print(f"📥 Extracted {len(table_rows)} rows.")
                    rows = []

                    for row in table_rows:
                        cells = row.query_selector_all("td")
                        row_data = [cell.inner_text().strip() for cell in cells]
                        rows.append(row_data)

                    if len(rows) == 0:
                        print("⚠️ Table present but no data rows. Writing blank space.")
                        rows = [[""]]

                except PlaywrightTimeoutError:
                    print(f"❌ Table not found at {url}. Writing blank space.")
                    rows = [[""]]

            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, rows
            )

        except PlaywrightTimeoutError:
            print(f"❌ Timeout error at {url}. Writing blank space.")
            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, [[""]]
            )

        except Exception as e:
            print(f"❌ Unexpected error: {e}. Writing blank space.")
            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, [[""]]
            )

        finally:
            page.screenshot(path=f"{worksheet_name}_debug.png", full_page=True)
            browser.close()

        now = datetime.now().strftime("Last updated on: %Y-%m-%d %H:%M:%S")
        google_sheets.append_footer(sheet_id, worksheet_name, [now])

        print(f"✅ Worksheet '{worksheet_name}' updated.")

for index, url in enumerate(URLS):
    scrape_chartink(url, worksheet_names[index])
    print(f"⏱️ Finished updating '{worksheet_names[index]}'")
