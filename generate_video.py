#!/usr/bin/env python3
"""
Generate a motivational video with Van Gogh-inspired painterly scenes.

Style Reference: Van Gogh/woodcut printmaking style with bold graphic
illustration, flat color areas, strong warm/cool contrast, visible
brushstroke textures, silhouette-heavy compositions.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed")
    print("Install with: pip install google-genai")
    sys.exit(1)

# Configuration
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Enhanced artistic style prompt for human-like painting look
VAN_GOGH_STYLE = """Traditional oil painting in Van Gogh post-impressionist style.
Thick impasto brushstrokes with visible paint texture and canvas grain. Hand-painted aesthetic with organic imperfections.
Rich color mixing on canvas - warm golden ochre and amber contrasting with Prussian blue and teal.
Expressive brushwork like Starry Night. Natural color transitions, not digitally smooth.
Dramatic chiaroscuro lighting. Emotional depth. Museum quality fine art. 9:16 vertical composition.
NOT digital art, NOT 3D render, NOT photorealistic. Pure traditional painting aesthetic."""

# Scenes from scenes.md with Van Gogh style prompts
SCENES = [
    {
        "id": 1,
        "text": "You are growing in ways\nyour eyes can't see yet.",
        "objective": "Painterly mirror scene as she ties her hair.",
        "camera": "slow zoom-in",
        "prompt": f"""A young woman with long dark hair tying her hair in front of an ornate vintage mirror in a warmly lit bedroom.
Morning golden sunlight streaming through curtains creating dramatic rays. Her silhouette reflected in mirror.
Warm amber and ochre tones contrasting with deep blue shadows. Visible brushstroke textures on walls and fabrics.
{VAN_GOGH_STYLE}"""
    },
    {
        "id": 2,
        "text": "Grace writes the parts of you\ndiscipline never could.",
        "objective": "Painterly café window shot with her writing gently.",
        "camera": "slow outside-in drift",
        "prompt": f"""View through a rain-streaked café window at night. A young woman sits inside writing in a journal,
illuminated by warm interior lamplight. Steam rising from coffee cup. Cool blue night outside contrasts with warm amber interior.
Wet cobblestone street reflects lights. Bold brushstroke textures on glass and reflections.
{VAN_GOGH_STYLE}"""
    },
    {
        "id": 3,
        "text": "Every quiet yes becomes a doorway\nto who you're becoming.",
        "objective": "Painterly golden street walk, silhouette soft.",
        "camera": "slow follow",
        "prompt": f"""A young woman walking alone on a tree-lined European street at golden hour sunset.
Her silhouette backlit by intense orange sun creating long dramatic shadows on cobblestones.
Autumn trees with swirling Van Gogh-style leaves in amber and gold. Deep blue sky above.
Mediterranean architecture with warm stone buildings. Bold impasto brushwork throughout.
{VAN_GOGH_STYLE}"""
    },
    {
        "id": 4,
        "text": "You are not behind —\nyour bloom is simply deliberate.",
        "objective": "Painterly mountain sunrise.",
        "camera": "upward tilt",
        "prompt": f"""Majestic mountain landscape at sunrise with dramatic clouds. Snow-capped peaks catching first golden light.
