"""
ApiFreeLLM AI service wrapper.
Free AI API with no token limits (1 req/5s without key).
https://apifreellm.com/
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ApiFreeLLMService:
    def __init__(self):
        self.api_key = os.getenv("APIFREELLM_API_KEY", "").strip()
        self.base_url = "https://apifreellm.com/api/v1/chat"
        self.model = "apifreellm"

        if self.api_key:
            logger.info("ApiFreeLLM service initialized WITH API key")
        else:
            logger.info("ApiFreeLLM service initialized (no API key - rate limited)")

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ):
        import requests

        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = {
            "message": full_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                self.base_url, headers=headers, json=data, timeout=60
            )

            if response.status_code == 200:
                result = response.json()

                if result.get("status") == "success":
                    return {
                        "success": True,
                        "text": result.get("response", ""),
                        "model": self.model,
                        "error": None,
                    }
                elif result.get("status") == "error":
                    error_msg = result.get("error", "Unknown error")
                    return {
                        "success": False,
                        "text": "",
                        "model": self.model,
                        "error": error_msg,
                    }
            else:
                return {
                    "success": False,
                    "text": "",
                    "model": self.model,
                    "error": f"HTTP {response.status_code}",
                }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "text": "",
                "model": self.model,
                "error": "Request timeout",
            }
        except Exception as e:
            return {"success": False, "text": "", "model": self.model, "error": str(e)}

        return {
            "success": False,
            "text": "",
            "model": self.model,
            "error": "Unknown error",
        }

    def analyze_stock_ibkr(
        self, stock_data: Dict[str, Any], instruction_prompt: str
    ) -> str:
        ticker = stock_data.get("ticker", "?")
        company = stock_data.get("company_name", ticker)

        system_prompt = instruction_prompt

        prompt = f"""Please perform your comprehensive analysis for {ticker} ({company}) using the following fundamental data:
- Sector: {stock_data.get("sector", "N/A")} | Industry: {stock_data.get("industry", "N/A")}
- Price: ${stock_data.get("price", "N/A")} | Market Cap: ${stock_data.get("market_cap_b", "N/A")}B
- P/E: {stock_data.get("pe_ratio", "N/A")} | Forward P/E: {stock_data.get("forward_pe", "N/A")} | P/B: {stock_data.get("pb_ratio", "N/A")}
- Revenue Growth: {stock_data.get("revenue_growth", "N/A")}% | Net Margin: {stock_data.get("net_margin", "N/A")}%
- ROE: {stock_data.get("roe", "N/A")}% | Debt/Equity: {stock_data.get("debt_equity", "N/A")}
- Free Cash Flow: ${stock_data.get("free_cash_flow_b", "N/A")}B | Dividend Yield: {stock_data.get("dividend_yield", "N/A")}%
- Analyst Rating: {stock_data.get("analyst_rating", "N/A")} | Target: ${stock_data.get("target_price", "N/A")}
- Beta: {stock_data.get("beta", "N/A")} | 52W High: ${stock_data.get("week_52_high", "N/A")} | 52W Low: ${stock_data.get("week_52_low", "N/A")}
- Description: {stock_data.get("description", "N/A")}

Include Fundamental Rating (out of 10) and Shariaa Compliance status.

CRITICAL: Start with exactly:
Fundamental Rating: [Your Rating]
Shariaa Compliant: [Yes/No/Uncertain]
"""
        result = self.generate(
            prompt, system=system_prompt, temperature=0.1, max_tokens=4000
        )

        if result["success"]:
            return result["text"]
        else:
            return f"<h3>Failed to generate analysis for {ticker}. Error: {result.get('error')}</h3>"


_apifreellm_service = None


def get_apifreellm_service():
    global _apifreellm_service
    if _apifreellm_service is None:
        _apifreellm_service = ApiFreeLLMService()
    return _apifreellm_service


def generate(prompt: str, **kwargs):
    return get_apifreellm_service().generate(prompt, **kwargs)


def analyze_stock_ibkr(stock_data: Dict[str, Any], instruction_prompt: str) -> str:
    return get_apifreellm_service().analyze_stock_ibkr(stock_data, instruction_prompt)
