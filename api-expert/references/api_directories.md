# API Directories & Discovery Sources

This document acts as a curated index for finding free, open, and accessible APIs across multiple domains.

## Core Aggregators & Directories

### 1. Public APIs (GitHub)
- **URL**: `https://github.com/public-apis/public-apis`
- **Use Case**: This is the single largest community-maintained list of free APIs.
- **How to Use**: Search the repository using standard GitHub search or by browsing the README, which categorizes APIs by topic (e.g., Animals, Finance, Machine Learning, Weather).

### 2. RapidAPI
- **URL**: `https://rapidapi.com/hub`
- **Use Case**: A massive API marketplace. Many APIs operate on a freemium model.
- **How to Use**:
  - Filter by "Freemium" or "Free".
  - **Caution**: Instruct the user to verify rate limits (e.g., "500 requests/month free") before integrating, to avoid unexpected cutoff.

### 3. APIList.fun
- **URL**: `https://apilist.fun/`
- **Use Case**: A smaller, continually updated list of fun and useful public APIs. Good for side projects or general data discovery.

### 4. ProgrammableWeb (Archival)
- **Use Case**: While ProgrammableWeb shut down, many of its historical API lists have been archived or moved to Postman's public API network. Search the Postman API Network (`https://www.postman.com/explore/apis`) for endpoints.

## Domain-Specific Resources

### Finance & Stocks
- **Alpha Vantage**: robust free tier (requires API key).
- **Yahoo Finance API**: Historically free/open, often requires rapid changes in endpoints; use community libraries (`yfinance` for Python).
- **Polygon.io**: Good free tier for end-of-day data.

### Machine Learning & AI
- **Hugging Face Hub API**: Extensive free access to open-source models (requires free token).
- **Groq / OpenRouter**: Often provide generous free tiers or extremely low-cost APIs for LLMs.

### Weather & Geolocation
- **Open-Meteo**: Completely free and open-source weather API, no API key required for non-commercial use.
- **OpenWeatherMap**: Generous free tier for current and forecasted weather.
- **Nominatim (OpenStreetMap)**: Free geocoding, but **strict rate limits** (1 request per second).

## Evaluation Checklist
Before proposing an API, always instruct the user to consider:
1. **Authentication**: Does it require an API key? OAuth? 
2. **Rate Limits**: Are the limits daily, monthly, or per-second? (e.g., Alpha Vantage is 25/day for free tier).
3. **Latency**: Is the API robust enough for the use case?
4. **Data Freshness**: Does the free tier provide real-time or delayed data?
