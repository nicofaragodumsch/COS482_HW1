""" import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
# options.add_argument('--headless')  # uncomment for silent run

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
base_url = "https://scholar.google.com/scholar?as_ylo=2023&q=machine+learning&hl=en&as_sdt=0,20"
driver.get(base_url)
time.sleep(3)

titles, publication_infos, citations = [], [], []

# ---------- Loop through all result pages ----------
while True:
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Each result block
    results = soup.select(".gs_r.gs_or.gs_scl")
    for r in results:
        # Title
        title_tag = r.select_one(".gs_rt")
        title = title_tag.get_text(" ", strip=True) if title_tag else ""

        # Publication info
        pub_tag = r.select_one(".gs_a")
        publication_info = pub_tag.get_text(" ", strip=True) if pub_tag else ""

        # Cited by
        cite_tag = r.select_one(".gs_fl a:contains('Cited by')")
        if not cite_tag:
            # fallback: look for any link containing "Cited by"
            cite_tag = next((a for a in r.select(".gs_fl a") if "Cited by" in a.text), None)
        cited_by = cite_tag.get_text(strip=True) if cite_tag else "Cited by 0"

        titles.append(title)
        publication_infos.append(publication_info)
        citations.append(cited_by)

    # ---------- Try to go to next page ----------
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")
        next_button.send_keys(Keys.ENTER)
        time.sleep(3)
    except Exception:
        # No more pages
        break

driver.quit()

# ---------- Construct and save DataFrame ----------
df = pd.DataFrame({
    "title": titles,
    "publication_info": publication_infos,
    "cited_by": citations
})

df.to_csv("ml_articles_info.csv", index=False)
print(f" Scraped {len(df)} articles and saved to ml_articles_info.csv") """
"""
Task 1 – Web Scraping Google Scholar (Machine Learning 2023+)
COS 482 & COS 582 – Homework 1
"""

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Set up Selenium driver ----------
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
# options.add_argument("--headless")  # uncomment for silent run

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ---------- Navigate to Google Scholar ----------
base_url = (
    "https://scholar.google.com/scholar"
    "?as_ylo=2023&q=machine+learning&hl=en&as_sdt=0,20"
)
driver.get(base_url)
time.sleep(3)

titles, publication_infos, citations = [], [], []

# ---------- Loop through all result pages ----------
while True:
    soup = BeautifulSoup(driver.page_source, "lxml")
    results = soup.select(".gs_r.gs_or.gs_scl")

    for r in results:
        # ---------- Title extraction (fixed duplication issue) ----------
        title_tag = r.select_one(".gs_rt")
        if title_tag:
            a_tag = title_tag.find("a")
            if a_tag:
                # Prefer <a> tag text (avoid duplicate [HTML] / [PDF])
                title = a_tag.get_text(" ", strip=True)
            else:
                # Fallback: sometimes there’s no <a> (e.g., books)
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

    # ---------- Move to next page, or stop ----------
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")
        next_button.send_keys(Keys.ENTER)
        time.sleep(3)
    except Exception:
        break  # no more pages

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
