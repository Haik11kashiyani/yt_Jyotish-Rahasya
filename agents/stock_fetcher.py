import os
import requests
import random
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StockFetcher:
    """
    Fetches high-quality stock video from Pexels API.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            logging.warning("⚠️ PEXELS_API_KEY missing. Stock fetch will fail.")
        
        self.headers = {"Authorization": self.api_key} if self.api_key else {}
        self.download_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "footage")
        os.makedirs(self.download_dir, exist_ok=True)

    def search_video(self, query: str, orientation: str = "portrait", min_duration: int = 5) -> str:
        """
        Search and download a video file matching the query.
        Returns local file path or None.
        """
        if not self.api_key:
            logging.error("❌ No Pexels Key")
            return None
            
        logging.info(f"🔍 Searching Pexels for: '{query}'")
        
        url = f"https://api.pexels.com/videos/search?query={query}&orientation={orientation}&per_page=5"
        
        try:
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            if not data.get("videos"):
                logging.warning(f"   ❌ No videos found for '{query}'")
                return None
                
            # Filter videos that are long enough
            valid_videos = [v for v in data["videos"] if v["duration"] >= min_duration]
            if not valid_videos:
                valid_videos = data["videos"] # Fallback
            
            # Pick random one
            video = random.choice(valid_videos)
            
            # Get best quality link (HD but not 4k to save bw, or best available)
            video_files = video["video_files"]
            # Sort by width desc
            video_files.sort(key=lambda x: x["width"], reverse=True)
            
            # Prefer 1080p
            selected_file = next((f for f in video_files if f["height"] >= 1080), video_files[0])
            download_url = selected_file["link"]
            
            # Filename
            safe_query = query.replace(" ", "_")[:20]
            filename = f"{safe_query}_{video['id']}.mp4"
            filepath = os.path.join(self.download_dir, filename)
            
            # Check if exists
            if os.path.exists(filepath):
                logging.info(f"   ✅ Cached: {filename}")
                return filepath
            
            # Download
            logging.info(f"   ⬇️ Downloading... ({selected_file['width']}x{selected_file['height']})")
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            logging.info(f"   ✅ Saved: {filename}")
            return filepath
            
        except Exception as e:
            logging.error(f"❌ Pexels Error: {e}")
            return None
