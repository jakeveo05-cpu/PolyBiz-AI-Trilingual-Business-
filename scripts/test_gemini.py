#!/usr/bin/env python
"""
Test Google Gemini API connection
Run: python scripts/test_gemini.py
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()


async def test_gemini():
    """Test Gemini API"""
    print("\n" + "="*50)
    print("  🧪 Testing Google Gemini API")
    print("="*50 + "\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set in .env file")
        print("\nTo get a free API key:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Click 'Create API Key'")
        print("3. Copy the key and add to .env file:")
        print("   GOOGLE_API_KEY=your_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test import
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Run: pip install google-generativeai")
        return False
    
    # Configure and test
    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("\n📤 Sending test message...")
        response = model.generate_content(
            "Say 'Hello from Gemini!' in Vietnamese, English, and Chinese. Keep it short.",
            generation_config=genai.GenerationConfig(
                max_output_tokens=200,
                temperature=0.7
            )
        )
        
        print("\n📥 Response:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        print("\n✅ Gemini API working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        if "API_KEY_INVALID" in str(e):
            print("\n💡 Your API key is invalid. Please check:")
            print("   - Key is copied correctly")
            print("   - Key is not expired")
            print("   - Key has Gemini API enabled")
        elif "quota" in str(e).lower():
            print("\n💡 Rate limit reached. Wait a moment and try again.")
        
        return False


async def test_agent():
    """Test BaseAgent with Gemini"""
    print("\n" + "="*50)
    print("  🤖 Testing BaseAgent with Gemini")
    print("="*50 + "\n")
    
    try:
        from agents.base import BaseAgent
        
        class TestAgent(BaseAgent):
            def get_system_prompt(self):
                return "You are a helpful assistant. Keep responses brief."
        
        agent = TestAgent(model="gemini-1.5-flash")
        print(f"✅ Agent created with priority: {agent._api_priority}")
        
        print("\n📤 Testing agent.chat()...")
        response = await agent.chat("What is 2+2? Answer in one word.")
        
        print(f"📥 Response: {response}")
        print("\n✅ BaseAgent working with Gemini!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    gemini_ok = await test_gemini()
    
    if gemini_ok:
        await test_agent()
    
    print("\n" + "="*50)
    if gemini_ok:
        print("  🎉 All tests passed! Ready to use Gemini.")
    else:
        print("  ⚠️ Please fix the issues above.")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
