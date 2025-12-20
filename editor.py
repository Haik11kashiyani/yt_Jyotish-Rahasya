import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip, vfx, concatenate_videoclips, CompositeAudioClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Monkeypatch ANTIALIAS for MoviePy compatibility with Pillow 10+
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EditorEngine:
    """
    Compiles the final video using MoviePy.
    """
    
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.font_path = "c:/Windows/Fonts/nirmala.ttf" # Standard Windows Hindi Font
        if not os.path.exists(self.font_path):
             self.font_path = "Arial" 

    def create_scene(self, video_path: str, text: str, duration: float, subtitle_path: str = None) -> CompositeVideoClip:
        """
        Creates a single scene with video background and text overlay.
        Supports perfect sync subtitles if subtitle_path is provided.
        """
        # 1. Background Video
        if video_path and os.path.exists(video_path):
            try:
                clip = VideoFileClip(video_path)
                # Loop if too short
                if clip.duration < duration:
                    clip = vfx.loop(clip, duration=duration)
                else:
                    clip = clip.subclip(0, duration)
            except Exception as e:
                logging.error(f"Error loading video {video_path}: {e}")
                clip = ColorClip(size=(self.width, self.height), color=(20, 20, 30), duration=duration)
        else:
            # Fallback Color Background
            clip = ColorClip(size=(self.width, self.height), color=(20, 20, 30), duration=duration)

        # Resize to fill vertical screen
        # Calculate aspect ratio
        if clip.h > 0:
            aspect_ratio = clip.w / clip.h
            target_ratio = self.width / self.height
            
            if aspect_ratio > target_ratio:
                # Too wide, crop sides
                new_w = int(self.height * aspect_ratio)
                clip = clip.resize(height=self.height)
                clip = clip.crop(x1=new_w//2 - self.width//2, width=self.width)
            else:
                # Too tall/narrow, resize by width
                clip = clip.resize(width=self.width)
                # Center vertically
                clip = clip.set_position("center")

        # 2. Text Overlay 
        if subtitle_path and os.path.exists(subtitle_path):
            # Perfect Sync Subtitles
            txt_clip = self._generate_subtitle_clip(subtitle_path, duration)
        else:
            # Fallback Static Overlay
            txt_img_path = self._generate_text_image(text)
            txt_clip = ImageClip(txt_img_path).set_duration(duration)
            txt_clip = txt_clip.set_position(("center", "bottom"))
        
        # 3. Composite
        final_clip = CompositeVideoClip([clip, txt_clip], size=(self.width, self.height))
        
        # Add fade in/out to look cinematic
        final_clip = final_clip.crossfadein(0.5)
        
        return final_clip
    
    def _generate_subtitle_clip(self, subtitle_path: str, duration: float) -> CompositeVideoClip:
        """Generates dynamic subtitle clips from JSON."""
        import json
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            subs = json.load(f)
            
        text_clips = []
        
        # Background box for subtitles
        bg_clip = ColorClip(size=(self.width, 250), color=(0,0,0), duration=duration)
        bg_clip = bg_clip.set_opacity(0.6).set_position(("center", "bottom"))
        
        for sub in subs:
            word = sub['text']
            start = sub['start']
            dur = sub['duration']
            
            # Create text clip for each word (or phrase)
            # Note: MoviePy TextClip requires ImageMagick. If not available, we might need a PIL fallback similar to _generate_text_image but for each word.
            # However, standard TextClip is cleaner for subtitles if configured.
            # Given likely environment constraints, I will use a PIL-based generator for safety.
            
            img_path = self._render_text_pill(word)
            
            clip = ImageClip(img_path).set_start(start).set_duration(dur)
            clip = clip.set_position(("center", 1750)) # Bottom position
            text_clips.append(clip)
            
        return CompositeVideoClip([bg_clip] + text_clips, size=(self.width, self.height))

    def _render_text_pill(self, text: str) -> str:
        """Renders small text snippet to image."""
        img_w, img_h = 1000, 150
        img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, 80)
        except:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0,0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (img_w - text_w) // 2
        
        # Yellow text with black stroke
        draw.text((x, 20), text, font=font, fill="#FFD700", stroke_width=3, stroke_fill="black")
        
        temp_path = f"assets/temp/word_{hash(text)}.png"
        img.save(temp_path)
        return temp_path

    def _generate_text_image(self, text: str) -> str:
        """Helper to render Hindi text to image using PIL."""
        img_w, img_h = 1080, 600 # Bottom area
        img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background box for text with rounded corners look (simulated)
        draw.rectangle([50, 50, img_w-50, img_h-50], fill=(0, 0, 0, 180))
        
        try:
            font = ImageFont.truetype(self.font_path, 55)
        except:
            font = ImageFont.load_default()

        # Simple word wrap
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_str = " ".join(current_line)
            bbox = draw.textbbox((0,0), line_str, font=font)
            if bbox[2] > img_w - 150:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        # Draw lines centered
        y = 100
        for line in lines:
            # Measure text width to center exact
            bbox = draw.textbbox((0,0), line, font=font)
            text_w = bbox[2] - bbox[0]
            x = (img_w - text_w) // 2
            draw.text((x, y), line, font=font, fill="white")
            y += 80
            
        temp_path = f"assets/temp/text_{hash(text)}.png"
        os.makedirs("assets/temp", exist_ok=True)
        img.save(temp_path)
        return temp_path

    def assemble_final(self, clips: list, output_path: str, watermark_path: str = None):
        """Concatenates prepared clips and adds background music."""
        if not clips:
            return
            
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Add Watermark
        if watermark_path:
             final_video = self.apply_watermark(final_video, watermark_path)
        
        # Add Background Music
        bg_music_path = "assets/music/bg.mp3"
        if os.path.exists(bg_music_path):
            try:
                bg_music = AudioFileClip(bg_music_path)
                # Loop music to match video duration
                if bg_music.duration < final_video.duration:
                    bg_music = vfx.loop(bg_music, duration=final_video.duration)
                else:
                    bg_music = bg_music.subclip(0, final_video.duration)
                
                # Lower volume to 15%
                bg_music = bg_music.volumex(0.15)
                
                # Composite with Voiceover
                final_audio = CompositeAudioClip([final_video.audio, bg_music])
                final_video = final_video.set_audio(final_audio)
                logging.info("   🎵 Background music added.")
            except Exception as e:
                logging.error(f"   ⚠️ Could not add background music: {e}")
        
        if hasattr(final_video, 'fps'):
            fps = final_video.fps if final_video.fps else 24
        else:
            fps = 24

        final_video.write_videofile(
            output_path, 
            fps=fps, 
            codec="libx264", 
            audio_codec="aac",
            threads=4,
            preset="medium"
        )

    def apply_watermark(self, video_clip, watermark_path: str):
        """Overlays a watermark image on the video."""
        if not os.path.exists(watermark_path):
            return video_clip
            
        watermark = ImageClip(watermark_path).set_duration(video_clip.duration)
        watermark = watermark.resize(height=150) # Scale down
        watermark = watermark.set_position(("left", "top")).set_opacity(0.8)
        
        return CompositeVideoClip([video_clip, watermark], size=video_clip.size)
