import time, random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
import re

""" # ---------- Set up Selenium driver ----------
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
        # ---------- Title extraction (preserves [HTML], [PDF], etc. without duplication) ----------
        title_tag = r.select_one(".gs_rt")
        if title_tag:
            # Remove debug line now that we've identified the issue
            # print(f"Debug: {title_tag}")
            
            # Get the FIRST content type span only (gs_ct1, not gs_ct2)
            content_type_span = title_tag.find("span", class_="gs_ct1")
            content_type = content_type_span.get_text(strip=True) if content_type_span else ""
            
            # Get the link text (the actual title)
            a_tag = title_tag.find("a")
            if a_tag:
                title_text = a_tag.get_text(strip=True)
            else:
                # If no link, get all text but need to remove content type wrapper
                title_text = title_tag.get_text(strip=True)
                # Remove the content type from the text if it's there
                if content_type and title_text.startswith(content_type):
                    title_text = title_text[len(content_type):].strip()
            
            # Combine them properly
            title = f"{content_type} {title_text}" if content_type else title_text
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
print(f"Scraped {len(df)} articles and saved to ml_articles_info.csv")
 """
# ---------- Task 2(a): Data Cleaning and Transformation ----------
print("\n" + "="*60)
print("Task 2(a): Cleaning and transforming the data...")
print("="*60)

# Load the scraped data
df = pd.read_csv("ml_articles_info.csv")

# Function to parse publication_info into components
def parse_publication_info(pub_info):
    """
    Parse publication_info string into authors, year, venue, and publisher.
    Expected format: "Authors - Venue, Year - Publisher"
    """
    if pd.isna(pub_info) or pub_info == "":
        return pd.Series(['', '', '', ''])
    
    # Split by ' - ' to separate main components
    parts = pub_info.split(' - ')
    
    authors = ''
    year = ''
    venue = ''
    publisher = ''
    
    if len(parts) >= 1:
        authors = parts[0].strip()
    
    if len(parts) >= 2:
        # Second part typically contains venue and year
        middle_part = parts[1].strip()
        # Extract year (4 digits)
        year_match = re.search(r'\b(202[3-5])\b', middle_part)
        if year_match:
            year = year_match.group(1)
            # Remove year and comma from venue
            venue = re.sub(r',?\s*' + year + r'\s*', '', middle_part).strip()
            venue = venue.rstrip(',').strip()
        else:
            venue = middle_part
    
    if len(parts) >= 3:
        publisher = parts[2].strip()
    
    return pd.Series([authors, year, venue, publisher])

# Apply the parsing function
df[['authors', 'year', 'venue', 'publisher']] = df['publication_info'].apply(parse_publication_info)

# Clean citation_count: remove "Cited by " and convert to integer
df['citation_count'] = df['cited_by'].str.replace('Cited by ', '', regex=False).astype(int)

# Convert year to integer (handle empty strings)
df['year'] = pd.to_numeric(df['year'], errors='coerce')

# Calculate avg_citations_per_year
def calculate_avg_citations(row):
    """Calculate average citations per year based on publication year"""
    if pd.isna(row['year']):
        return 0
    
    year = int(row['year'])
    citation_count = row['citation_count']
    
    if year == 2023:
        divisor = 3
    elif year == 2024:
        divisor = 2
    elif year == 2025:
        divisor = 1
    else:
        divisor = 1  # Default for unexpected years
    
    return round(citation_count / divisor, 4)

df['avg_citations_per_year'] = df.apply(calculate_avg_citations, axis=1)

# Reorder columns as specified
df_cleaned = df[['title', 'authors', 'year', 'venue', 'publisher', 'citation_count', 'avg_citations_per_year']]

# Save cleaned dataframe
df_cleaned.to_csv("ml_articles_info-cleaned.csv", index=False, encoding="utf-8")
print(f"Cleaned data saved to ml_articles_info-cleaned.csv")
print(f"Shape: {df_cleaned.shape}")
print("\nFirst few rows:")
print(df_cleaned.head())

# ---------- Task 2(b): Filter articles from 2024+ with >100 citations ----------
print("\n" + "="*60)
print("Task 2(b): Articles from 2024+ with >100 citations")
print("="*60)

filtered_articles = df_cleaned[(df_cleaned['year'] >= 2024) & (df_cleaned['citation_count'] > 100)]
print(f"\nFound {len(filtered_articles)} articles:\n")
for idx, row in filtered_articles.iterrows():
    print(f"Title: {row['title']}")
    print(f"Authors: {row['authors']}")
    print(f"Year: {int(row['year'])}")
    print(f"Citations: {row['citation_count']}")
    print("-" * 60)

# ---------- Task 2(c): Scatterplot of citation_count vs avg_citations_per_year ----------
print("\n" + "="*60)
print("Task 2(c): Creating scatterplot...")
print("="*60)

plt.figure(figsize=(10, 6))
plt.scatter(df_cleaned['avg_citations_per_year'], df_cleaned['citation_count'], alpha=0.6)
plt.xlabel('Average Citations per Year')
plt.ylabel('Total Citation Count')
plt.title('Total Citation Count vs. Average Citations per Year')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('scatterplot_citations.png', dpi=300)
print("Scatterplot saved as scatterplot_citations.png")
#plt.show()

# ---------- Task 2(d): Histogram of avg_citations_per_year ----------
print("\n" + "="*60)
print("Task 2(d): Creating histogram...")
print("="*60)

plt.figure(figsize=(10, 6))
plt.hist(df_cleaned['avg_citations_per_year'], bins=30, edgecolor='black', alpha=0.7)
plt.xlabel('Average Citations per Year')
plt.ylabel('Frequency')
plt.title('Distribution of Average Citations per Year')
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('histogram_avg_citations.png', dpi=300)
print("Histogram saved as histogram_avg_citations.png")
#plt.show()

# ---------- Task 2(e): Articles per year ----------
print("\n" + "="*60)
print("Task 2(e): Number of articles per year")
print("="*60)

articles_per_year = df_cleaned['year'].value_counts().sort_index()
print("\nArticles published per year:")
print(articles_per_year)

plt.figure(figsize=(10, 6))
articles_per_year.plot(kind='bar', color='steelblue', edgecolor='black')
plt.xlabel('Publication Year')
plt.ylabel('Number of Articles')
plt.title('Number of Articles Published per Year (Since 2023)')
plt.xticks(rotation=0)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('barplot_articles_per_year.png', dpi=300)
print("Bar plot saved as barplot_articles_per_year.png")
#plt.show()

# ---------- Task 2(f): Mean citation count per year ----------
print("\n" + "="*60)
print("Task 2(f): Mean citation count per publication year")
print("="*60)

mean_citations_per_year = df_cleaned.groupby('year')['citation_count'].mean().sort_index()
print("\nMean citation count per publication year:")
print(mean_citations_per_year)

plt.figure(figsize=(10, 6))
mean_citations_per_year.plot(kind='bar', color='coral', edgecolor='black')
plt.xlabel('Publication Year')
plt.ylabel('Mean Citation Count')
plt.title('Mean Citation Count by Publication Year')
plt.xticks(rotation=0)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('barplot_mean_citations_per_year.png', dpi=300)
print("Bar plot saved as barplot_mean_citations_per_year.png")
#plt.show()

print("\n" + "="*60)
print("All Task 2 analyses completed!")
print("="*60)