"""
Anki Flashcard Generator - Auto-create Anki decks for vocabulary learning
Supports both genanki (standalone .apkg) and AnkiConnect (live sync)
"""
import os
import json
import random
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

# genanki for standalone deck generation
try:
    import genanki
    GENANKI_AVAILABLE = True
except ImportError:
    GENANKI_AVAILABLE = False

# requests for AnkiConnect API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AnkiCard:
    """Represents a single flashcard"""
    
    def __init__(
        self,
        front: str,
        back: str,
        example: str = "",
        audio_path: str = None,
        tags: List[str] = None,
        extra_fields: Dict[str, str] = None
    ):
        self.front = front
        self.back = back
        self.example = example
        self.audio_path = audio_path
        self.tags = tags or []
        self.extra_fields = extra_fields or {}


class AnkiDeckTemplate:
    """Pre-defined deck templates for different learning purposes"""
    
    TEMPLATES = {
        "vocabulary": {
            "name": "Business Vocabulary",
            "description": "Essential business vocabulary with examples",
            "fields": ["Word", "Translation", "Example", "Audio", "Notes"],
            "card_template": """
                <div class="front">{{Word}}</div>
                ---
                <div class="back">
                    <div class="translation">{{Translation}}</div>
                    <div class="example">{{Example}}</div>
                    {{Audio}}
                    <div class="notes">{{Notes}}</div>
                </div>
            """
        },
        "phrases": {
            "name": "Business Phrases",
            "description": "Common business phrases and idioms",
            "fields": ["Phrase", "Meaning", "Context", "Example", "Audio"],
            "card_template": """
                <div class="front">{{Phrase}}</div>
                ---
                <div class="back">
                    <div class="meaning">{{Meaning}}</div>
                    <div class="context">When to use: {{Context}}</div>
                    <div class="example">Example: {{Example}}</div>
                    {{Audio}}
                </div>
            """
        },
        "sentences": {
            "name": "Sentence Patterns",
            "description": "Business sentence patterns and structures",
            "fields": ["Pattern", "Translation", "Example1", "Example2", "Notes"],
            "card_template": """
                <div class="front">{{Pattern}}</div>
                ---
                <div class="back">
                    <div class="translation">{{Translation}}</div>
                    <div class="examples">
                        <p>Example 1: {{Example1}}</p>
                        <p>Example 2: {{Example2}}</p>
                    </div>
                    <div class="notes">{{Notes}}</div>
                </div>
            """
        },
        "conversation": {
            "name": "Conversation Practice",
            "description": "Business conversation scenarios",
            "fields": ["Situation", "YourLine", "Response", "Audio", "Notes"],
            "card_template": """
                <div class="front">
                    <div class="situation">{{Situation}}</div>
                    <div class="your-line">You: {{YourLine}}</div>
                </div>
                ---
                <div class="back">
                    <div class="response">Response: {{Response}}</div>
                    {{Audio}}
                    <div class="notes">{{Notes}}</div>
                </div>
            """
        }
    }


