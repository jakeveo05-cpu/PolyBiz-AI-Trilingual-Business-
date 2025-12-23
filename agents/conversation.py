"""
Conversation Partner Agent - Role-play business scenarios
"""
from .base import BaseAgent


class ConversationPartner(BaseAgent):
    """AI agent for conversation practice with business scenarios"""
    
    SCENARIOS = {
        "job_interview": "Job interview at a multinational company",
        "client_meeting": "Meeting with a potential client",
        "negotiation": "Price negotiation with supplier",
        "presentation": "Presenting quarterly results",
        "networking": "Networking at a business conference",
        "email_call": "Following up on an email via phone call",
    }
    
    def __init__(self, language: str = "en", scenario: str = "networking"):
        super().__init__()
        self.language = language
        self.scenario = scenario
    
    def get_system_prompt(self) -> str:
        scenario_desc = self.SCENARIOS.get(self.scenario, self.scenario)
        
        lang_instructions = {
            "en": "Respond in English. Use natural business English.",
            "zh": "用中文回复。使用自然的商务中文。",
            "vi": "Trả lời bằng tiếng Việt. Sử dụng tiếng Việt thương mại tự nhiên."
        }
        
        return f"""You are a conversation partner for business language practice.

Current scenario: {scenario_desc}
Language: {self.language}

Your role:
1. Play the role of a business professional in this scenario
2. Keep responses natural and conversational (2-4 sentences)
3. After each exchange, provide brief feedback on the learner's language
4. Gently correct major errors without breaking the conversation flow
5. Gradually increase complexity as the conversation progresses

{lang_instructions.get(self.language, lang_instructions['en'])}

Response format:
🗣️ [Your response in character]

📝 Quick feedback: [1 sentence about their language use - optional, only if needed]

Keep the conversation flowing naturally. Be encouraging!"""
    
    async def respond(self, user_message: str) -> str:
        """Respond to user in the conversation"""
        return await self.chat(user_message)
    
    def change_scenario(self, scenario: str):
        """Change the conversation scenario"""
        self.scenario = scenario
