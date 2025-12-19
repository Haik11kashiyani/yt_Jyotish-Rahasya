import os
import asyncio
import edge_tts
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NarratorAgent:
    """
    The Narrator Agent uses Edge-TTS (Neural) to generate human-like Hindi voiceovers.
    """
    
    def __init__(self):
        # Neural Voices: hi-IN-SwaraNeural (Female) or hi-IN-MadhurNeural (Male)
        self.voice = "hi-IN-SwaraNeural"
        self.rate = "+0%"   # Speed
        self.pitch = "+0Hz" # Pitch

    async def generate_audio(self, text: str, output_path: str):
        """
        Generates MP3 audio from text.
        """
        logging.info(f"🎙️ Narrator: Speaking {len(text)} chars...")
        
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            await communicate.save(output_path)
            
            if os.path.exists(output_path):
                logging.info(f"   ✅ Audio saved: {output_path}")
                return True
            return False
            
        except Exception as e:
            logging.error(f"❌ Narrator Failed: {e}")
            return False

    def speak(self, text: str, output_path: str):
        """Synchronous wrapper for async speak."""
        asyncio.run(self.generate_audio(text, output_path))
