from bs4 import BeautifulSoup
from urllib.request import urlopen

chromedriver_scrape = [] # Raw scrape list
chromedriver_versions = []  # final versions list
url = "https://chromedriver.chromium.org/downloads"
html = urlopen(url)
bs = BeautifulSoup(html, "html.parser")
versions = bs.findAll("strong")


# Add each scraped element to a list
for version in versions:
  version = version.get_text()
  chromedriver_scrape.append(version)

# Skip non-relevant entries and clean string to only version numbers
for entry in chromedriver_scrape:
    if "ChromeDriver" in entry:
        entry = entry.replace("ChromeDriver ", "")
        chromedriver_versions.append(entry)


# Print versions to console if script is run directly
if __name__ == "__main__":
    print(chromedriver_versions)