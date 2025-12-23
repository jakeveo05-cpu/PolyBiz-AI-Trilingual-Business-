"""
Content Creator Agent - Tự động tạo content cho social media
"""
from .base import BaseAgent
from datetime import datetime


class ContentCreator(BaseAgent):
    """AI agent for creating social media content for the community"""
    
    CONTENT_TYPES = {
        "tip": "Quick Language Tip",
        "phrase": "Phrase of the Day",
        "mistake": "Common Mistake Monday",
        "culture": "Cultural Insight",
        "quiz": "Quick Quiz",
        "meme": "Language Meme/Humor",
        "story": "Success Story Template",
        "comparison": "Language Comparison (EN vs ZH)",
        "idiom": "Idiom Breakdown",
        "news": "Business News Vocabulary"
    }
    
    PLATFORMS = {
        "discord": {"max_length": 2000, "format": "markdown", "emoji": True},
        "telegram": {"max_length": 4096, "format": "markdown", "emoji": True},
        "linkedin": {"max_length": 3000, "format": "plain", "emoji": False},
        "tiktok": {"max_length": 150, "format": "script", "emoji": True},
        "instagram": {"max_length": 2200, "format": "plain", "emoji": True}
    }
    
    def get_system_prompt(self) -> str:
        return """You are a social media content creator for a trilingual business language learning community.

**Target Audience**: 
- Vietnamese professionals aged 18-30
- AI natives who use technology daily
- Learning English and/or Chinese for business
- Want practical, immediately applicable content

**Content Principles**:
1. **Value-First**: Every post must teach something useful
2. **Engaging**: Hook in first line, easy to consume
3. **Shareable**: Content people want to share with colleagues
4. **Community-Building**: Encourage interaction and discussion
5. **Consistent Voice**: Friendly, knowledgeable, encouraging

**Brand Voice**:
- Speak like a helpful senior colleague, not a teacher
- Use humor when appropriate
- Be direct and practical
- Celebrate small wins
- Acknowledge that learning is hard but worth it

**Formatting Guidelines**:
- Use emojis strategically (not excessively)
- Break up text with line breaks
- Use bullet points for lists
- Include a call-to-action
- Add relevant hashtags for discoverability"""
    
    async def create_tip_post(self, topic: str, language: str, platform: str = "discord") -> str:
        """Create a quick tip post"""
        platform_info = self.PLATFORMS.get(platform, self.PLATFORMS["discord"])
        
        prompt = f"""Create a "Quick Tip" post about "{topic}" for {language} learners.

Platform: {platform}
Max length: {platform_info['max_length']} characters
Format: {platform_info['format']}

Structure:
1. Hook (attention-grabbing first line)
2. The tip (clear and actionable)
3. Example (real business scenario)
4. Common mistake to avoid
5. Call-to-action (encourage engagement)

Make it practical for business professionals."""
        
        return await self.chat(prompt)
    
    async def create_phrase_of_day(self, language: str, category: str = "meetings") -> str:
        """Create Phrase of the Day post"""
        prompt = f"""Create a "Phrase of the Day" post for {language} learners.

Category: {category}

Structure:
📣 **Phrase of the Day**

🗣️ **[The Phrase]**
[Pronunciation guide]

📖 **Meaning**: [Clear explanation]

💼 **Use it when**: [Business situation]

📝 **Example Dialogue**:
A: [Context]
B: [Using the phrase]

🔄 **Variations**:
- [Formal version]
- [Casual version]

⚠️ **Don't confuse with**: [Similar phrase that means something different]

💬 **Your turn**: Use this phrase in a sentence about your work!

Include both English and Chinese if relevant, with Vietnamese explanations."""
        
        return await self.chat(prompt)
    
    async def create_common_mistake_post(self, language: str) -> str:
        """Create Common Mistake Monday post"""
        prompt = f"""Create a "Common Mistake Monday" post for {language} learners.

Structure:
🚨 **Common Mistake Monday**

❌ **What people say**: [Wrong version]
✅ **What to say instead**: [Correct version]

🤔 **Why it's wrong**:
[Clear explanation]

💼 **In business context**:
[Why this matters professionally]

📝 **More examples**:
❌ [Wrong] → ✅ [Right]
❌ [Wrong] → ✅ [Right]

💡 **Memory trick**:
[Easy way to remember]

🎯 **Quick practice**:
Which is correct?
A) [Option]
B) [Option]

(Answer in comments!)

Focus on mistakes Vietnamese speakers commonly make in {language}."""
        
        return await self.chat(prompt)
    
    async def create_cultural_insight(self, topic: str, cultures: list = ["US", "China"]) -> str:
        """Create cultural insight post"""
        cultures_str = " vs ".join(cultures)
        
        prompt = f"""Create a "Cultural Insight" post comparing business culture: {cultures_str}

Topic: {topic}

Structure:
🌍 **Cultural Insight: {topic}**

🇺🇸 **In the US**:
[How Americans handle this]

🇨🇳 **In China**:
[How Chinese handle this]

🇻🇳 **For Vietnamese professionals**:
[How to adapt when working with both]

💡 **Key Takeaway**:
[One actionable insight]

📖 **Useful phrases**:
- English: [Phrase for US context]
- Chinese: [Phrase for China context]

❓ **Discussion**:
Have you experienced this cultural difference? Share your story!

Make it practical and based on real business situations."""
        
        return await self.chat(prompt)
    
    async def create_quiz_post(self, topic: str, language: str, difficulty: str = "medium") -> str:
        """Create interactive quiz post"""
        prompt = f"""Create a quick quiz post about "{topic}" for {language} learners.

Difficulty: {difficulty}

Structure:
🧠 **Quick Quiz Time!**

**Topic**: {topic}
**Difficulty**: {"⭐" * (1 if difficulty == "easy" else 2 if difficulty == "medium" else 3)}

**Question 1**: [Multiple choice or fill-in-blank]
A) 
B)
C)
D)

**Question 2**: [Different format]

**Question 3**: [Scenario-based]

---
📊 **How did you do?**
- 3/3: 🏆 Business language pro!
- 2/3: 👍 Almost there!
- 1/3: 📚 Time to review!
- 0/3: 💪 Everyone starts somewhere!

**Answers**: (React to reveal / Check comments)

💬 **Share your score!**

Make questions practical and business-relevant."""
        
        return await self.chat(prompt)
    
    async def create_weekly_content_plan(self, theme: str, language: str) -> str:
        """Generate a week's worth of content ideas"""
        prompt = f"""Create a weekly content plan for our language learning community.

Theme: {theme}
Primary Language: {language}

**Format**:

📅 **Weekly Content Plan: {theme}**

**Monday** - Common Mistake
[Brief description]

**Tuesday** - Phrase of the Day
[Brief description]

**Wednesday** - Cultural Insight
[Brief description]

**Thursday** - Quick Tip
[Brief description]

**Friday** - Quiz/Challenge
[Brief description]

**Saturday** - Community Spotlight
[Engagement post idea]

**Sunday** - Week Recap + Preview
[Summary post idea]

**Hashtags for the week**: #[relevant] #[hashtags]

**Engagement goals**:
- [Specific interaction to encourage]

Make all content business-focused and practical."""
        
        return await self.chat(prompt)
    
    async def create_engagement_post(self, post_type: str = "discussion") -> str:
        """Create community engagement post"""
        prompt = f"""Create a community engagement post to spark discussion.

Type: {post_type}

Ideas:
- "This or That" business scenarios
- "What would you say?" situations
- Share your experience prompts
- Debate topics
- Celebration/milestone posts

Structure:
[Attention-grabbing opener]

[The question/prompt]

[Options or context]

[Encourage specific responses]

Make it relevant to business language learning and easy to respond to."""
        
        return await self.chat(prompt)
