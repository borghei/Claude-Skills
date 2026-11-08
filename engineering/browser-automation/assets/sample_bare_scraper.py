"""Deliberately careless scraper: input for anti_detection_checker.py (expect exit 1).

No pauses between requests, no error handling, no crawl-permission check, a fixed bot
User-Agent and a headless browser.
Not meant to be run.
"""
import requests
from selenium import webdriver

options = webdriver.ChromeOptions()
headless = True
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}

for page in range(1, 500):
    html = requests.get(f"https://example.com/catalog?page={page}", headers=HEADERS).text
    print(len(html))
