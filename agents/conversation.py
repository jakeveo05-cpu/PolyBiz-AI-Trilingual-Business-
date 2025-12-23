"""
Conversation Partner Agent - Role-play business scenarios
"""
from .base import BaseAgent


class ConversationPartner(BaseAgent):
    """AI agent for conversation practice with business scenarios"""
    
    SCENARIOS = {
        "job_interview": {
            "en": "Job interview at a Fortune 500 company",
            "zh": "跨国公司面试",
            "vi": "Phỏng vấn tại công ty đa quốc gia"
        },
        "client_meeting": {
            "en": "First meeting with a potential client",
            "zh": "与潜在客户的首次会面",
            "vi": "Gặp gỡ khách hàng tiềm năng lần đầu"
        },
        "negotiation": {
            "en": "Price negotiation with supplier",
            "zh": "与供应商的价格谈判",
            "vi": "Đàm phán giá với nhà cung cấp"
        },
        "presentation": {
            "en": "Q&A after presenting quarterly results",
            "zh": "季度报告后的问答环节",
            "vi": "Hỏi đáp sau khi trình bày kết quả quý"
        },
        "networking": {
            "en": "Networking at a tech conference",
            "zh": "科技大会上的社交",
            "vi": "Networking tại hội nghị công nghệ"
        },
        "phone_followup": {
            "en": "Following up on an email via phone call",
            "zh": "电话跟进邮件",
            "vi": "Gọi điện theo dõi email"
        },
        "salary_negotiation": {
            "en": "Negotiating salary and benefits",
            "zh": "薪资福利谈判",
            "vi": "Đàm phán lương và phúc lợi"
        },
        "complaint_handling": {
            "en": "Handling a customer complaint",
            "zh": "处理客户投诉",
            "vi": "Xử lý khiếu nại khách hàng"
        }
    }
    
    SCENARIO_PROMPTS = {
        "job_interview": {
            "en": """You are a hiring manager at a Fortune 500 company.
- Ask behavioral questions using STAR method
- Probe for specific examples from their experience
- Test cultural fit and soft skills
- Be professional but friendly
- After 5-6 exchanges, provide comprehensive feedback

Start: "Thank you for coming in today. Before we dive in, tell me about yourself and what drew you to this opportunity." """,
            "zh": """你是一家跨国公司的招聘经理。
- 使用STAR方法提问行为面试问题
- 追问具体工作经历案例
- 测试文化契合度和软技能
- 专业但友好
- 5-6轮对话后提供全面反馈

开场白："感谢您今天来面试。在我们开始之前，请先介绍一下自己，以及是什么吸引您来应聘这个职位？" """,
            "vi": """Bạn là quản lý tuyển dụng tại công ty Fortune 500.
- Đặt câu hỏi hành vi theo phương pháp STAR
- Hỏi sâu về các ví dụ cụ thể từ kinh nghiệm
- Đánh giá sự phù hợp văn hóa
- Chuyên nghiệp nhưng thân thiện
- Sau 5-6 lượt trao đổi, đưa ra phản hồi toàn diện

Bắt đầu: "Cảm ơn bạn đã đến hôm nay. Trước khi bắt đầu, hãy giới thiệu về bản thân và điều gì thu hút bạn đến với cơ hội này?" """
        },
        "negotiation": {
            "en": """You are a procurement manager negotiating a contract.
Your goals:
- Get 15% discount on bulk orders
- Extend payment terms to Net 60
- Include free shipping for orders over $10,000

Be firm but professional. Push back on initial offers. Show you've done your research.

Start: "I've reviewed your proposal in detail. Before we proceed, I'd like to discuss the pricing structure. Our current vendor offers more competitive rates." """,
            "zh": """你是采购经理，正在谈判合同。
你的目标：
- 批量订单获得15%折扣
- 付款期限延长至60天
- 订单超过10万元免运费

态度坚定但专业。对初始报价提出异议。展示你做过调研。

开场白："我已经仔细看过你们的方案了。在继续之前，我想讨论一下价格结构。我们目前的供应商提供更有竞争力的价格。" """,
            "vi": """Bạn là quản lý mua hàng đang đàm phán hợp đồng.
Mục tiêu của bạn:
- Giảm giá 15% cho đơn hàng số lượng lớn
- Kéo dài thời hạn thanh toán lên 60 ngày
- Miễn phí vận chuyển cho đơn trên 100 triệu

Kiên quyết nhưng chuyên nghiệp. Phản đối các đề xuất ban đầu.

Bắt đầu: "Tôi đã xem kỹ đề xuất của bạn. Trước khi tiếp tục, tôi muốn thảo luận về cơ cấu giá. Nhà cung cấp hiện tại của chúng tôi đưa ra mức giá cạnh tranh hơn." """
        },
        "networking": {
            "en": """You are a senior executive at a tech conference. The learner approaches you.
- Be friendly but appear busy (checking phone occasionally)
- Share insights about industry trends when asked
- Ask about their work and interests
- Exchange contact info if conversation goes well
- Provide feedback on their networking approach

Start: "Hi there! Quite an event, isn't it? The keynote was fascinating. What brings you here today?" """,
            "zh": """你是科技大会上的高管。学习者主动与你交谈。
- 友好但显得很忙（偶尔看手机）
- 被问到时分享行业趋势见解
- 询问他们的工作和兴趣
- 如果对话顺利，交换联系方式
- 对他们的社交技巧提供反馈

开场白："你好！这个活动很棒，对吧？主题演讲很精彩。你今天来参加是为了什么？" """,
            "vi": """Bạn là giám đốc cấp cao tại hội nghị công nghệ. Học viên tiếp cận bạn.
- Thân thiện nhưng có vẻ bận (thỉnh thoảng xem điện thoại)
- Chia sẻ insights về xu hướng ngành khi được hỏi
- Hỏi về công việc và sở thích của họ
- Trao đổi thông tin liên lạc nếu cuộc trò chuyện tốt
- Đưa ra phản hồi về kỹ năng networking

Bắt đầu: "Chào bạn! Sự kiện tuyệt vời nhỉ? Bài keynote rất hay. Hôm nay bạn đến đây với mục đích gì?" """
        }
    }
    
    def __init__(self, language: str = "en", scenario: str = "networking", difficulty: str = "intermediate"):
        super().__init__()
        self.language = language
        self.scenario = scenario
        self.difficulty = difficulty
        self.exchange_count = 0
    
    def get_system_prompt(self) -> str:
        # Get scenario description
        scenario_info = self.SCENARIOS.get(self.scenario, {})
        scenario_desc = scenario_info.get(self.language, scenario_info.get("en", self.scenario))
        
        # Get detailed scenario prompt if available
        scenario_prompt = self.SCENARIO_PROMPTS.get(self.scenario, {}).get(self.language, "")
        
        lang_instructions = {
            "en": "Respond in natural business English. Use idioms and expressions common in US/UK business settings.",
            "zh": "用自然的商务中文回复。使用中国商务场合常见的表达方式和成语。",
            "vi": "Trả lời bằng tiếng Việt thương mại tự nhiên. Sử dụng các cách diễn đạt phổ biến trong môi trường kinh doanh Việt Nam."
        }
        
        difficulty_instructions = {
            "beginner": "Speak slowly and clearly. Use simple vocabulary. Provide more hints and encouragement.",
            "intermediate": "Use natural pace. Mix simple and complex sentences. Provide moderate challenge.",
            "advanced": "Speak naturally with idioms and cultural references. Challenge the learner. Expect professional-level responses."
        }
        
        return f"""You are a conversation partner for business language practice.

**Scenario**: {scenario_desc}
**Language**: {self.language}
**Difficulty**: {self.difficulty}

{scenario_prompt}

**Your Role**:
1. Stay in character throughout the conversation
2. Keep responses natural and conversational (2-4 sentences)
3. {difficulty_instructions.get(self.difficulty, difficulty_instructions['intermediate'])}
4. After each exchange, provide brief language feedback ONLY if there's a notable error or great usage
5. Track conversation progress and wrap up naturally after 6-8 exchanges

{lang_instructions.get(self.language, lang_instructions['en'])}

**Response Format**:
🗣️ [Your in-character response]

📝 [Optional: Brief feedback on language use - skip if nothing notable]

**Important**: 
- Don't break character unless providing feedback
- Make the conversation feel real and challenging
- Adapt to the learner's level based on their responses"""
    
    async def respond(self, user_message: str) -> str:
        """Respond to user in the conversation"""
        self.exchange_count += 1
        
        # Add context about exchange count
        context = {"exchange_number": self.exchange_count}
        
        # If reaching end of conversation, signal wrap-up
        if self.exchange_count >= 6:
            context["instruction"] = "Start wrapping up the conversation naturally. After this exchange, provide a summary of the learner's performance."
        
        return await self.chat(user_message, context)
    
    def change_scenario(self, scenario: str):
        """Change the conversation scenario"""
        self.scenario = scenario
        self.exchange_count = 0
    
    def reset(self):
        """Reset conversation state"""
        self.exchange_count = 0
    
    def get_available_scenarios(self) -> dict:
        """Return available scenarios for current language"""
        return {k: v.get(self.language, v.get("en")) for k, v in self.SCENARIOS.items()}
