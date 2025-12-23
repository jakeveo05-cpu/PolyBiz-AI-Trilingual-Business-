"""
Vocabulary Extractor - AI agent to extract vocabulary from lessons/conversations
and create Anki decks automatically
"""
from .base import BaseAgent
from .anki_generator import AnkiCard, AnkiGenerator, AnkiConnect
from typing import List, Dict


class VocabularyExtractor(BaseAgent):
    """AI agent that extracts vocabulary and creates Anki decks"""
    
    def __init__(self):
        super().__init__()
        self.anki_generator = None
        self.anki_connect = None
    
    def get_system_prompt(self) -> str:
        return """You are a vocabulary extraction expert for language learning.

Your task is to analyze text (lessons, conversations, articles) and extract:
1. Key vocabulary words/phrases
2. Their meanings/translations
3. Example sentences showing usage
4. Context notes (when/how to use)

**Extraction Criteria**:
- Focus on business-relevant vocabulary
- Prioritize words/phrases learners at B1-C1 level should know
- Include idioms and collocations
- Avoid overly basic or overly advanced words
- Consider cultural context

**Output Format** (JSON):
```json
{
  "vocabulary": [
    {
      "word": "leverage",
      "translation_vi": "tận dụng, khai thác",
      "translation_zh": "利用",
      "definition": "to use something to maximum advantage",
      "example": "We need to leverage our existing customer base.",
      "context": "Used in business strategy discussions",
      "level": "B2",
      "tags": ["business", "strategy", "verb"]
    }
  ]
}
```

Be selective - quality over quantity. Extract 5-15 key items per text."""
    
    async def extract_from_text(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "vi",
        max_items: int = 15
    ) -> List[Dict]:
        """
        Extract vocabulary from text
        
        Args:
            text: Source text to analyze
            source_language: Language of the text
            target_language: Language for translations
            max_items: Maximum vocabulary items to extract
            
        Returns:
            List of vocabulary dictionaries
        """
        prompt = f"""Extract key vocabulary from this {source_language} text.
Provide translations in {target_language}.
Maximum {max_items} items.

TEXT:
{text}

Return as JSON array."""
        
        response = await self.chat(prompt)
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                vocab_list = json.loads(json_str)
                return vocab_list
            else:
                # Fallback: try to parse entire response
                return json.loads(response)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {response}")
            return []
    
    async def extract_from_conversation(
        self,
        conversation_history: List[Dict[str, str]],
        language: str = "en"
    ) -> List[Dict]:
        """
        Extract vocabulary from a conversation history
        
        Args:
            conversation_history: List of {"role": "user/assistant", "content": "..."}
            language: Language of conversation
            
        Returns:
            List of vocabulary dictionaries
        """
        # Combine conversation into text
        text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        return await self.extract_from_text(text, language)
    
    async def create_anki_deck_from_text(
        self,
        text: str,
        deck_name: str,
        language: str = "en",
        method: str = "file"  # "file" or "sync"
    ) -> str:
        """
        Extract vocabulary and create Anki deck in one step
        
        Args:
            text: Source text
            deck_name: Name for the Anki deck
            language: Source language
            method: "file" for .apkg or "sync" for AnkiConnect
            
        Returns:
            Path to .apkg file or success message
        """
        # Extract vocabulary
        vocab_list = await self.extract_from_text(text, language)
        
        if not vocab_list:
            return "No vocabulary extracted"
        
        # Convert to AnkiCards
        cards = []
        for vocab in vocab_list:
            card = AnkiCard(
                front=vocab.get("word", ""),
                back=vocab.get("translation_vi", vocab.get("translation_zh", "")),
                example=vocab.get("example", ""),
                tags=vocab.get("tags", []) + [language, "auto-generated"],
                extra_fields={
                    "notes": vocab.get("context", ""),
                    "definition": vocab.get("definition", "")
                }
            )
            cards.append(card)
        
        # Create deck based on method
        if method == "file":
            if not self.anki_generator:
                self.anki_generator = AnkiGenerator()
            
            deck_path = self.anki_generator.create_deck(
                deck_name=deck_name,
                cards=cards,
                template_name="vocabulary",
                description=f"Auto-generated from text analysis ({len(cards)} cards)"
            )
            return deck_path
        
        elif method == "sync":
            if not self.anki_connect:
                self.anki_connect = AnkiConnect()
            
            if not self.anki_connect.check_connection():
                return "Error: Cannot connect to Anki. Make sure Anki is running with AnkiConnect addon."
            
            note_ids = self.anki_connect.add_cards_bulk(deck_name, cards)
            self.anki_connect.sync()
            
            return f"Success: Added {len(note_ids)} cards to Anki and synced!"
        
        else:
            return f"Error: Unknown method '{method}'"
    
    async def suggest_deck_structure(
        self,
        learning_goal: str,
        current_level: str,
        language: str
    ) -> Dict:
        """
        AI suggests optimal deck structure for learning goal
        
        Args:
            learning_goal: e.g., "prepare for job interview", "improve email writing"
            current_level: A1-C2
            language: Target language
            
        Returns:
            Suggested deck structure with topics and priorities
        """
        prompt = f"""Suggest an optimal Anki deck structure for this learner:

Learning Goal: {learning_goal}
Current Level: {current_level}
Language: {language}

Provide:
1. Recommended deck names (3-5 decks)
2. Topics to cover in each deck
3. Estimated cards per deck
4. Learning sequence (which deck to study first)
5. Daily review recommendations

Format as JSON."""
        
        response = await self.chat(prompt)
        
        import json
        try:
            return json.loads(response)
        except:
            return {"raw_response": response}


# Convenience function
async def auto_create_deck_from_lesson(
    lesson_text: str,
    deck_name: str,
    language: str = "en",
    method: str = "file"
) -> str:
    """
    Quick function to create Anki deck from lesson text
    
    Args:
        lesson_text: The lesson content
        deck_name: Name for the deck
        language: Source language
        method: "file" or "sync"
        
    Returns:
        Path to .apkg or success message
    """
    extractor = VocabularyExtractor()
    return await extractor.create_anki_deck_from_text(
        text=lesson_text,
        deck_name=deck_name,
        language=language,
        method=method
    )
