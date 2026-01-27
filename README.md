# 🔮 YT Jyotish Rahasya (Vedic Astrology Automation)

An autonomous, production-grade video studio for **Hindi Vedic Astrology (Rashifal)**.
Automatically generates, edits, and uploads YouTube Shorts/Videos for all 12 Rashis.

## 🌟 Features

- **Authentic Vedic Astrology** - Generates Daily/Monthly/Yearly forecasts.
- **Pure Hindi Content** - Scripts and narration in high-quality Hindi.
- **Automated Video Production** - Creates premium visuals with Rashi-specific themes.
- **YouTube Integration** - Auto-uploads with SEO-optimized titles, tags, and descriptions.
- **Reliable Scheduling** - Runs daily via GitHub Actions for all 12 signs.

## 🕉️ Supported Rashis (Zodiac Signs)

| Hindi Name              | English Name |
| ----------------------- | ------------ |
| **मेष (Mesh)**          | Aries        |
| **वृषभ (Vrishabh)**     | Taurus       |
| **मिथुन (Mithun)**      | Gemini       |
| **कर्क (Kark)**         | Cancer       |
| **सिंह (Singh)**        | Leo          |
| **कन्या (Kanya)**       | Virgo        |
| **तुला (Tula)**         | Libra        |
| **वृश्चिक (Vrishchik)** | Scorpio      |
| **धनु (Dhanu)**         | Sagittarius  |
| **मकर (Makar)**         | Capricorn    |
| **कुंभ (Kumbh)**        | Aquarius     |
| **मीन (Meen)**          | Pisces       |

## ⚙️ How It Works

1. **Astrologer Agent**: Uses AI to generate accurate Vedic predictions in Hindi.
2. **Narrator Agent**: Converts text to natural-sounding Hindi speech.
3. **Director Agent**: Selects appropriate visual themes and music.
4. **Editor Engine**: Renders high-quality video with animations and overlays.
5. **Uploader Agent**: Publishes to YouTube with viral metadata.

## 🚀 Usage

### Generate Daily Video

```bash
python main.py --rashi "Mesh (Aries)" --type shorts
```

### Generate Detailed Video

```bash
python main.py --rashi "Mesh (Aries)" --type detailed
```

### Generate & Upload

```bash
python main.py --rashi "Mesh (Aries)" --type shorts --upload
```

## 📂 Project Structure

- `main.py`: Core orchestration logic.
- `editor.py`: Video rendering and visual effects.
- `agents/`: AI agents for Astrology, Narration, and YouTube.
- `.github/workflows/`: Automation schedules for daily batches.
- `assets/`: Background images and music resources.

## 📅 Automation Schedule

The system runs automatically via GitHub Actions in 4 batches daily to cover all 12 signs before sunrise.

---

_Powered by AI & Vedic Wisdom_
