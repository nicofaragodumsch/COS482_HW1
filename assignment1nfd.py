

import time, random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Set up Selenium driver ----------
options = webdriver.ChromeOptions()

# Use a temporary Chrome profile (not incognito, not your main profile)
options.add_argument('--user-data-dir=C:\\Temp\\ChromeProfile')

# Optional tweaks that make traffic look less like a bot
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-blink-features=AutomationControlled")

# CRITICAL: DO NOT use headless mode - it triggers CAPTCHA
# options.add_argument('--headless')  # KEEP THIS COMMENTED OUT

# These are fine to keep
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Randomize window size
options.add_argument(f"--window-size={random.randint(1000,1600)},{random.randint(700,1000)}")

# Additional anti-detection measures
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Hide webdriver property
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# ---------- Navigate to Google Scholar ----------
base_url = (
    "https://scholar.google.com/scholar"
    "?as_ylo=2023&q=machine+learning&hl=en&as_sdt=0,20"
)
driver.get(base_url)

# Random initial pause to let page load naturally
time.sleep(random.uniform(5, 10))

titles, publication_infos, citations = [], [], []

# ---------- Loop through all result pages ----------
page_count = 0
max_pages = 10  # Set a reasonable limit to avoid running forever

while page_count < max_pages:
    print(f"Scraping page {page_count + 1}...")
    
    soup = BeautifulSoup(driver.page_source, "lxml")
    results = soup.select(".gs_r.gs_or.gs_scl")
    
    if not results:
        print(f"No results found on page {page_count + 1}. Stopping.")
        break
    
    print(f"Found {len(results)} results on this page.")

    for r in results:
        # ---------- Title extraction ----------
        title_tag = r.select_one(".gs_rt")
        if title_tag:
            a_tag = title_tag.find("a")
            if a_tag:
                title = a_tag.get_text(" ", strip=True)
            else:
                title = title_tag.get_text(" ", strip=True)
        else:
            title = ""

        # ---------- Publication info ----------
        pub_tag = r.select_one(".gs_a")
        publication_info = pub_tag.get_text(" ", strip=True) if pub_tag else ""

        # ---------- Citation count ----------
        cite_tag = next(
            (a for a in r.select(".gs_fl a") if "Cited by" in a.text),
            None
        )
        cited_by = cite_tag.get_text(strip=True) if cite_tag else "Cited by 0"

        titles.append(title)
        publication_infos.append(publication_info)
        citations.append(cited_by)

    page_count += 1

    # ---------- Move to next page, or stop ----------
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")

        # Add a long, random pause to look human
        sleep_time = random.uniform(8, 15)
        print(f"Sleeping for {sleep_time:.1f}s before next page...")
        time.sleep(sleep_time)

        next_button.click()  # Use click() instead of send_keys()
        
        # Extra wait for page load
        time.sleep(random.uniform(5, 8))
    except Exception as e:
        print(f"No more pages or error encountered: {e}")
        break

# ---------- Close driver ----------
driver.quit()

# ---------- Build and save DataFrame ----------
df = pd.DataFrame({
    "title": titles,
    "publication_info": publication_infos,
    "cited_by": citations
})

df.to_csv("ml_articles_info.csv", index=False, encoding="utf-8")
print(f"✅ Scraped {len(df)} articles and saved to ml_articles_info.csv")
