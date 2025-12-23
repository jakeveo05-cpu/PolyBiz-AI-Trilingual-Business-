"""
Test Toucan TTS integration
"""
import os
import sys

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "IMS-Toucan"))

def test_import():
    """Test if Toucan can be imported"""
    print("🔍 Testing Toucan TTS import...")
    try:
        from agents.tts_toucan import ToucanTTS, TOUCAN_AVAILABLE
        print(f"   TOUCAN_AVAILABLE: {TOUCAN_AVAILABLE}")
        
        if TOUCAN_AVAILABLE:
            print("✅ Toucan TTS is ready!")
            return True
        else:
            print("⚠️ Toucan TTS not fully loaded. Run setup_toucan.py first.")
            return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_synthesis():
    """Test TTS synthesis"""
    print("\n🔊 Testing TTS synthesis...")
    try:
        from agents.tts_toucan import ToucanTTS
        
        tts = ToucanTTS(device="cpu")
        
        # Test English
        print("   Generating English audio...")
        output_en = tts.synthesize(
            "Hello, welcome to PolyBiz AI.",
            output_path="test_output_en.wav",
            language="en"
        )
        print(f"   ✅ English: {output_en}")
        
        # Test Vietnamese
        print("   Generating Vietnamese audio...")
        output_vi = tts.synthesize(
            "Xin chào, chào mừng bạn đến với PolyBiz AI.",
            output_path="test_output_vi.wav",
            language="vi"
        )
        print(f"   ✅ Vietnamese: {output_vi}")
        
        # Test Chinese
        print("   Generating Chinese audio...")
        output_zh = tts.synthesize(
            "你好，欢迎来到PolyBiz AI。",
            output_path="test_output_zh.wav",
            language="zh"
        )
        print(f"   ✅ Chinese: {output_zh}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PolyBiz AI - Toucan TTS Test")
    print("=" * 50)
    
    if test_import():
        test_synthesis()
