import asyncio
import os
import random
import subprocess
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel

USER_DATA_DIR = os.path.expanduser("./playwright_x_profile")

# ==========================================
# TOOL 1: LIVE SPACE EMOJI BOT
# ==========================================
async def run_space_emoji_bot():
    print("\n" + "="*50)
    print("[+] Launching X Space Emoji Bot...")
    print("[+] Opens your browser. Log in, and join any live Space.")
    print("="*50 + "\n")

    async with async_playwright() as p:
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ],
            ignore_default_args=["--enable-automation"]
        )

        await browser_context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

        await page.goto("https://x.com/home", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        if "login" in page.url or "i/flow/login" in page.url:
            print("[!] Please log into your X account in the browser window, then press ENTER here...")
            input()
            await page.goto("https://x.com/home", wait_until="domcontentloaded")

        print("\n[+] Ready! Join any live Space in the browser window. Waiting for active Space...")
        in_space = False
        emoji_map = {
            "1": "😂",
            "2": "😮",
            "3": "😢",
            "4": "💜",
            "5": "💯",
            "6": "👏",
            "7": "✊",
            "8": "👍",
            "9": "👎",
            "10": "👋"
        }
        all_emojis = list(emoji_map.values())

        try:
            while True:
                url = page.url
                space_active = False
                try:
                    space_active = ("/i/spaces/" in url) or (await page.locator("button[aria-label*='React'], button[aria-label*='Reaction']").count() > 0)
                except Exception:
                    await asyncio.sleep(2)
                    continue

                if space_active:
                    if not in_space:
                        in_space = True
                        print(f"\n[+] Active Space detected!")
                        await asyncio.sleep(3)

                        try:
                            listen_btn = page.locator("button:has-text('Start listening')")
                            if await listen_btn.is_visible():
                                await listen_btn.click()
                                print("[+] Clicked 'Start listening'.")
                                await asyncio.sleep(2)
                        except Exception:
                            pass

                    # Clean Emoji Menu
                    print("\n" + "="*45)
                    print("         SELECT REACTION EMOJI")
                    print("="*45)
                    for k, v in emoji_map.items():
                        print(f" [{k}] {v}", end="  ")
                        if int(k) % 5 == 0:
                            print()
                    print("\n" + "="*45)
                    print(" [Enter] -> RANDOM EMOJI CHAOS MODE")
                    print("="*45)
                    
                    choice_input = input("Select emoji number (1-10) or press Enter for Random: ").strip()

                    is_random = (choice_input == "")
                    if is_random:
                        chosen_emoji = None
                        print("\n[+] Mode set to: RANDOM EMOJI CHAOS 🎲")
                    elif choice_input in emoji_map:
                        chosen_emoji = emoji_map[choice_input]
                    else:
                        print("[-] Invalid selection, defaulting to Random Chaos mode.")
                        chosen_emoji = None

                    try:
                        count = int(input(f"How many times to send?: ").strip() or "30")
                    except ValueError:
                        count = 30

                    delay = 0.018 # Slightly balanced speed to prevent DOM desync
                    target_label = "Random Chaos" if is_random else chosen_emoji
                    print(f"\n[+] Spaming {count} bursts of [{target_label}] at Ultra-Turbo speed ({delay}s)...")

                    try:
                        for i in range(count):
                            current_emoji = random.choice(all_emojis) if is_random else chosen_emoji

                            try:
                                react_btn = page.locator("button[aria-label='React'], button[aria-label='Reactions']").first
                                if await react_btn.is_visible():
                                    await react_btn.click()
                                    await asyncio.sleep(delay)

                                    tray_emoji_btn = page.locator(f"div[role='dialog'] button:has-text('{current_emoji}'), div.css-175oi2r button:has-text('{current_emoji}')").first
                                    if await tray_emoji_btn.count() > 0:
                                        await tray_emoji_btn.click()
                                        print(f"[{i+1}/{count}] Sent: {current_emoji}")
                                    else:
                                        fallback_btn = page.locator(f"button:has-text('{current_emoji}')").last
                                        if await fallback_btn.count() > 0:
                                            await fallback_btn.click()
                                            print(f"[{i+1}/{count}] Sent (fallback): {current_emoji}")
                            except Exception:
                                pass # Soft skip if a frame drops, keeping the loop flowing smoothly
                            
                            await asyncio.sleep(delay)
                    except Exception as e:
                        print(f"[-] Error sending reaction: {e}")

                    print("[+] Round complete! Ready for next round.")
                    await asyncio.sleep(4)
                else:
                    if in_space:
                        print("\n[-] Left Space or dock closed. Waiting for another...")
                        in_space = False
                    await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("\nExiting bot...")
        finally:
            await browser_context.close()

# ==========================================
# TOOL 2: RETRO PIXEL CLIPPER & RENDERER
# ==========================================
def create_pixel_avatar(pfp_url: str, size: int = 96) -> Image.Image:
    try:
        import requests
        response = requests.get(pfp_url, stream=True, timeout=10)
        img = Image.open(response.raw).convert("RGB")
    except Exception:
        img = Image.new("RGB", (size, size), color=(70, 130, 180))

    small = img.resize((16, 16), Image.Resampling.NEAREST)
    return small.resize((size, size), Image.Resampling.NEAREST)

def run_pixel_clipper():
    print("\n" + "="*50)
    print("[+] X Space Retro Pixel Clipper")
    print("="*50 + "\n")
    
    audio_path = input("Enter path to audio file (e.g., space_clip.mp3): ").strip()
    if not os.path.exists(audio_path):
        print(f"[-] Error: File '{audio_path}' not found.")
        return

    speaker_handle = input("Enter speaker X handle (e.g., elonmusk): ").strip()
    pfp_url = input("Enter speaker profile picture URL: ").strip()
    output_path = input("Enter output video filename (default: output_clip.mp4): ").strip() or "output_clip.mp4"

    print("\n[1/4] Loading Faster-Whisper model...")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    print(f"[2/4] Transcribing audio...")
    segments, _ = model.transcribe(audio_path, beam_size=5)
    transcript_segments = list(segments)

    width, height = 720, 1280
    fps = 30
    
    print("[3/4] Processing avatar pixel art...")
    pixel_avatar = create_pixel_avatar(pfp_url, size=112)

    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", 36)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", 24)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    duration = float(probe.stdout.strip()) if probe.stdout.strip() else 10.0
    total_frames = int(duration * fps)

    print(f"[4/4] Rendering {total_frames} frames into FFmpeg...")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "pipe:0",
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    bg_color = (15, 15, 35)
    box_color = (30, 30, 60)
    border_color = (0, 255, 204)

    for frame_idx in range(total_frames):
        current_time = frame_idx / fps
        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # CRT lines
        for y in range(0, height, 4):
            draw.line([(0, y), (width, y)], fill=(20, 20, 45), width=1)

        # Speaker Box
        draw.rectangle([50, 80, width - 50, 240], fill=box_color, outline=border_color, width=4)
        img.paste(pixel_avatar, (80, 104))
        draw.text((216, 115), f"@{speaker_handle}", fill=(255, 255, 255), font=font_large)
        draw.text((216, 165), "LIVE X SPACE CLIP", fill=(0, 255, 204), font=font_small)

        # Active Captions
        active_text = ""
        for seg in transcript_segments:
            if seg.start <= current_time <= seg.end:
                active_text = seg.text.strip()
                break

        if active_text:
            draw.rectangle([50, 600, width - 50, 950], fill=(10, 10, 25), outline=(255, 255, 255), width=3)
            words = active_text.split()
            lines, current_line = [], []
            for word in words:
                current_line.append(word)
                if len(" ".join(current_line)) > 24:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))

            y_offset = 640
            for line in lines[:4]:
                draw.text((80, y_offset), line, fill=(255, 255, 255), font=font_large)
                y_offset += 50

        process.stdin.write(img.tobytes())

    process.stdin.close()
    process.wait()
    print(f"\n[+] Rendered successfully to: {output_path}")

# ==========================================
# MAIN TUI MENU
# ==========================================
def main():
    while True:
        print("\n" + "="*40)
        print("   X SPACE TOOLKIT (Open Source)")
        print("="*40)
        print("1. Launch Live Space Emoji Bot")
        print("2. Render Retro Pixel Clip Video")
        print("3. Exit")
        print("="*40)
        
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            asyncio.run(run_space_emoji_bot())
        elif choice == "2":
            run_pixel_clipper()
        elif choice == "3":
            print("Exiting. Goodbye! 🤗")
            break
        else:
            print("[-] Invalid option. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