class AnkiGenerator:
    """Generate Anki decks using genanki (standalone .apkg files)"""
    
    def __init__(self, output_dir: str = "anki_decks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if not GENANKI_AVAILABLE:
            raise ImportError("genanki not installed. Run: pip install genanki")
    
    def _generate_id(self, text: str) -> int:
        """Generate consistent ID from text"""
        return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    
    def create_model(self, template_name: str = "vocabulary") -> genanki.Model:
        """Create Anki note model from template"""
        template = AnkiDeckTemplate.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        model_id = self._generate_id(f"polybiz_{template_name}")
        
        fields = [{"name": field} for field in template["fields"]]
        
        templates = [{
            "name": "Card 1",
            "qfmt": template["card_template"].split("---")[0],
            "afmt": template["card_template"].split("---")[1]
        }]
        
        css = """
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .front { font-size: 24px; font-weight: bold; }
        .translation { color: #2196F3; margin: 10px 0; }
        .example { color: #666; font-style: italic; margin: 10px 0; }
        .notes { color: #999; font-size: 14px; margin-top: 10px; }
        """
        
        return genanki.Model(
            model_id,
            template["name"],
            fields=fields,
            templates=templates,
            css=css
        )
    
    def create_deck(
        self,
        deck_name: str,
        cards: List[AnkiCard],
        template_name: str = "vocabulary",
        description: str = ""
    ) -> str:
        """
        Create an Anki deck and return path to .apkg file
        
        Args:
            deck_name: Name of the deck
            cards: List of AnkiCard objects
            template_name: Template to use
            description: Deck description
            
        Returns:
            Path to generated .apkg file
        """
        deck_id = self._generate_id(deck_name)
        deck = genanki.Deck(deck_id, deck_name)
        deck.description = description
        
        model = self.create_model(template_name)
        
        media_files = []
        
        for card in cards:
            # Prepare fields based on template
            if template_name == "vocabulary":
                fields = [
                    card.front,
                    card.back,
                    card.example,
                    f"[sound:{os.path.basename(card.audio_path)}]" if card.audio_path else "",
                    card.extra_fields.get("notes", "")
                ]
            elif template_name == "phrases":
                fields = [
                    card.front,
                    card.back,
                    card.extra_fields.get("context", ""),
                    card.example,
                    f"[sound:{os.path.basename(card.audio_path)}]" if card.audio_path else ""
                ]
            else:
                # Generic fallback
                fields = [card.front, card.back, card.example, "", ""]
            
            note = genanki.Note(
                model=model,
                fields=fields,
                tags=card.tags
            )
            deck.add_note(note)
            
            # Collect media files
            if card.audio_path and os.path.exists(card.audio_path):
                media_files.append(card.audio_path)
        
        # Generate package
        output_path = self.output_dir / f"{deck_name.replace(' ', '_')}.apkg"
        package = genanki.Package(deck)
        package.media_files = media_files
        package.write_to_file(str(output_path))
        
        return str(output_path)
    
    def create_deck_from_lesson(
        self,
        lesson_content: str,
        deck_name: str,
        language: str = "en"
    ) -> str:
        """
        Parse lesson content and create Anki deck
        AI will extract vocabulary/phrases from lesson
        """
        # This would use AI to extract cards from lesson
        # For now, placeholder
        cards = []
        # TODO: Implement AI extraction
        return self.create_deck(deck_name, cards)


class AnkiConnect:
    """Connect to Anki via AnkiConnect addon for live sync"""
    
    def __init__(self, url: str = "http://localhost:8765"):
        self.url = url
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not installed. Run: pip install requests")
    
    def _invoke(self, action: str, **params) -> dict:
        """Invoke AnkiConnect API"""
        payload = {
            "action": action,
            "version": 6,
            "params": params
        }
        
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                raise Exception(f"AnkiConnect error: {result['error']}")
            
            return result.get("result")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Cannot connect to Anki. Make sure:\n"
                "1. Anki is running\n"
                "2. AnkiConnect addon is installed\n"
                "3. Anki is not showing any dialogs"
            )
    
    def check_connection(self) -> bool:
        """Check if AnkiConnect is available"""
        try:
            self._invoke("version")
            return True
        except:
            return False
    
    def create_deck(self, deck_name: str) -> None:
        """Create a new deck in Anki"""
        self._invoke("createDeck", deck=deck_name)
    
    def add_note(
        self,
        deck_name: str,
        front: str,
        back: str,
        tags: List[str] = None,
        audio_path: str = None
    ) -> int:
        """
        Add a note to Anki
        
        Returns:
            Note ID
        """
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": tags or [],
            "audio": []
        }
        
        if audio_path and os.path.exists(audio_path):
            note["audio"].append({
                "path": audio_path,
                "filename": os.path.basename(audio_path),
                "fields": ["Back"]
            })
        
        return self._invoke("addNote", note=note)
    
    def add_cards_bulk(
        self,
        deck_name: str,
        cards: List[AnkiCard]
    ) -> List[int]:
        """Add multiple cards at once"""
        # Create deck if doesn't exist
        self.create_deck(deck_name)
        
        note_ids = []
        for card in cards:
            note_id = self.add_note(
                deck_name=deck_name,
                front=card.front,
                back=f"{card.back}\n\n{card.example}",
                tags=card.tags,
                audio_path=card.audio_path
            )
            note_ids.append(note_id)
        
        return note_ids
    
    def get_deck_names(self) -> List[str]:
        """Get all deck names"""
        return self._invoke("deckNames")
    
    def sync(self) -> None:
        """Trigger Anki sync"""
        self._invoke("sync")


# Convenience functions
def create_vocabulary_deck(
    words: List[Dict[str, str]],
    deck_name: str,
    language: str = "en",
    output_dir: str = "anki_decks"
) -> str:
    """
    Quick function to create vocabulary deck
    
    Args:
        words: List of dicts with keys: word, translation, example
        deck_name: Name of deck
        language: Language code
        output_dir: Where to save .apkg
        
    Returns:
        Path to .apkg file
    """
    generator = AnkiGenerator(output_dir)
    
    cards = []
    for word_data in words:
        card = AnkiCard(
            front=word_data["word"],
            back=word_data["translation"],
            example=word_data.get("example", ""),
            tags=[language, "business", "vocabulary"]
        )
        cards.append(card)
    
    return generator.create_deck(deck_name, cards, "vocabulary")


def sync_to_anki(
    cards: List[AnkiCard],
    deck_name: str
) -> bool:
    """
    Quick function to sync cards to Anki via AnkiConnect
    
    Returns:
        True if successful
    """
    try:
        connector = AnkiConnect()
        if not connector.check_connection():
            return False
        
        connector.add_cards_bulk(deck_name, cards)
        connector.sync()
        return True
    except Exception as e:
        print(f"Sync failed: {e}")
        return False
