import os
import argparse
import asyncio
import logging
from datetime import datetime

from agents.astrologer import AstrologerAgent
from agents.director import DirectorAgent
from agents.narrator import NarratorAgent
from agents.stock_fetcher import StockFetcher
from editor import EditorEngine
from moviepy.editor import AudioFileClip

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="AI Video Studio Orchestrator")
    parser.add_argument("--rashi", type=str, default="Mesh (Aries)", help="Target Rashi")
    args = parser.parse_args()
    
    date_str = datetime.now().strftime("%d %B %Y")
    
    print("\n" + "="*60)
    print(f"🌟 YT JYOTISH RAHASYA: Production Started 🌟")
    print(f"   Target: {args.rashi}")
    print(f"   Date: {date_str}")
    print("="*60 + "\n")
    
    # 1. The Astrologer (Script)
    try:
        astro = AstrologerAgent()
        script = astro.generate_daily_rashifal(args.rashi, date_str)
        if not script: raise Exception("Script Generation Failed")
    except Exception as e:
        print(f"❌ Astrologer Agent Error: {e}")
        return

    # 2. The Director (Visuals)
    try:
        director = DirectorAgent()
        screenplay = director.create_screenplay(script)
    except Exception as e:
        print(f"⚠️ Director Agent Error: {e}. Using defaults.")
        screenplay = {"scenes": {}} # Fallback

    # 3. Agents
    narrator = NarratorAgent()
    fetcher = StockFetcher()
    editor = EditorEngine()
    
    scenes = []
    
    sections = ["intro", "love", "career", "money", "health", "remedy"]
    
    print("\n🎬 STARTING PRODUCTION...")
    
    for section in sections:
        text = script.get(section, "")
        if not text: continue
            
        visual_query = screenplay["scenes"].get(section, "calm abstract background")
        
        print(f"\n   📍 Section: {section.upper()}")
        print(f"      📜 Script: {text[:40]}...")
        print(f"      👀 Visual: '{visual_query}'")
        
        # A. Voiceover
        os.makedirs("assets/temp", exist_ok=True)
        audio_path = f"assets/temp/{section}.mp3"
        narrator.speak(text, audio_path)
        
        if not os.path.exists(audio_path):
            print("      ⚠️ Audio generation failed, skipping section.")
            continue
            
        # Get Duration
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.5 # Add small breath pause
        except Exception as e:
            print(f"      ⚠️ Audio read error: {e}")
            duration = 5.0
        
        # B. Video Asset
        video_path = fetcher.search_video(visual_query, min_duration=int(duration))
        
        # C. Create Clip
        clip = editor.create_scene(video_path, text, duration)
        
        # Attach Audio (Critical Step)
        if hasattr(audio_clip, 'set_duration'): # Safety check
           clip = clip.set_audio(audio_clip)
        
        scenes.append(clip)
        
    if not scenes:
        print("❌ No scenes created.")
        return

    # 4. Final Assembly
    print(f"\n🎞️ Assembling Final Master...")
    output_filename = f"outputs/{args.rashi.split()[0]}_Rashifal_{datetime.now().strftime('%Y%m%d')}.mp4"
    os.makedirs("outputs", exist_ok=True)
    
    editor.assemble_final(scenes, output_filename)
    
    print(f"\n✅ PRODUCTION COMPLETE: {output_filename}")

if __name__ == "__main__":
    main()