Layers of mountains in atmospheric perspective. Swirling Van Gogh sky with bold brushstrokes in orange, pink, and deep blue.
Pine tree silhouettes in foreground. Mist in valleys. Expansive vista with emotional intensity.
{VAN_GOGH_STYLE}"""
    }
]

# Text overlay settings matching reference video
FONT_SIZE = 42  # Larger for better readability
TEXT_COLOR = "white"
TEXT_SHADOW_COLOR = "black@0.8"  # Stronger shadow
TEXT_Y_PERCENT = 0.25  # ~25% from top like reference


def find_api_key():
    """Find Gemini API key from environment or .env files."""
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        return api_key

    env_paths = [
        Path.home() / '.claude' / '.env',
        Path.home() / '.claude' / 'skills' / '.env',
        Path.home() / '.claude' / 'skills' / 'ai-multimodal' / '.env',
        Path(__file__).parent / '.claude' / '.env',
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        return line.split('=', 1)[1].strip().strip('"\'')
    return None


def generate_image(client, prompt: str, output_path: Path, max_retries: int = 5) -> bool:
    """Generate image using Imagen 4."""
    for attempt in range(max_retries):
        try:
            print(f"  Generating image (attempt {attempt + 1}/{max_retries})...")

            response = client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    numberOfImages=1,
                    aspectRatio='9:16',
                    imageSize='1K'
                )
            )

            for generated_image in response.generated_images:
                with open(output_path, 'wb') as f:
                    f.write(generated_image.image.image_bytes)
                print(f"  Saved: {output_path}")
                return True

        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                wait_time = min(2 ** attempt * 10, 120)
                print(f"  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif '503' in error_str or 'UNAVAILABLE' in error_str:
                wait_time = min(2 ** attempt * 5, 60)
                print(f"  Service unavailable. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  Error: {error_str}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(5)
    return False


def generate_video_from_image(client, image_path: Path, prompt: str, output_path: Path,
                               max_retries: int = 3) -> bool:
    """Generate animated video from image using Veo (image-to-video)."""
    for attempt in range(max_retries):
        try:
            print(f"  Generating video animation (attempt {attempt + 1}/{max_retries})...")
            print(f"  This may take 1-3 minutes...")

            # Load the image
            image_bytes = image_path.read_bytes()

            # Create image object for Veo
            reference_image = types.Image(
                image_bytes=image_bytes,
                mime_type='image/png'
            )

            # Generate video config
            config = types.GenerateVideosConfig(
                aspect_ratio='9:16',
                resolution='720p'
            )

            start_time = time.time()

            # Generate video from image using Veo 3.1 for better quality
            operation = client.models.generate_videos(
                model='veo-3.1-generate-preview',
                prompt=prompt,
                image=reference_image,
                config=config
            )

            # Poll until complete
            poll_count = 0
            while not operation.done:
                poll_count += 1
                if poll_count % 6 == 0:  # Update every 60s
                    elapsed = time.time() - start_time
                    print(f"    Still generating... ({elapsed:.0f}s)")
                time.sleep(10)
                operation = client.operations.get(operation)

            duration = time.time() - start_time
            print(f"  Generated in {duration:.0f}s")

            # Get the video
            generated_video = operation.response.generated_videos[0]
            client.files.download(file=generated_video.video)
            generated_video.video.save(str(output_path))

            print(f"  Saved: {output_path}")
            return True

        except Exception as e:
            error_str = str(e)
            print(f"  Error: {error_str}")
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                wait_time = min(2 ** attempt * 30, 180)
                print(f"  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif attempt == max_retries - 1:
                return False
            else:
                time.sleep(10)
    return False


def add_text_overlay_to_video(input_video: Path, output_video: Path, text: str) -> bool:
    """Add text overlay to video matching reference style. Also strips audio."""
    # Escape special characters for ffmpeg drawtext
    escaped_text = text.replace("\\", "\\\\").replace("'", "'\\''").replace(":", "\\:").replace("%", "\\%")

    # Use a clean serif font - try multiple options
    font_options = [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Times.ttc",
        "/System/Library/Fonts/NewYork.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]

    font_file = None
    for font in font_options:
        if Path(font).exists():
            font_file = font
            break

    if not font_file:
        font_file = "Times"

    # Calculate Y position
    y_expr = f"h*{TEXT_Y_PERCENT}"

    # Build drawtext filter with strong shadow for visibility
    # Using borderw for outline effect + shadow for better contrast
    drawtext_filter = (
        f"drawtext=fontfile='{font_file}':"
        f"text='{escaped_text}':"
        f"fontsize={FONT_SIZE}:"
        f"fontcolor=white:"
        f"borderw=2:"
        f"bordercolor=black@0.7:"
        f"shadowcolor=black@0.9:"
        f"shadowx=3:shadowy=3:"
        f"x=(w-text_w)/2:"
        f"y={y_expr}:"
        f"line_spacing=12"
    )

    # Strip audio (-an) and apply text overlay
    cmd = [
        'ffmpeg', '-y',
        '-i', str(input_video),
        '-vf', drawtext_filter,
        '-c:v', 'libx264',
        '-an',  # Remove audio completely
        '-preset', 'medium',
        str(output_video)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  FFmpeg error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  Error adding text: {e}")
        return False


def create_fallback_video(image_path: Path, output_video: Path, duration: float = 6.0,
                          motion: str = "zoom-in") -> bool:
    """Create video from image with Ken Burns effect as fallback."""

    if motion == "slow zoom-in":
        filter_complex = (
            f"[0:v]scale=8000:-1,zoompan=z='min(zoom+0.0003,1.12)':"
            f"d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s=720x1280,setsar=1[v]"
        )
    elif motion == "slow outside-in drift":
        filter_complex = (
            f"[0:v]scale=8000:-1,zoompan=z='min(zoom+0.0002,1.1)':"
            f"d={int(duration*25)}:x='if(eq(on,1),iw/4,x-0.3)':y='ih/2-(ih/zoom/2)':"
            f"s=720x1280,setsar=1[v]"
        )
    elif motion == "slow follow":
        filter_complex = (
            f"[0:v]scale=8000:-1,zoompan=z='1.08':"
            f"d={int(duration*25)}:x='if(eq(on,1),0,x+0.8)':y='ih/2-(ih/zoom/2)':"
            f"s=720x1280,setsar=1[v]"
        )
    elif motion == "upward tilt":
        filter_complex = (
            f"[0:v]scale=8000:-1,zoompan=z='1.1':"
            f"d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='if(eq(on,1),ih/3,y-0.6)':"
            f"s=720x1280,setsar=1[v]"
        )
    else:
        filter_complex = (
            f"[0:v]scale=8000:-1,zoompan=z='min(zoom+0.0003,1.1)':"
            f"d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s=720x1280,setsar=1[v]"
        )

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', str(image_path),
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-c:v', 'libx264',
        '-t', str(duration),
        '-pix_fmt', 'yuv420p',
        '-r', '25',
        str(output_video)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr.decode()}")
        return False


def concatenate_videos(video_files: list, output_video: Path) -> bool:
    """Concatenate multiple videos into one."""
    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, 'w') as f:
        for video in video_files:
            f.write(f"file '{video}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(output_video)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        concat_file.unlink()
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr.decode()}")
        return False


def main():
    print("=" * 60)
    print("Video Generation: 'When You're Becoming Someone New'")
    print("Style: Van Gogh-inspired painterly animation")
    print("=" * 60)

    api_key = find_api_key()
    if not api_key:
        print("\nError: GEMINI_API_KEY not found")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    scene_videos = []
    use_veo = True  # Try Veo first, fallback to Ken Burns

    for scene in SCENES:
        print(f"\n{'='*60}")
        print(f"Scene {scene['id']}: {scene['objective']}")
        print(f"Text: {scene['text'].replace(chr(10), ' | ')}")
        print(f"{'='*60}")

        # Paths
        raw_image = OUTPUT_DIR / f"scene_{scene['id']}_raw.png"
        raw_video = OUTPUT_DIR / f"scene_{scene['id']}_raw.mp4"
        final_video = OUTPUT_DIR / f"scene_{scene['id']}.mp4"

        # Step 1: Generate image
        if not raw_image.exists():
            print("\n[1/3] Generating Van Gogh-style image...")
            if not generate_image(client, scene['prompt'], raw_image):
                print(f"  FAILED - Skipping scene {scene['id']}")
                continue
        else:
            print(f"\n[1/3] Image exists: {raw_image.name}")

        # Step 2: Generate animated video from image
        print("\n[2/3] Creating animated video...")
        video_created = False

        if use_veo and not raw_video.exists():
            # Animation prompt for Veo - emphasize painterly motion
            animation_prompt = f"""Gentle living painting animation like a Van Gogh artwork coming to life.
{scene['camera']}. Subtle organic movement - brushstrokes seem to flow, colors breathe and shift naturally.
Clouds drift with painted texture, light dances like in impressionist art. Maintain thick impasto oil painting look throughout.
Movement should feel hand-animated, artistic, dreamlike. NOT realistic motion. 8 seconds of peaceful contemplation."""

            video_created = generate_video_from_image(
                client, raw_image, animation_prompt, raw_video
            )

            if not video_created:
                print("  Veo failed, using Ken Burns fallback...")
                use_veo = False  # Disable for remaining scenes

        if not video_created and not raw_video.exists():
            # Fallback: Ken Burns effect
            print("  Using Ken Burns motion effect...")
            video_created = create_fallback_video(
                raw_image, raw_video, 6.0, scene['camera']
            )
        elif raw_video.exists():
            print(f"  Video exists: {raw_video.name}")
            video_created = True

        if not video_created:
            print(f"  FAILED - Skipping scene {scene['id']}")
            continue

        # Step 3: Add text overlay
        print("\n[3/3] Adding text overlay...")
        if add_text_overlay_to_video(raw_video, final_video, scene['text']):
            scene_videos.append(final_video)
            print(f"  Scene {scene['id']} complete!")
        else:
            print(f"  Text overlay failed, using raw video...")
            scene_videos.append(raw_video)

    # Final: Concatenate all scenes
    if scene_videos:
        print(f"\n{'='*60}")
        print("FINAL ASSEMBLY")
        print(f"{'='*60}")

        final_output = OUTPUT_DIR / "final_video.mp4"
        print(f"Concatenating {len(scene_videos)} scenes...")

        if concatenate_videos(scene_videos, final_output):
            # Get video info
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries',
                 'format=duration', '-of', 'csv=p=0', str(final_output)],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip()) if result.stdout.strip() else 0

            print(f"\n{'='*60}")
            print(f"SUCCESS!")
            print(f"Output: {final_output}")
            print(f"Duration: {duration:.1f}s")
            print(f"{'='*60}")
        else:
            print("FAILED to concatenate videos")
    else:
        print("\nNo scenes were successfully generated.")


if __name__ == "__main__":
    main()
