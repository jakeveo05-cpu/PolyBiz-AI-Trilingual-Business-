"""
Lesson Generator Agent - Tạo bài học personalized
"""
from .base import BaseAgent


class LessonGenerator(BaseAgent):
    """AI agent for generating personalized lessons"""
    
    LESSON_TYPES = {
        "vocabulary": "Business Vocabulary",
        "grammar": "Grammar Focus",
        "reading": "Reading Comprehension",
        "listening": "Listening Practice",
        "business_phrases": "Business Phrases & Idioms",
        "email_writing": "Email Writing",
        "meeting_skills": "Meeting Skills",
        "presentation": "Presentation Skills",
        "negotiation": "Negotiation Language",
        "small_talk": "Small Talk & Networking"
    }
    
    LEVELS = {
        "A1": "Beginner - Can understand basic phrases",
        "A2": "Elementary - Can communicate in simple tasks",
        "B1": "Intermediate - Can deal with most situations",
        "B2": "Upper Intermediate - Can interact with fluency",
        "C1": "Advanced - Can express fluently and spontaneously",
        "C2": "Proficient - Can understand virtually everything"
    }
    
    TOPICS = {
        "general_business": ["meetings", "emails", "phone calls", "presentations", "reports"],
        "tech": ["product demos", "sprint planning", "code reviews", "tech support", "startup pitches"],
        "finance": ["financial reports", "investment discussions", "banking", "budgeting", "forecasting"],
        "sales": ["cold calling", "client meetings", "closing deals", "objection handling", "follow-ups"],
        "hr": ["interviews", "performance reviews", "onboarding", "conflict resolution", "team building"]
    }
    
    def get_system_prompt(self) -> str:
        return """You are an expert language curriculum designer specializing in business language education for young professionals (18-30) who are AI natives.

**Design Principles**:
1. Practical & Immediately Applicable - No theoretical fluff
2. Real-world Scenarios - Based on actual business situations
3. Progressive Difficulty - Build on previous knowledge
4. Engaging Format - Interactive, not lecture-style
5. Cultural Context - Include US/China business culture notes
6. AI-Native Friendly - Reference how AI tools complement (not replace) these skills

**Lesson Structure**:

📚 **[Lesson Title]**
*[One-line description of what they'll learn]*

🎯 **Learning Objectives**
By the end of this lesson, you will be able to:
- [Specific, measurable objective 1]
- [Specific, measurable objective 2]
- [Specific, measurable objective 3]

📖 **Key Content**

**1. [Section Title]**
[Teaching content with examples]

💬 **Example Dialogue/Text**
[Realistic business scenario example]

📝 **Key Phrases**
| Phrase | Meaning | When to Use |
|--------|---------|-------------|
| ... | ... | ... |

✍️ **Practice Exercises**

**Exercise 1: [Type]** ⭐ Difficulty: [Easy/Medium/Hard]
[Exercise content]

**Exercise 2: [Type]**
[Exercise content]

**Exercise 3: [Type]**
[Exercise content]

💼 **Real-World Application**
*Scenario*: [Realistic business situation]
*Your Task*: [What they need to do]

🌍 **Cultural Note**
[US/China/Vietnam business culture insight related to the topic]

🤖 **AI Tool Tip**
[How AI tools can help with this skill, but why human skill still matters]

📝 **Homework Challenge**
[Self-study task they can share in community]

---
*Estimated time: [X] minutes*
*Best paired with: [Related lesson suggestion]*"""
    
    async def generate_lesson(
        self,
        topic: str,
        language: str,
        level: str = "B1",
        lesson_type: str = "vocabulary",
        industry: str = "general_business"
    ) -> str:
        """Generate a personalized lesson"""
        level_desc = self.LEVELS.get(level, self.LEVELS["B1"])
        type_desc = self.LESSON_TYPES.get(lesson_type, lesson_type)
        
        prompt = f"""Create a {type_desc} lesson about "{topic}" for {language} learners.

**Target Level**: {level} - {level_desc}
**Industry Focus**: {industry}
**Language**: {language} (with translations/explanations in Vietnamese for context)

Make it practical and engaging for young professionals (18-30) who are AI natives and want to succeed in global business.

Include:
- Real examples from {industry} context
- Common mistakes to avoid
- Cultural tips for US/China business settings
- How this skill complements AI tools"""
        
        return await self.chat(prompt)
    
    async def generate_daily_challenge(self, language: str, level: str = "B1", theme: str = None) -> str:
        """Generate a quick daily challenge (cached for 6 hours)"""
        from datetime import date
        from utils.cache import get_cache_manager
        
        # Cache key based on date, language, level
        today = date.today().isoformat()
        cache_key = f"daily_challenge:{today}:{language}:{level}"
        
        # Try cache first
        cache = get_cache_manager()
        cached_challenge = await cache.get(cache_key)
        if cached_challenge:
            self.logger.debug(f"Daily challenge cache hit: {cache_key}")
            return cached_challenge
        
        # Generate new challenge
        prompt = f"""Create a quick 5-minute daily challenge for {language} learners at {level} level.

{f'Theme: {theme}' if theme else 'Theme: Random business skill'}

The challenge should be:
- Quick to complete (5 minutes max)
- Business-relevant and practical
- Shareable (can post results in community)
- Fun and slightly competitive
- Include a "bonus" for extra challenge

**Format**:

🎯 **Daily Challenge: [Catchy Title]**
*[One-line hook]*

📋 **The Task**
[Clear instructions]

⏱️ **Time Limit**: 5 minutes

📊 **Share Your Result**
Post in the community:
- [What to share]
- [Format suggestion]

⭐ **Bonus Challenge** (Optional)
[Extra challenge for overachievers]

💡 **Why This Matters**
[One sentence on real-world application]

🏆 **Community Spotlight**
Tag your practice partner and challenge them!

---
*Tomorrow's theme hint: [Teaser for next challenge]*"""
        
        challenge = await self.chat(prompt)
        
        # Cache for 6 hours (21600 seconds)
        await cache.set(cache_key, challenge, ttl_seconds=21600)
        self.logger.debug(f"Daily challenge cached: {cache_key}")
        
        return challenge
    
    async def generate_weekly_plan(self, language: str, level: str, focus_area: str) -> str:
        """Generate a weekly learning plan"""
        prompt = f"""Create a 7-day learning plan for {language} at {level} level.

**Focus Area**: {focus_area}
**Daily Time Commitment**: 15-30 minutes

**Format**:

📅 **Week Plan: Mastering {focus_area}**

**Day 1 (Monday)**: Foundation
- [Activity 1] - 10 min
- [Activity 2] - 10 min
- Daily Challenge: [Quick task]

**Day 2 (Tuesday)**: Build
[...]

**Day 3 (Wednesday)**: Practice
[...]

**Day 4 (Thursday)**: Apply
[...]

**Day 5 (Friday)**: Challenge
[...]

**Day 6 (Saturday)**: Review & Community
[...]

**Day 7 (Sunday)**: Rest & Reflect
[...]

📈 **Weekly Goal**
By Sunday, you should be able to: [Measurable outcome]

🎯 **Accountability**
Share your Day 7 reflection in the community!"""
        
        return await self.chat(prompt)
    
    async def generate_vocabulary_set(self, topic: str, language: str, count: int = 10) -> str:
        """Generate a vocabulary set for a specific topic"""
        prompt = f"""Create a vocabulary set of {count} essential {language} words/phrases for "{topic}" in business context.

**Format for each word**:

**1. [Word/Phrase]** 
- 🔊 Pronunciation: [IPA or pinyin]
- 📖 Meaning: [Clear definition]
- 💼 Business Context: [When/how to use in business]
- 📝 Example: [Realistic business sentence]
- ⚠️ Common Mistake: [What learners often get wrong]
- 🔗 Related: [2-3 related words]

Include a mix of:
- Formal and informal variations
- Written vs spoken differences
- Cultural usage notes for US/China"""
        
        return await self.chat(prompt)
