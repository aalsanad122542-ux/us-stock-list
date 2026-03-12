"""
gemini_service.py
Google Gemini AI service wrapper.
Uses gemini-1.5-flash (free tier: 1M tokens/month).
Drop-in replacement for groq_service.py.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini AI service for stock analysis"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.available = bool(self.api_key)
        self.model_name = "gemini-2.5-flash"

        if self.available:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini service initialized with {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.available = False
        else:
            logger.warning("GEMINI_API_KEY not set. AI features will be disabled.")

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_mime_type: str = "text/plain"
    ) -> Dict[str, Any]:
        """Generate a completion using Gemini."""
        if not self.available:
            return {"success": False, "text": "", "model": "gemini", "error": "GEMINI_API_KEY not configured"}

        import time

        def attempt_generation(model_name: str, max_retries: int = 3):
            # Internal helper to handle generation with retries
            client = genai.GenerativeModel(model_name)
            
            for attempt in range(max_retries):
                try:
                    response = client.generate_content(
                        full_prompt,
                        generation_config=GenerationConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                            response_mime_type=response_mime_type
                        )
                    )
                    
                    if hasattr(response, 'candidates') and response.candidates:
                        finish_reason = response.candidates[0].finish_reason
                        logger.info(f"Gemini finish_reason: {finish_reason}")
                        
                    text = response.text.strip() if response.text else ""
                    if text:
                        return {"success": True, "text": text, "model": model_name, "error": None}
                    else:
                        return {"success": False, "text": "", "model": model_name, "error": "Empty response"}
                        
                except Exception as e:
                    error_msg = str(e)
                    # Handle Rate Limits (429)
                    if "429" in error_msg or "Quota exceeded" in error_msg:
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s
                            logger.warning(f"Gemini {model_name} rate limit hit. Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                    
                    # Log error and return failure if out of retries or non-429 error
                    logger.error(f"Gemini generation failed for model {model_name}: {error_msg}")
                    return {"success": False, "text": "", "model": model_name, "error": error_msg}
            
            return {"success": False, "text": "", "model": model_name, "error": "Max retries exceeded"}

        try:
            import google.generativeai as genai
            from google.generativeai.types import GenerationConfig
            
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            
            # Primary attempt with gemini-2.0-flash
            result = attempt_generation(self.model_name)
            
            # Fallback to gemini-2.5-pro if 2.0 fails due to quota
            if not result["success"] and ("429" in str(result["error"]) or "Quota" in str(result["error"])):
                fallback_model = "gemini-2.5-pro"
                logger.warning(f"Falling back to {fallback_model} due to quota limits on {self.model_name}")
                result = attempt_generation(fallback_model, max_retries=2)
                
            return result
        except Exception as e:
            logger.error(f"Gemini total failure: {e}")
            return {"success": False, "text": "", "model": "gemini", "error": str(e)}

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment thesis for a stock."""
        ticker = stock_data.get("ticker", "?")
        company = stock_data.get("company_name", ticker)

        system_prompt = """You are an expert investment consultant and portfolio manager specializing in US equity markets (NYSE/NASDAQ).
Your primary mission is to identify high-potential growth stocks (GEM stocks) and provide comprehensive, data-driven analysis.

When providing investment recommendations, use this EXACT structure:

Summary: 2-3 sentence overview of the opportunity and investment thesis.

Company Snapshot: Business model, sector, and recent overall performance context.

Catalyst Deep-Dive: Specific events/announcements driving growth outlook with timing and probability.

Management Team Analysis: 
(Provide a brief assessment of the management quality. If specific executive names/tenures aren't in the provided data, provide a general assessment of what strong management would look like for this specific company's current stage/industry).

Fair Value Analysis: 
(Calculate a rough fair value or target price based on the provided P/E, Forward P/E, revenue growth, and Analyst Target. State your assumptions clearly).

Financial Projections: Revenue/EPS growth interpretation based on the provided metrics.

Risk Assessment: 3-4 bullet points detailing execution risk, competitive threats, macro headwinds, etc.

Recommendation: Buy/Hold/Reduce/Avoid with brief sizing guidance.

Be objective, data-driven, and conservative in your estimates."""

        prompt = f"""Analyze {ticker} ({company}) using these fundamentals:
- Sector: {stock_data.get('sector', 'N/A')} | Industry: {stock_data.get('industry', 'N/A')}
- P/E: {stock_data.get('pe_ratio', 'N/A')} | Forward P/E: {stock_data.get('forward_pe', 'N/A')} | P/B: {stock_data.get('pb_ratio', 'N/A')}
- Revenue Growth: {stock_data.get('revenue_growth', 'N/A')}% | Net Margin: {stock_data.get('net_margin', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}% | Debt/Equity: {stock_data.get('debt_equity', 'N/A')}
- Free Cash Flow: ${stock_data.get('free_cash_flow_b', 'N/A')}B | Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}%
- Analyst: {stock_data.get('analyst_rating', 'N/A')} | Target: ${stock_data.get('target_price', 'N/A')}
- Beta: {stock_data.get('beta', 'N/A')} | 52W High: ${stock_data.get('week_52_high', 'N/A')}
- Video context: {stock_data.get('video_context', 'Not provided')}"""

        result = self.generate(prompt, system=system_prompt, temperature=0.3, max_tokens=1000)

        if result["success"]:
            text = result["text"]
            thesis = risks = summary = ""
            
            # Map the detailed IBKR sections into our expected UI fields
            # We'll put the full detailed report into the 'thesis' field for now
            # and extract the specific Recommendation/Summary fields
            
            for line in text.split("\n"):
                line_upper = line.strip().upper()
                if line_upper.startswith("SUMMARY:"):
                    summary = line.split(":", 1)[1].strip()
                elif line_upper.startswith("RECOMMENDATION:"):
                    # Extract buy/sell/hold from recommendation
                    rec = line.split(":", 1)[1].strip()
                    summary = f"{rec} - {summary}" if summary else rec
                elif line_upper.startswith("RISK ASSESSMENT:"):
                    risks = "See full detailed risk assessment in thesis."
                    
            return {
                "thesis": text, # Pass the entire detailed report to the UI
                "risks": risks or "See detailed report",
                "summary": summary or "Detailed analysis provided",
                "model_used": result.get("model")
            }

        return {
            "thesis": f"AI analysis unavailable: {result.get('error')}",
            "risks": "N/A",
            "summary": "",
            "model_used": None
        }

    def analyze_stocks_batch(self, stocks_list: list[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate investment thesis for multiple stocks in a single LLM request to save tokens."""
        if not stocks_list:
            return {}
            
        system_prompt = """You are an expert investment consultant and portfolio manager specializing in US equity markets (NYSE/NASDAQ).
Your primary mission is to identify high-potential growth stocks (GEM stocks).

You will be provided with fundamental data and context for multiple stocks.
You MUST analyze all of them and return ONLY a valid JSON object where keys are the stock TICKERS, and values are objects containing the exact analysis fields.

JSON Format required:
{
  "AAPL": {
    "summary": "1-line general verdict: BUY, SELL, or HOLD, and brief reason.",
    "risks": "2 short bullet points on primary risks.",
    "thesis": "Concise 3-4 sentence analysis covering market position, catalysts, and valuation."
  },
  "MSFT": {
    ...
  }
}

Be objective, data-driven, and brief. NEVER write outside the JSON block."""

        prompt_parts = []
        for stock_data in stocks_list:
            ticker = stock_data.get("ticker", "?")
            company = stock_data.get("company_name", ticker)
            
            prompt_parts.append(f"""
TICKER: {ticker} ({company})
- Sector: {stock_data.get('sector', 'N/A')} | Industry: {stock_data.get('industry', 'N/A')}
- P/E: {stock_data.get('pe_ratio', 'N/A')} | Forward P/E: {stock_data.get('forward_pe', 'N/A')} | P/B: {stock_data.get('pb_ratio', 'N/A')}
- Revenue Growth: {stock_data.get('revenue_growth', 'N/A')}% | Net Margin: {stock_data.get('net_margin', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}% | Debt/Equity: {stock_data.get('debt_equity', 'N/A')}
- Free Cash Flow: ${stock_data.get('free_cash_flow_b', 'N/A')}B | Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}%
- Analyst: {stock_data.get('analyst_rating', 'N/A')} | Target: ${stock_data.get('target_price', 'N/A')}
- Beta: {stock_data.get('beta', 'N/A')} | 52W High: ${stock_data.get('week_52_high', 'N/A')}
- Video context (transcripts mentioning this stock): {stock_data.get('video_context', 'Not provided')}
""")
            
        full_prompt = "Analyze the following stocks and strictly return the JSON object:\n" + "".join(prompt_parts)
        
        max_tokens_alloc = min(8000, max(2000, len(stocks_list) * 600))
        
        result = self.generate(
            full_prompt, 
            system=system_prompt, 
            temperature=0.2, 
            max_tokens=max_tokens_alloc,
            response_mime_type="application/json"
        )
        
        results_map = {}
        if result["success"]:
            text = result["text"].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            import json
            try:
                parsed_json = json.loads(text)
                for ticker, analysis in parsed_json.items():
                    # Ensure strictly string formats in case the LLM returned lists
                    risks_raw = analysis.get("risks", "Risk assessment missing")
                    if isinstance(risks_raw, list):
                        risks_raw = "\n".join([str(r) for r in risks_raw])
                        
                    results_map[ticker] = {
                        "thesis": str(analysis.get("thesis", "Detailed analysis missing")),
                        "risks": str(risks_raw),
                        "summary": str(analysis.get("summary", "Summary missing")),
                        "model_used": result.get("model")
                    }
            except json.JSONDecodeError as e:
                import logging
                logging.error(f"Failed to parse batched JSON from Gemini: {e}\nRaw output length: {len(text)}\nRaw output: {text}")
                for stock in stocks_list:
                    ticker = stock.get("ticker", "?")
                    results_map[ticker] = {
                        "thesis": "Error parsing batched AI response. Raw output was malformed.",
                        "risks": "N/A",
                        "summary": "Error",
                        "model_used": result.get("model")
                    }
        else:
            for stock in stocks_list:
                ticker = stock.get("ticker", "?")
                results_map[ticker] = {
                    "thesis": f"AI analysis unavailable: {result.get('error')}",
                    "risks": "N/A",
                    "summary": "Error",
                    "model_used": None
                }
                
        return results_map

    def summarize_transcript(self, transcript: str, video_title: str = "") -> str:
        """Summarize a YouTube video transcript."""
        truncated = transcript[:25000]
        system_prompt = """You are a helpful AI that summarizes YouTube financial content.
Provide a concise summary that captures:
1. Main topic and thesis
2. Key stocks/assets mentioned
3. Notable insights or predictions"""

        prompt = f"""Video Title: {video_title}

Transcript:
{truncated}

Provide a summary with:
1. Brief overview (2-3 sentences)
2. Key points (bullet list)
3. Stocks mentioned (if any)"""

        result = self.generate(prompt, system=system_prompt, temperature=0.5, max_tokens=1000)
        return result["text"] if result["success"] else f"Summary unavailable: {result.get('error')}"

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Chat about portfolio and analysis."""
        system_prompt = """You are a helpful financial AI assistant.
Help users understand their portfolio, market analysis, and investment concepts.
Always clarify when information is uncertain. Provide clear, actionable insights."""
        prompt = message
        if context:
            if context.get("portfolio"):
                prompt = f"Portfolio context: {context['portfolio']}\n\nUser question: {message}"
            if context.get("analysis"):
                prompt = f"Latest analysis: {context['analysis']}\n\nUser question: {message}"
        result = self.generate(prompt, system=system_prompt, temperature=0.5, max_tokens=1500)
        return result["text"] if result["success"] else f"AI unavailable: {result.get('error')}"

    def analyze_stock_ibkr(self, stock_data: Dict[str, Any], instruction_prompt: str) -> str:
        """
        Takes the fundamental data and runs it through the detailed IBKR Instructions.md prompt.
        Returns the raw markdown output generated by the LLM.
        """
        ticker = stock_data.get("ticker", "?")
        company = stock_data.get("company_name", ticker)
        
        system_prompt = instruction_prompt
        
        prompt = f"""Please perform your comprehensive analysis for {ticker} ({company}) using the following fundamental data:
- Sector: {stock_data.get('sector', 'N/A')} | Industry: {stock_data.get('industry', 'N/A')}
- Price: ${stock_data.get('price', 'N/A')} | Market Cap: ${stock_data.get('market_cap_b', 'N/A')}B
- P/E: {stock_data.get('pe_ratio', 'N/A')} | Forward P/E: {stock_data.get('forward_pe', 'N/A')} | P/B: {stock_data.get('pb_ratio', 'N/A')}
- Revenue Growth: {stock_data.get('revenue_growth', 'N/A')}% | Net Margin: {stock_data.get('net_margin', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}% | Debt/Equity: {stock_data.get('debt_equity', 'N/A')}
- Free Cash Flow: ${stock_data.get('free_cash_flow_b', 'N/A')}B | Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}%
- Analyst Rating: {stock_data.get('analyst_rating', 'N/A')} | Target: ${stock_data.get('target_price', 'N/A')}
- Beta: {stock_data.get('beta', 'N/A')} | 52W High: ${stock_data.get('week_52_high', 'N/A')} | 52W Low: ${stock_data.get('week_52_low', 'N/A')}
- Description: {stock_data.get('description', 'N/A')}

Remember to include the Mandatory Management Analysis Table and Mandatory Fair Value Analysis as dictated in your operational instructions. Make reasonable estimates if specific management profiles or advanced inputs aren't available in this prompt.

CRITICAL INSTRUCTION: You MUST start your response exactly with the following two lines. Do not add any conversational opening text.
Fundamental Rating: [Your Rating out of 10]
Shariaa Compliant: [Yes/No/Uncertain]

After those two lines, proceed with your full analysis.
"""
        result = self.generate(prompt, system=system_prompt, temperature=0.1, max_tokens=4000)
        
        if result["success"]:
            return result["text"]
        else:
             return f"<h3>Failed to generate IBKR analysis for {ticker}. Error: {result.get('error')}</h3>"


# Singleton
_gemini_service = None

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

def generate(prompt: str, **kwargs) -> Dict[str, Any]:
    return get_gemini_service().generate(prompt, **kwargs)

def analyze_stock(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    return get_gemini_service().analyze_stock(stock_data)

def analyze_stocks_batch(stocks_list: list[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return get_gemini_service().analyze_stocks_batch(stocks_list)

def summarize_transcript(transcript: str, video_title: str = "") -> str:
    return get_gemini_service().summarize_transcript(transcript, video_title)

def chat(message: str, context: Optional[Dict[str, Any]] = None) -> str:
    return get_gemini_service().chat(message, context)

def analyze_stock_ibkr(stock_data: Dict[str, Any], instruction_prompt: str) -> str:
    return get_gemini_service().analyze_stock_ibkr(stock_data, instruction_prompt)
