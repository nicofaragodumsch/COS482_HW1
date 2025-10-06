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
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=IsolateOrigins,site-per-process")

# CRITICAL: DO NOT use headless mode - it triggers CAPTCHA
# options.add_argument('--headless')  # KEEP THIS COMMENTED OUT

# Remove these - they can trigger detection
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')

# Set a realistic window size (not randomized - too suspicious)
options.add_argument("--window-size=1920,1080")

# Additional anti-detection measures
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Add a realistic user agent
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Hide webdriver property and other automation indicators
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    '''
})

# ---------- Navigate to Google Scholar ----------
base_url = (
    "https://scholar.google.com/scholar"
    "?as_ylo=2023&q=machine+learning&hl=en&as_sdt=0,20"
)
driver.get(base_url)

# Random initial pause to let page load naturally
initial_sleep = random.uniform(10, 15)
print(f"Initial page load - sleeping for {initial_sleep:.1f}s...")
time.sleep(initial_sleep)

# Check for CAPTCHA and give user time to solve it
print("\n" + "="*60)
print("⚠️  CHECK THE BROWSER WINDOW!")
print("If you see a CAPTCHA, solve it now.")
print("After the page loads normally, press Enter here to continue...")
print("="*60 + "\n")
input()  # Wait for manual CAPTCHA solving

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
        # Scroll down before clicking (more human-like)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        
        next_button = driver.find_element(By.LINK_TEXT, "Next")

        # Add a long, random pause to look human (increased significantly)
        sleep_time = random.uniform(15, 25)
        print(f"Sleeping for {sleep_time:.1f}s before next page...")
        time.sleep(sleep_time)

        next_button.click()  # Use click() instead of send_keys()
        
        # Extra wait for page load
        time.sleep(random.uniform(8, 12))
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
