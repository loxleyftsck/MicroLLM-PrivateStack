#!/usr/bin/env python3
"""
Model Download Script
Downloads DeepSeek-R1 1.5B GGUF model - Alternative methods
"""

import os
import sys
import urllib.request
from pathlib import Path

# Model configuration - Using alternative smaller model first
MODELS = {
    "qwen-0.5b": {
        "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "name": "qwen-0.5b-q4.gguf",
        "size": "~350MB"
    },
    "deepseek-1.5b": {
        "url": "https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
        "name": "deepseek-r1-1.5b-q4.gguf",
        "size": "~1GB"
    }
}

MODELS_DIR = Path(__file__).parent.parent / "models"


def download_with_progress(url: str, dest: Path):
    """Download file with progress bar"""
    print(f"Downloading to: {dest}")
    print(f"Source: {url}")
    print()
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            bar_length = 50
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            
            print(f"\r[{bar}] {percent:.1f}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)", end='', flush=True)
        else:
            mb_downloaded = downloaded / (1024 * 1024)
            print(f"\rDownloaded: {mb_downloaded:.1f}MB...", end='', flush=True)
    
    try:
        # Add user agent to avoid blocks
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, dest, reporthook=report_progress)
        print(f"\n✓ Download completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False


def main():
    """Main download logic"""
    print("=" * 70)
    print("MicroLLM-PrivateStack - Model Download")
    print("=" * 70)
    print()
    
    print("Available models:")
    print("1. Qwen 0.5B (Recommended for testing) - 350MB")
    print("2. DeepSeek-R1 1.5B - 1GB")
    print()
    
    choice = input("Select model (1 or 2, default=1): ").strip() or "1"
    
    if choice == "1":
        model_key = "qwen-0.5b"
    elif choice == "2":
        model_key = "deepseek-1.5b"
    else:
        print("Invalid choice. Defaulting to Qwen 0.5B")
        model_key = "qwen-0.5b"
    
    model = MODELS[model_key]
    
    # Create models directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    model_path = MODELS_DIR / model["name"]
    
    # Check if already exists
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"Model already exists: {model_path}")
        print(f"Size: {size_mb:.1f}MB")
        print()
        
        response = input("Download again? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping download.")
            print(f"\nUpdate .env file:")
            print(f'MODEL_PATH=./models/{model["name"]}')
            return 0
        
        # Remove existing file
        model_path.unlink()
    
    print(f"\nDownloading {model_key} ({model['size']})...")
    print("This may take a few minutes depending on your connection.")
    print()
    
    # Download
    success = download_with_progress(model["url"], model_path)
    
    if success:
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"\nModel downloaded successfully!")
        print(f"  Path: {model_path}")
        print(f"  Size: {size_mb:.1f}MB")
        print(f"\nUpdate your .env file (or create from .env.example):")
        print(f'  MODEL_PATH=./models/{model["name"]}')
        print(f"\nYou can now run the server:")
        print(f"  cd backend")
        print(f"  python api_gateway.py")
        return 0
    else:
        print("\n" + "=" * 70)
        print("Download failed. Manual download instructions:")
        print("=" * 70)
        print(f"\n1. Visit: {model['url']}")
        print(f"2. Download the file manually")
        print(f"3. Save it as: {model_path}")
        print(f"\nOr use curl/wget:")
        print(f'  curl -L "{model["url"]}" -o "{model_path}"')
        return 1


if __name__ == "__main__":
    sys.exit(main())
