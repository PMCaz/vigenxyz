# Van Gogh Video Generator

A Python script that generates motivational videos with Van Gogh-inspired painterly scenes using Google's AI models (Imagen 4.0 and Veo 3.1).

## 🎨 Overview

This project creates a 32-second motivational video featuring four scenes inspired by Van Gogh's post-impressionist style. Each scene combines AI-generated images, animated video sequences, and overlaid text to create an emotional, artistic experience.

## 📋 Prerequisites

### System Requirements
- Python 3.7+
- ffmpeg (for video processing)
- Internet connection (for API calls)
- Cross-platform support: Windows, macOS, Linux

### Python Dependencies
```bash
pip install google-genai
```

### API Access
You need a Google Gemini API key with access to:
- Vertex AI Imagen 4.0
- Vertex AI Veo 3.1

## 🔧 Environment Setup

### 1. Get API Key
Obtain a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Set Environment Variable
Set the `GEMINI_API_KEY` environment variable:

**Option A: System-wide**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Option B: .env file**
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-api-key-here
```

## 🚀 Usage

### Basic Run
```bash
python generate_video.py
```

### What It Does
1. **Reads Scenes**: Parses `scenes.md` for scene descriptions
2. **Generates Images**: Creates Van Gogh-style images for each scene
3. **Animates Videos**: Uses Veo 3.1 to animate images with painterly motion
4. **Adds Text**: Overlays motivational text on each video
5. **Concatenates**: Combines all scenes into a final 32-second video

### Output Files
All generated content is saved to the `output/` directory:
- `scene_[1-4]_raw.png` - Generated images
- `scene_[1-4]_raw.mp4` - Animated videos
- `scene_[1-4].mp4` - Videos with text overlays
- `final_video.mp4` - Complete concatenated video

## 📁 Project Structure

```
├── generate_video.py    # Main generation script
├── scenes.md           # Scene descriptions and prompts
├── ref.mp4            # Reference video (optional)
├── output/            # Generated content directory
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## ⚙️ Configuration

### Style Customization
Edit the `VAN_GOGH_STYLE` constant in `generate_video.py` to modify the artistic style.

### Text Settings
Modify these constants for text overlay customization:
- `FONT_SIZE`: Text size (default: 42)
- `TEXT_COLOR`: Text color (default: "white")
- `TEXT_Y_PERCENT`: Vertical position (default: 0.25)

### Video Settings
- **Resolution**: 720p (9:16 aspect ratio)
- **Duration**: 8 seconds per scene (32 seconds total)
- **Format**: MP4 with H.264 encoding

## 🛠️ Troubleshooting

### Common Issues

**"google-genai package not installed"**
```bash
pip install google-genai
```

**"GEMINI_API_KEY not found"**
- Check that the environment variable is set
- Verify the API key is valid and has required permissions

**Rate Limiting**
- The script includes automatic retry logic with exponential backoff
- Wait times increase for repeated failures

**Veo Generation Fails**
- Falls back to Ken Burns effect automatically
- Check internet connection and API quota

**FFmpeg Errors**
- Ensure ffmpeg is installed:
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/download.html
- Check that all output paths are writable
- Font issues: The script tries multiple font paths per platform; if text overlay fails, ensure system fonts are available

## 📝 Customization

### Adding Scenes
1. Add new scene objects to the `SCENES` list in `generate_video.py`
2. Include: id, text, objective, camera, and prompt
3. Update `scenes.md` with corresponding scene descriptions

### Modifying Prompts
Edit the `prompt` field in each scene object to change the visual content while maintaining the Van Gogh style.

## 📄 License

This project is for personal/educational use. Check Google's terms of service for AI model usage restrictions.