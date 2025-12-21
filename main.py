import os
import sys
import argparse
import json
import logging
from datetime import datetime

from agents.astrologer import AstrologerAgent
from agents.director import DirectorAgent
from agents.narrator import NarratorAgent
from editor import EditorEngine
from moviepy.editor import AudioFileClip

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def produce_video_from_script(agents, rashi, title_suffix, script, date_str):
    """
    Orchestrates the production of a single video from a script.
    Uses gradient Rashi-themed backgrounds with karaoke text (no Pexels API).
    """
    narrator, editor, director = agents['narrator'], agents['editor'], agents['director']
    
    print(f"\n🎬 STARTING PRODUCTION: {title_suffix}...")
    scenes = []
    
    # Use Director to analyze script and get mood for music
    print(f"   🎬 Director analyzing content mood...")
    screenplay = director.create_screenplay(script)
    content_mood = screenplay.get("mood", "peaceful")
    print(f"   🎵 Detected mood: {content_mood}")
    
    # Define order of sections to ensure flow
    priority_order = ["hook", "intro", "love", "career", "money", "health", "remedy", "lucky_color", "lucky_number", "lucky_dates", "lucky_months"]

    for section in priority_order:
        if section not in script: 
            continue
        
        text = str(script[section])
        if not text or len(text) < 5: 
            continue
        
        print(f"\n   📍 Section: {section.upper()}")
        print(f"      📜 Script: {text[:50]}...")
        
        # A. Generate Voiceover
        os.makedirs(f"assets/temp/{title_suffix}", exist_ok=True)
        audio_path = f"assets/temp/{title_suffix}/{section}.mp3"
        subtitle_path = audio_path.replace(".mp3", ".json")
        
        narrator.speak(text, audio_path)
        
        if not os.path.exists(audio_path):
            print("      ⚠️ Audio generation failed, skipping section.")
            continue
            
        # B. Get Duration from Audio
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.3  # Small buffer
        except Exception as e:
            print(f"      ⚠️ Audio read error: {e}")
            duration = 5.0
            audio_clip = None
        
        # C. Load subtitle data for karaoke effect
        subtitle_data = None
        if os.path.exists(subtitle_path):
            try:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    subtitle_data = json.load(f)
                print(f"      🎤 Loaded {len(subtitle_data)} karaoke words")
            except:
                subtitle_data = None
        
        # D. Create Scene with Gradient Background + Rashi Image + Karaoke Text
        clip = editor.create_scene(rashi, text, duration, subtitle_data=subtitle_data)
        
        # E. Attach Audio
        if audio_clip:
            clip = clip.set_audio(audio_clip)
        
        scenes.append(clip)
        print(f"      ✅ Scene created: {duration:.1f}s")
        
    if not scenes:
        print("❌ No scenes created.")
        raise Exception("No scenes created.")

    # Final Assembly
    print(f"\n🎞️ Assembling Final Master: {title_suffix}")
    output_filename = f"outputs/{rashi.split()[0]}_{title_suffix}.mp4"
    os.makedirs("outputs", exist_ok=True)
    
    # Assemble with background music
    editor.assemble_final(scenes, output_filename, mood=content_mood)
    print(f"\n✅ CREATED: {output_filename}")


def main():
    parser = argparse.ArgumentParser(description="AI Video Studio Orchestrator")
    parser.add_argument("--rashi", type=str, default="Mesh (Aries)", help="Target Rashi")
    args = parser.parse_args()
    
    # Initialize Agents (No StockFetcher needed anymore!)
    agents = {
        'astrologer': AstrologerAgent(),
        'director': DirectorAgent(),
        'narrator': NarratorAgent(),
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
    print(f"   Style: Gradient Theme + Karaoke Text")
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
        import traceback
        traceback.print_exc()

    # --- 2. MONTHLY VIDEO (Run on 1st of Month) ---
    if today.day == 1: 
        try:
            print(f"\n📅 It is the 1st! Generating MONTHLY Horoscope for {month_year}...")
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
