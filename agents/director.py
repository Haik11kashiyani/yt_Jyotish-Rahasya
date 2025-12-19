import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DirectorAgent:
    """
    The Director Agent converts a script into a Visual Screenplay.
    It decides the 'Mood' and selects specific, cinematic keywords for stock footage.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing!")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.model = "google/gemini-2.0-flash-thinking-exp:free"

    def create_screenplay(self, script_data: dict) -> dict:
        """
        Analyzes the horoscope script and generates a shot list.
        """
        logging.info("🎬 Director: visualizing the script...")
        
        sections = ["intro", "love", "career", "money", "health", "remedy"]
        full_script_text = " ".join([script_data.get(k, "") for k in sections])
        
        system_prompt = """
        You are a Christopher Nolan-esque Film Director.
        You transform simple text into CINEMATIC VISUALS.
        
        Your Goal: Select STOCK FOOTAGE keywords that match the emotion but are NOT cheesy.
        
        Rules for Keywords:
        1. Always English.
        2. Visual, Atmospheric, High Quality.
        3. NO text on screen descriptions.
        4. Examples:
           - Bad: "Sad man" -> Good: "Silhouette in rain window reflection dark, moody"
           - Bad: "Money" -> Good: "Golden coins falling slow motion cinematic lighting"
           - Bad: "Love" -> Good: "Couple holding hands sunset silhouette beach"
        """
        
        user_prompt = f"""
        Analyze this Hindi Horoscope Script and generate a JSON Screenplay.
        
        Script Context: {full_script_text}
        
        Return ONLY a JSON object with this structure:
        {{
            "mood": "Mysterious" | "Energetic" | "Peaceful" | "Dark",
            "music_style": "Ambient Drone" | "Upbeat classical" | "Deep meditation",
            "scenes": {{
                "intro": "cinematic keyword 1",
                "love": "cinematic keyword 2",
                "career": "cinematic keyword 3",
                "money": "cinematic keyword 4",
                "health": "cinematic keyword 5",
                "remedy": "cinematic keyword 6"
            }}
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
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"❌ Director Visualization Failed: {e}")
            # Fallback visuals
            return {
                "mood": "Peaceful",
                "scenes": {k: "Abstract golden particles slow motion" for k in sections}
            }
