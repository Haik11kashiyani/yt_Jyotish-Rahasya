# AI Video Studio: Jyotish Rahasya

An autonomous, "Industry Level" video production studio for Hindi Astrology.

## The Team (AI Agents)
- **Astrologer Agent**: Writes authentic Vedic scripts using OpenRouter LLMs.
- **Director Agent**: Visualizes the script into cinematic shot lists.
- **Narrator Agent**: Speaks in human-like Hindi using Neural TTS.
- **Editor Agent**: Fetches stock footage (Pexels) and renders the final video.

## Setup
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**:
   Create a `.env` file with:
   ```
   OPENROUTER_API_KEY=sk-or-your-key
   PEXELS_API_KEY=your-pexels-key
   ```

## Usage
Run the studio to produce a video for a specific Rashi:
```bash
python main.py --rashi "Kumbh (Aquarius)"
```

## GitHub Actions
This repo is configured to run daily on the cloud.
Check `.github/workflows/daily_video.yml`.
