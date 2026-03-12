# Web Scraping Strategies and Fallbacks

When an official API is unavailable, deprecated, or prohibitively expensive, web scraping is a viable alternative for extracting structured data from websites.

## 1. Choosing the Right Tool

The approach depends entirely on how the target website renders its content.

### A. Static HTML Parsing
**Use when**: The data is embedded directly in the HTML returned by the server on initial load.
- **Python**: `requests` + `BeautifulSoup` or `lxml`.
- **Node.js**: `axios` + `cheerio`.
- **Pros**: Very fast, low resource overhead.
- **Cons**: Useless for Single Page Applications (SPAs) or heavily JavaScript-rendered sites.

### B. Network Traffic Interception (Hidden APIs)
**Use when**: The page loads dynamically, but fetching the data relies on XHR/Fetch requests to internal backend APIs.
- **Technique**: Open browser developer tools (F12) -> Network tab -> Filter by `Fetch/XHR`. Look for JSON responses containing the desired data.
- **Execution**: Recreate the HTTP request (including necessary headers, cookies, and tokens) in code using `requests` or `axios`.
- **Pros**: Fastest and most structured method; basically accessing an unofficial API.
- **Cons**: Endpoints may change frequently; often requires reverse-engineering authentication tokens.

### C. Headless Browsers
**Use when**: The page requires complex JavaScript execution to render the DOM, and network interception is explicitly blocked or obfuscated.
- **Tools**: `Playwright` (preferred), `Puppeteer`, or `Selenium`.
- **Pros**: Can interact with the page just like a real user (clicking buttons, waiting for elements).
- **Cons**: Extremely slow, high memory/CPU overhead, prone to breaking on UI tweaks.

## 2. Bypassing Basic Protections

If requests are blocked (e.g., 403 Forbidden), apply these defensive scraping techniques:

### Headers and User Agents
Always include realistic headers. Default library headers (e.g., `python-requests/2.28.1`) are immediately blocked by WAFs (Web Application Firewalls).
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}
```

### Rate Limiting and Delays
Never hammer a server. Use randomized sleep intervals to mimic human browsing.
```python
import time, random
time.sleep(random.uniform(1.5, 4.5))
```

## 3. Handling Advanced Protections (Cloudflare, Datadome)

If the site uses Cloudflare or similar bot protection:
1. **Cloudscraper**: A Python library designed to bypass basic Cloudflare anti-bot pages.
2. **Playwright Stealth**: Use `playwright-stealth` to mask headless browser fingerprints (e.g., overriding `navigator.webdriver`).
3. **Scraping APIs**: Recommend services like ScraperAPI, ZenRows, or BrightData, which handle proxy rotation and CAPTCHA solving automatically (though they cost money, they usually have free trials).

## 4. Ethical Considerations
- Check `robots.txt` (`https://example.com/robots.txt`) to see if the path is explicitly disallowed.
- Respect the site's terms of service where commercially applicable.
- Do not perform Denial of Service (DoS) attacks by sending concurrent requests rapidly.
- Cash/store scraped data locally (e.g., SQLite, JSON) to avoid re-scraping the same pages unnecessarily.
