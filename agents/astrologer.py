import os
import json
import logging
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
        self.model = "google/gemini-2.0-flash-thinking-exp:free" # Using a capable model for Hindi

    def generate_daily_rashifal(self, rashi: str, date: str) -> dict:
        """
        Generates a detailed daily horoscope for a specific Rashi.
        Returns a JSON structure with script sections.
        """
        logging.info(f"✨ Astrologer: Casting chart for {rashi} on {date}...")
        
        system_prompt = """
        You are 'Rishiraj', an expert Vedic Astrologer (Jyotish Acharya) with 25 years of experience.
        You perform deep calculations of Gochar (Planetary Transits), Nakshatras, and Yogas.
        
        Your task is to write a Daily Horoscope Script for a YouTube Video in HINDI.
        The tone should be: Mystical, Authoritative, yet Caring and Positive.
        
        CRITICAL RULES:
        1. Use PURE HINDI (Devanagari script). No Hinglish.
        2. Reference specific astrological events (e.g., "Moon in Bharni Nakshatra").
        3. Do NOT mention dates in the script text (so it stays evergreen).
        4. Organize the output strictly as a JSON object.
        """
        
        user_prompt = f"""
        Generate a Daily Horoscope for **{rashi} (Rashi)** for the date **{date}**.

        Return ONLY a raw JSON object with this exact structure:
        {{
            "hook": "A short, powerful opening sentence to grab attention (Hindi). E.g., 'Warning about money...'",
            "intro": "Greeting and astrological analysis (Gochar/Nakshatra impact) (2 sentences).",
            "love": "Prediction for Love/Relationship (2 sentences).",
            "career": "Prediction for Career/Business (2 sentences).",
            "money": "Prediction for Finance (2 sentences).",
            "health": "Prediction for Health (1 sentence).",
            "remedy": "A powerful, simple Vedic Upay (Remedy) for the day.",
            "lucky_color": "One color name.",
            "lucky_number": "One number."
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            return json.loads(raw_content)
            
        except Exception as e:
            logging.error(f"❌ Astrologer Prediction Failed: {e}")
            return None

# Test Run (Uncomment to test)
# if __name__ == "__main__":
#     agent = AstrologerAgent()
#     print(json.dumps(agent.generate_daily_rashifal("Kumbh (Aquarius)", "2024-12-21"), indent=2, ensure_ascii=False))
