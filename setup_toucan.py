"""
Setup script for Toucan TTS
Run this once to install dependencies
"""
import subprocess
import sys
import os

def main():
    print("🔧 Setting up Toucan TTS...")
    
    # Check if IMS-Toucan exists
    toucan_path = os.path.join(os.path.dirname(__file__), "IMS-Toucan")
    if not os.path.exists(toucan_path):
        print("❌ IMS-Toucan not found. Clone it first:")
        print("   git clone https://github.com/DigitalPhonetics/IMS-Toucan.git")
        return False
    
    # Install core dependencies (minimal for inference)
    core_deps = [
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "numpy<2.0.0",
        "scipy",
        "librosa",
        "soundfile",
        "phonemizer",
        "pypinyin",
        "transphone",
        "huggingface-hub",
        "pydub",  # For audio processing
    ]
    
    print("📦 Installing core dependencies...")
    for dep in core_deps:
        print(f"   Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"])
    
    print("✅ Setup complete!")
    print("\n📝 Next steps:")
    print("1. Test TTS: python -c \"from agents import ToucanTTS; print('OK')\"")
    print("2. Run bot: python bots/discord_bot/main.py")
    
    return True

if __name__ == "__main__":
    main()
