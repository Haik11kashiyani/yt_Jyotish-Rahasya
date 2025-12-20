import os
import sys
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

def produce_video_from_script(agents, rashi, title_suffix, script, date_str):
    """
    Orchestrates the production of a single video from a script.
    """
    narrator, fetcher, editor = agents['narrator'], agents['fetcher'], agents['editor']
    
    print(f"\n🎬 STARTING PRODUCTION: {title_suffix}...")
    scenes = []
    
    # Define order of sections to ensure flow
    # Common sections first, then specifics
    priority_order = ["hook", "intro", "love", "career", "money", "health", "remedy", "lucky_color", "lucky_number", "lucky_dates", "lucky_months"]
    
    # Visual Mapping Fallbacks
    visual_map = {
        "hook": "dramatic mystical nebula",
        "intro": "peaceful sunrise himalayas",
        "love": "romantic couple silhouette sunset",
        "career": "modern office city timelapse or success",
        "money": "gold coins falling slow motion luxury",
        "health": "yoga healthy lifestyle nature",
        "remedy": "hindu temple diya praying",
        "lucky_color": "abstract color background artistic",
        "lucky_number": "numerology mathematics abstract",
        "lucky_dates": "calendar pages turning",
        "lucky_months": "seasons changing time lapse"
    }

    for section in priority_order:
        if section not in script: continue
        
        text = str(script[section]) # Ensure it's string
        if not text or len(text) < 5: continue
            
        visual_query = visual_map.get(section, "calm abstract background")
        
        print(f"\n   📍 Section: {section.upper()}")
        print(f"      📜 Script: {text[:40]}...")
        
        # A. Voiceover
        os.makedirs(f"assets/temp/{title_suffix}", exist_ok=True)
        audio_path = f"assets/temp/{title_suffix}/{section}.mp3"
        narrator.speak(text, audio_path)
        
        if not os.path.exists(audio_path):
            print("      ⚠️ Audio generation failed, skipping.")
            continue
            
        # Get Duration
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.5 
        except Exception as e:
            print(f"      ⚠️ Audio read error: {e}")
            duration = 5.0
        
        # B. Video Asset
        video_path = fetcher.search_video(visual_query, min_duration=int(duration))
        
        # C. Create Clip with Subtitles
        subtitle_path = audio_path.replace(".mp3", ".json")
        clip = editor.create_scene(video_path, text, duration, subtitle_path=subtitle_path)
        
        # Attach Audio
        if hasattr(audio_clip, 'set_duration'):
           clip = clip.set_audio(audio_clip)
        
        scenes.append(clip)
        
    if not scenes:
        print("❌ No scenes created.")
        raise Exception("No scenes created.")

    # Final Assembly
    print(f"\n🎞️ Assembling Final Master: {title_suffix}")
    output_filename = f"outputs/{rashi.split()[0]}_{title_suffix}.mp4"
    os.makedirs("outputs", exist_ok=True)
    
    # Identify Watermark
    icon_path = f"assets/zodiac_icons/{rashi}.png"
    
    editor.assemble_final(scenes, output_filename, watermark_path=icon_path)
    print(f"\n✅ CREATED: {output_filename}")


def main():
    parser = argparse.ArgumentParser(description="AI Video Studio Orchestrator")
    parser.add_argument("--rashi", type=str, default="Mesh (Aries)", help="Target Rashi")
    args = parser.parse_args()
    
    # Initialize Agents Once
    agents = {
        'astrologer': AstrologerAgent(),
        'director': DirectorAgent(), # kept for future advanced screenplays
        'narrator': NarratorAgent(),
        'fetcher': StockFetcher(),
        'editor': EditorEngine()
    }
    
    today = datetime.now()
    date_str = today.strftime("%d %B %Y")
    month_year = today.strftime("%B %Y")
    year_str = today.strftime("%Y")
    
    print("\n" + "="*60)
    print(f"🌟 YT JYOTISH RAHASYA: Automation Engine 🌟")
    print(f"   Target: {args.rashi}")
    print(f"   Date: {date_str}")
    print("="*60 + "\n")
    
    # --- 1. DAILY VIDEO (Always Run) ---
    daily_success = False
    try:
        print("🔮 Generating DAILY Horoscope...")
        daily_script = agents['astrologer'].generate_daily_rashifal(args.rashi, date_str)
        produce_video_from_script(
            agents, 
            args.rashi, 
            f"Daily_{today.strftime('%Y%m%d')}", 
            daily_script, 
            date_str
        )
        daily_success = True
    except Exception as e:
        print(f"❌ Daily Video Failed: {e}")
        # traceback.print_exc() # Useful if imported

    # --- 2. MONTHLY VIDEO (Run on 1st of Month) ---
    # For testing, you can force this by commenting out the 'if' condition
    if today.day == 1: 
        try:
            print(f"\n📅 It is the 1st of the month! Generating MONTHLY Horoscope for {month_year}...")
            monthly_script = agents['astrologer'].generate_monthly_forecast(args.rashi, month_year)
            produce_video_from_script(
                agents,
                args.rashi,
                f"Monthly_{today.strftime('%B_%Y')}",
                monthly_script,
                month_year
            )
        except Exception as e:
            print(f"❌ Monthly Video Failed: {e}")

    # --- 3. YEARLY VIDEO (Run on Jan 1st) ---
    if today.day == 1 and today.month == 1:
        try:
            print(f"\n🎆 HAPPY NEW YEAR! Generating YEARLY Horoscope for {year_str}...")
            yearly_script = agents['astrologer'].generate_yearly_forecast(args.rashi, year_str)
            produce_video_from_script(
                agents,
                args.rashi,
                f"Yearly_{year_str}",
                yearly_script,
                year_str
            )
        except Exception as e:
            print(f"❌ Yearly Video Failed: {e}")
            
    # CRITICAL: Exit with error if Daily video failed
    if not daily_success:
        print("\n❌ CRITICAL: Daily Video Production Failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
