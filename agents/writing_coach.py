"""
Writing Coach Agent - Chấm bài viết và feedback
"""
from .base import BaseAgent


class WritingCoach(BaseAgent):
    """AI agent for writing feedback and correction"""
    
    WRITING_TYPES = {
        "email": "Business Email",
        "report": "Business Report",
        "linkedin": "LinkedIn Post",
        "presentation": "Presentation Script",
        "meeting_notes": "Meeting Minutes",
        "proposal": "Business Proposal",
        "general": "General Business Writing"
    }
    
    RUBRICS = {
        "IELTS": {
            "criteria": ["Task Achievement", "Coherence & Cohesion", "Lexical Resource", "Grammatical Range & Accuracy"],
            "scale": "0-9"
        },
        "TOEFL": {
            "criteria": ["Development", "Organization", "Language Use"],
            "scale": "0-5"
        },
        "HSK": {
            "criteria": ["内容完整", "语法准确", "词汇丰富", "表达流畅"],
            "scale": "0-100"
        },
        "Business": {
            "criteria": ["Clarity", "Professionalism", "Tone", "Structure", "Grammar"],
            "scale": "1-10"
        }
    }
    
    def __init__(self, writing_type: str = "general", rubric: str = "Business"):
        super().__init__()
        self.writing_type = writing_type
        self.rubric = rubric
    
    def get_system_prompt(self) -> str:
        rubric_info = self.RUBRICS.get(self.rubric, self.RUBRICS["Business"])
        criteria = ", ".join(rubric_info["criteria"])
        
        return f"""You are an expert multilingual writing coach specializing in business communication.
You help learners improve their writing in English, Chinese, and Vietnamese.

**Writing Type**: {self.WRITING_TYPES.get(self.writing_type, "General")}
**Assessment Rubric**: {self.rubric} (Scale: {rubric_info['scale']})
**Criteria**: {criteria}

**Your Analysis Process**:
1. Detect the language automatically
2. Identify the writer's approximate level (A1-C2 / HSK 1-6)
3. Assess against the rubric criteria
4. Provide specific, actionable corrections
5. Explain the "why" behind each correction (educational)
6. Offer an improved version

**Response Format**:

📝 **Analysis**
- Language: [detected language]
- Level: [estimated level]
- Writing Type: [identified type]

📊 **Scores** ({self.rubric})
{chr(10).join([f'- {c}: [X/{rubric_info["scale"]}]' for c in rubric_info["criteria"]])}
- **Overall**: [X/{rubric_info['scale']}]

✅ **Corrected Version**
[Full corrected text with improvements]

📚 **Key Corrections**
1. ❌ [original] → ✅ [correction]
   💡 [explanation why this matters in business context]
2. ...

🎯 **Strengths**
- [What they did well]

💡 **Priority Improvements**
1. [Most important thing to work on]
2. [Second priority]

📖 **Learning Tip**
[One specific tip related to their main weakness]

**Guidelines**:
- Be encouraging but honest
- Focus on business communication effectiveness
- Explain cultural nuances when relevant
- Respond in the same language as the submitted text
- For emails: check subject line, greeting, closing, tone
- For LinkedIn: check hook, value, CTA, hashtags"""
    
    async def review(self, text: str, target_level: str = None, context: str = None) -> str:
        """Review a piece of writing and provide feedback"""
        additional_context = {}
        if target_level:
            additional_context["target_level"] = target_level
        if context:
            additional_context["additional_context"] = context
        
        return await self.chat(text, additional_context if additional_context else None)
    
    async def review_email(self, text: str, recipient: str = "client", tone: str = "professional") -> str:
        """Specialized review for business emails"""
        self.writing_type = "email"
        context = {
            "recipient_type": recipient,
            "expected_tone": tone,
            "check_points": ["subject line", "greeting", "body structure", "call-to-action", "closing", "signature"]
        }
        return await self.chat(text, context)
    
    async def review_linkedin(self, text: str, goal: str = "engagement") -> str:
        """Specialized review for LinkedIn posts"""
        self.writing_type = "linkedin"
        context = {
            "goal": goal,
            "check_points": ["hook (first line)", "value proposition", "storytelling", "call-to-action", "hashtags", "length optimization"]
        }
        return await self.chat(text, context)
    
    async def compare_versions(self, original: str, revised: str) -> str:
        """Compare original and revised versions, provide feedback on improvements"""
        prompt = f"""Compare these two versions of the same text:

**ORIGINAL:**
{original}

**REVISED:**
{revised}

Analyze:
1. What improvements were made?
2. What issues remain?
3. Any new issues introduced?
4. Overall progress assessment"""
        
        return await self.chat(prompt)
