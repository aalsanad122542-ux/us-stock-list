# Free Stock APIs Reference

This document outlines the best free and freemium stock APIs available, detailing their rate limits, data access, and best use cases.

## 1. Yahoo Finance (`yfinance`)
- **Type**: Unofficial Python Library (Scraper/API wrapper)
- **Authentication**: None required.
- **Rate Limits**: Extremely generous, though subject to undocumented IP-based rate limits if scraping aggressively.
- **Data Access**: Real-time quotes, historical data (minute/daily levels), fundamental data, options chain, and sector/industry information.
- **Pros**: Completely free, easiest to start with in Python, broad coverage (global markets).
- **Cons**: Unofficial, can break if Yahoo changes their front-end structure. Not suitable for production-level trading systems.
- **Best For**: Personal analysis, hobby projects, quickly grabbing sector or historical data.

## 2. Alpaca Trading API
- **Type**: Official Brokerage API
- **Authentication**: API Key & Secret required.
- **Rate Limits (Free Tier)**: 200 API calls per minute.
- **Data Access**: Real-time equities data from the IEX (Investors Exchange) only. Other exchanges are delayed by 15 minutes. Historical data limited to the latest 15 minutes on the free tier.
- **Pros**: Built for algorithmic trading, allows paper trading (simulated) for free.
- **Cons**: Free tier real-time data is limited to IEX, which can result in larger spreads and less accurate volume representation compared to consolidated SIP feeds.
- **Best For**: Algorithmic trading backtesting and automated paper trading.

## 3. Finnhub
- **Type**: Financial Data API
- **Authentication**: API Key required.
- **Rate Limits (Free Tier)**: 60 general calls per minute. 300 calls/min for fundamental data. 900 calls/min for market data. Global limit of 30 calls/second.
- **Data Access**: Excellent historical data (up to 10 years of daily/1-min US stocks), company fundamentals (30+ years), real-time trades via websocket.
- **Pros**: Very generous request limits per minute compared to competitors. Strong institutional-grade fundamental data.
- **Cons**: Websocket on the free tier only tracks US stocks (no forex/crypto). 
- **Best For**: Building dashboards and apps that require comprehensive fundamental data and robust historical data.

## 4. Polygon.io
- **Type**: Financial Data API
- **Authentication**: API Key required.
- **Rate Limits (Free Tier)**: strictly 5 API calls per minute.
- **Data Access**: End-of-Day (EOD) data, 2 years of historical daily bars. No real-time data available.
- **Pros**: Extremely high-quality, clean institutional data.
- **Cons**: The 5 calls/min limit makes it unusable for any sort of real-time application or rapid bulk data fetching.
- **Best For**: Slowly updating a local database with EOD prices.

## 5. Alpha Vantage
- **Type**: Financial Data API
- **Authentication**: API Key required.
- **Rate Limits (Free Tier)**: 25 requests per day.
- **Data Access**: Core stock data, physical/crypto currencies, technical indicators.
- **Pros**: Covers technical indicators (SMA, EMA, etc.) natively out of the box.
- **Cons**: 25 requests per day is extremely restrictive and effectively limits it to very slow batch jobs.
- **Best For**: Fetching highly specific technical indicators a few times a day.

## Summary Recommendation
- To update an Excel sheet with **sectors** or company information: Use **`yfinance`**, **Finnhub**, or **FMP**.
- To build a simulated **algorithmic trading** bot: Use **Alpaca**.
- To build a financial **dashboard** with 10 years of history: Use **Finnhub** or **Twelve Data**.

## 6. Financial Modeling Prep (FMP)
- **Type**: Financial Data API
- **Authentication**: API Key required.
- **Rate Limits (Free Tier)**: 250 requests per day.
- **Data Access**: End-of-day data, basic company profile, 5 years annual income statements.
- **Pros**: Very accurate fundamental data. 
- **Cons**: 250/day limit is somewhat restrictive but better than Alpha Vantage.
- **Best For**: Accurate fallback data for company profiles and sectors.

## 7. Twelve Data
- **Type**: Financial Data API
- **Authentication**: API Key required.
- **Rate Limits (Free Tier)**: 800 API credits per day.
- **Data Access**: Global market coverage, real-time prices, basic fundamentals.
- **Pros**: Good global coverage including forex and crypto.
- **Cons**: Strict daily credit limits.
- **Best For**: End of day prices and basic global stock metrics.

## Open Source Wrappers & Region-Specific APIs (GitHub)
Based on recent GitHub searches for `stock market api`, here are some notable open-source repositories and wrappers that can be highly useful:

### 1. financial-datasets/mcp-server
- **Description**: An open-source Model Context Protocol (MCP) server for financial datasets.
- **Use Case**: Excellent for integrating financial data directly into AI agents (like Claude or Gemini) that support MCP.

### 2. maanavshah/stock-market-india
- **Description**: A Node.js API to get the latest stock market data from India (National Stock Exchange - NSE).
- **Use Case**: Best for Indian stock market tracking.

### 3. jessecooper/pyetrade
- **Description**: A Python API client for the E*TRADE API.
- **Use Case**: If you have an E*TRADE account, this is an excellent open-source wrapper for executing trades and fetching account data.

### 4. godsarmy/chinese-stock-api
- **Description**: A Python API to fetch Chinese stock market data.
- **Use Case**: Specialized for tracking the Chinese markets.

### 5. thepylot/real-time-forex-api
- **Description**: A simple Python/Flask API for real-time forex conversions.
- **Use Case**: Useful if you specifically need Forex (foreign exchange) data rather than equities.
