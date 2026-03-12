---
name: api-expert
description: Expert skill for finding free APIs, navigating API alternatives (like web scraping), and integrating external data sources. Use this skill when the user asks to find an API for a specific use case, needs a free/open-source alternative, or when an API is unavailable/expensive and web scraping is required.
---

# API Expert

This skill provides strategies and resources for discovering APIs, evaluating free alternatives, and implementing web scraping when APIs are not viable.

## Core Capabilities

1. **API Discovery**: Finding free, freemium, or open-source APIs for specific use cases (e.g., finance, weather, machine learning).
2. **Evaluation**: Assessing API limitations (rate limits, pricing tiers, authentication requirements).
3. **Web Scraping (Fallbacks)**: Using web scraping techniques (BeautifulSoup, Playwright, Selenium) when APIs are unavailable or prohibitively expensive.

## API Discovery Workflow

When a user requests an API for a specific task:

1. **Check standard directories:** See [api_directories.md](references/api_directories.md) for a curated list of free API aggregators.
2. **Search GitHub:** Look for open-source wrappers or community-maintained lists (e.g., "public APIs github").
3. **Evaluate constraints:** Always verify rate limits and pricing before recommending an API. If an API requires an upfront credit card for a "free tier," warn the user.

## Web Scraping as an Alternative

If no suitable free API exists, propose web scraping as an alternative.

**When to suggest scraping:**
- The official API is paid and outside the user's budget.
- The official API is deprecated or broken.
- The data is publicly visible on a website but not exposed via a public endpoint.

**Crucial Constraints & Ethics:**
- Ensure the scraping approach respects `robots.txt` where possible.
- Warn the user about potential rate limits, CAPTCHAs, or IP bans.
- Use staggered requests and rotating user agents to ensure stability.

See [web_scraping_strategies.md](references/web_scraping_strategies.md) for specific guides on scraping static vs. dynamic content.

## Implementation Guidelines

When implementing an API integration or a scraper for the user:
- **Always implement robust error handling:** Catch HTTP errors, timeout exceptions, and JSON parsing errors.
- **Implement rate limiting:** Provide sleep/delay mechanisms between requests to avoid bans.
- **Environment variables:** Never hardcode API keys. Use `.env` or equivalent configuration files.
