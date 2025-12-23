"""
Lesson Generator Agent - Tạo bài học personalized
"""
from .base import BaseAgent


class LessonGenerator(BaseAgent):
    """AI agent for generating personalized lessons"""
    
    LESSON_TYPES = [
        "vocabulary",
        "grammar", 
        "reading",
        "listening",
        "business_phrases",
        "email_writing",
        "meeting_skills"
    ]
    
    def get_system_prompt(self) -> str:
        return """You are an expert language curriculum designer specializing in business language education.

Create lessons that are:
1. Practical and immediately applicable in business contexts
2. Appropriate for the learner's level (A1-C2)
3. Engaging with real-world scenarios
4. Progressive in difficulty

Lesson structure:
📚 **Lesson Title**
🎯 **Learning Objectives** (2-3 bullet points)
📖 **Content** (main teaching material)
✍️ **Practice Exercises** (3-5 exercises)
💼 **Business Application** (real scenario to apply learning)
📝 **Homework** (optional self-study task)

Focus on Việt-Anh-Trung trilingual business contexts.
Include cultural notes when relevant."""
    
    async def generate_lesson(
        self,
        topic: str,
        language: str,
        level: str = "B1",
        lesson_type: str = "vocabulary"
    ) -> str:
        """Generate a personalized lesson"""
        prompt = f"""Create a {lesson_type} lesson about "{topic}" for {language} learners.

Target level: {level}
Focus: Business communication context

Make it practical and engaging for young professionals (18-30) who are AI natives."""
        
        return await self.chat(prompt)
    
    async def generate_daily_challenge(self, language: str, level: str = "B1") -> str:
        """Generate a quick daily challenge"""
        prompt = f"""Create a quick 5-minute daily challenge for {language} learners at {level} level.

The challenge should be:
- Quick to complete (5 minutes max)
- Business-relevant
- Shareable (can post results in community)
- Fun and engaging

Format:
🎯 **Today's Challenge**
[challenge description]

⏱️ Time: 5 minutes
📊 Share your result: [what to share]"""
        
        return await self.chat(prompt)
