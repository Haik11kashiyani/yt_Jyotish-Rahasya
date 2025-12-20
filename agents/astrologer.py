import os
import json
import logging
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AstrologerAgent:
    """
    The Astrologer Agent uses LLMs to generate authentic Vedic Astrology content.
    It acts like a knowledgeable Shastri (Astrologer).
    """
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenRouter API Key."""
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing!")
            
        # Initialize OpenAI Client pointing to OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        self.models = self.get_best_free_models()
        self.current_model_index = 0

    def get_best_free_models(self) -> list:
        """
        Fetches available models from OpenRouter, filters for free ones,
        and ranks them based on heuristics (e.g. 'gemini', 'llama', '70b').
        """
        try:
            logging.info("🔎 Discovering best free models on OpenRouter...")
            response = requests.get("https://openrouter.ai/api/v1/models")
            if response.status_code != 200:
                logging.warning("⚠️ Failed to fetch models list. Using defaults.")
                return ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free"]
            
            all_models = response.json().get("data", [])
            free_models = []
            
            for m in all_models:
                pricing = m.get("pricing", {})
                if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                    free_models.append(m["id"])
            
            # Smart Ranking Heuristics
            # 1. Prefer 'gemini' (best for creative writing)
            # 2. Prefer 'llama-3' (strong instruction following)
            # 3. Prefer 'deepseek' (good reasoning)
            # 4. Prefer larger models ('70b', 'flash')
            # 5. Avoid tiny models ('nano', '1b', '3b')
            
            scored_models = []
            for mid in free_models:
                score = 0
                mid_lower = mid.lower()
                
                if "gemini" in mid_lower: score += 10
                if "llama-3" in mid_lower: score += 8
                if "deepseek" in mid_lower: score += 7
                if "phi-4" in mid_lower: score += 6
                
                if "flash" in mid_lower: score += 3
                if "exp" in mid_lower: score += 2
                if "70b" in mid_lower: score += 2
                
                if "nano" in mid_lower or "1b" in mid_lower or "3b" in mid_lower: score -= 20
                
                scored_models.append((score, mid))
            
            # Sort by score desc
            scored_models.sort(key=lambda x: x[0], reverse=True)
            
            best_models = [m[1] for m in scored_models[:5]] # Take top 5
            
            logging.info(f"✅ Selected Top Free Models: {best_models}")
            if not best_models:
                 return ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free"]
                 
            return best_models
            
        except Exception as e:
            logging.error(f"⚠️ Model discovery failed: {e}")
            # Fallback hardcoded list
            return ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free"]

    def _generate_script(self, rashi: str, date: str, period_type: str, system_prompt: str, user_prompt: str) -> dict:
        """Helper to try models in rotation."""
        errors = []
        for model in self.models:
            logging.info(f"🤖 Casting {period_type} chart using: {model}")
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                raw_content = response.choices[0].message.content
                return json.loads(raw_content)
                
            except Exception as e:
                logging.warning(f"⚠️ Model {model} failed: {e}")
                errors.append(f"{model}: {str(e)}")
                continue # Try next model
        
        logging.error(f"❌ All models failed: {errors}")
        raise Exception(f"All models failed to generate {period_type}. Errors: {errors}")

    def generate_daily_rashifal(self, rashi: str, date: str) -> dict:
        """Generates Daily Horoscope."""
        logging.info(f"✨ Astrologer: Generating Daily Horoscope for {rashi}...")
        
        system_prompt = """
        You are 'Rishiraj', an expert Vedic Astrologer. Tone: Mystical, Positive, Authoritative.
        Write a DAILY Horoscope Script in PURE HINDI.
        Do NOT mention specific dates.
        """
        
        user_prompt = f"""
        Generate a **Daily Horoscope** for **{rashi}** for {date}.
        Return ONLY valid JSON:
        {{
            "hook": "Short attention grabber (Hindi)",
            "intro": "Astrological context (Gochar)",
            "love": "Love prediction",
            "career": "Career prediction",
            "money": "Financial prediction",
            "health": "Health prediction",
            "remedy": "Specific Vedic remedy",
            "lucky_color": "Color",
            "lucky_number": "Number"
        }}
        """
        return self._generate_script(rashi, date, "Daily", system_prompt, user_prompt)

    def generate_monthly_forecast(self, rashi: str, month_year: str) -> dict:
        """Generates Monthly Horoscope (Detailed)."""
        logging.info(f"✨ Astrologer: Generating Monthly Horoscope for {rashi} ({month_year})...")
        
        system_prompt = """
        You are 'Rishiraj', an expert Vedic Astrologer. Tone: Detailed, Predictive, Guiding.
        Write a MONTHLY Horoscope Script in PURE HINDI.
        Focus on major planetary shifts (Sun transit, Moon phases).
        """
        
        user_prompt = f"""
        Generate a **Monthly Horoscope** for **{rashi}** for **{month_year}**.
        Return ONLY valid JSON:
        {{
            "hook": "Major theme of the month (Hindi)",
            "intro": "Overview of the month & planetary changes",
            "love": "Detailed Relationship forecast",
            "career": "Detailed Career & Business forecast",
            "money": "Financial opportunities & risks",
            "health": "Health warnings",
            "remedy": "Major monthly remedy (Upay)",
            "lucky_dates": "List of lucky dates"
        }}
        """
        return self._generate_script(rashi, month_year, "Monthly", system_prompt, user_prompt)

    def generate_yearly_forecast(self, rashi: str, year: str) -> dict:
        """Generates Yearly 2025+ Horoscope (Grand)."""
        logging.info(f"✨ Astrologer: Generating Yearly Horoscope for {rashi} ({year})...")
        
        system_prompt = """
        You are 'Rishiraj', the Grand Vedic Astrologer. Tone: Epic, Visionary, Comprehensive.
        Write a YEARLY 'Varshiphal' Script in PURE HINDI.
        Focus on Jupiter (Guru), Saturn (Shani), and Rahu/Ketu transits.
        """
        
        user_prompt = f"""
        Generate a **Yearly Horoscope** for **{rashi}** for the year **{year}**.
        Return ONLY valid JSON:
        {{
            "hook": "The biggest theme of the year (Hindi)",
            "intro": "Grand overview of 2025 for this sign",
            "love": "Love life analysis for the whole year",
            "career": "Career growth analysis",
            "money": "Wealth accumulation forecast",
            "health": "Major health periods to watch",
            "remedy": "Maha-Upay (Grand Remedy) for the year",
            "lucky_months": "Best months of the year"
        }}
        """
        return self._generate_script(rashi, year, "Yearly", system_prompt, user_prompt)

# Test Run (Uncomment to test)
# if __name__ == "__main__":
#     agent = AstrologerAgent()
#     print(json.dumps(agent.generate_daily_rashifal("Kumbh (Aquarius)", "2024-12-21"), indent=2, ensure_ascii=False))
