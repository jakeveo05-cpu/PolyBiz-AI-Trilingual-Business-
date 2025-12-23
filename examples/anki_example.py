"""
Example: How to use Anki integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents import AnkiGenerator, AnkiConnect, AnkiCard, create_vocabulary_deck


# Example 1: Create standalone .apkg file (no Anki needed)
def example_create_deck():
    """Create a vocabulary deck as .apkg file"""
    
    # Prepare vocabulary
    words = [
        {
            "word": "leverage",
            "translation": "tận dụng, khai thác",
            "example": "We need to leverage our existing customer base."
        },
        {
            "word": "synergy",
            "translation": "sự cộng hưởng, hiệu ứng tổng hợp",
            "example": "The merger will create synergy between the two companies."
        },
        {
            "word": "stakeholder",
            "translation": "bên liên quan, người có quyền lợi",
            "example": "We need to consider all stakeholders in this decision."
        }
    ]
    
    # Create deck
    deck_path = create_vocabulary_deck(
        words=words,
        deck_name="Business English - Week 1",
        language="en"
    )
    
    print(f"✅ Deck created: {deck_path}")
    print("📥 Download and import into Anki!")
    
    return deck_path


# Example 2: Advanced deck with custom cards
def example_advanced_deck():
    """Create deck with audio and custom fields"""
    
    generator = AnkiGenerator()
    
    cards = [
        AnkiCard(
            front="How do you say 'Let's schedule a meeting' professionally?",
            back="I'd like to schedule a meeting at your earliest convenience.",
            example="Context: Following up after initial contact",
            tags=["business", "meetings", "phrases"],
            extra_fields={"notes": "More formal than 'Let's meet'"}
        ),
        AnkiCard(
            front="What's a polite way to disagree in a meeting?",
            back="I see your point, however, I'd like to offer a different perspective.",
            example="Context: Team discussion",
            tags=["business", "meetings", "soft-skills"]
        )
    ]
    
    deck_path = generator.create_deck(
        deck_name="Business Communication Phrases",
        cards=cards,
        template_name="phrases",
        description="Essential phrases for business meetings"
    )
    
    print(f"✅ Advanced deck created: {deck_path}")
    return deck_path


# Example 3: Sync directly to Anki (requires AnkiConnect)
def example_sync_to_anki():
    """Sync cards directly to Anki desktop"""
    
    try:
        connector = AnkiConnect()
        
        # Check connection
        if not connector.check_connection():
            print("❌ Cannot connect to Anki")
            print("Make sure:")
            print("1. Anki is running")
            print("2. AnkiConnect addon is installed")
            return False
        
        print("✅ Connected to Anki!")
        
        # Create cards
        cards = [
            AnkiCard(
                front="ROI",
                back="Return on Investment - Lợi nhuận trên vốn đầu tư",
                example="What's the ROI on this marketing campaign?",
                tags=["business", "acronyms", "finance"]
            ),
            AnkiCard(
                front="KPI",
                back="Key Performance Indicator - Chỉ số đo lường hiệu suất chính",
                example="We need to track our KPIs monthly.",
                tags=["business", "acronyms", "management"]
            )
        ]
        
        # Sync to Anki
        note_ids = connector.add_cards_bulk(
            deck_name="PolyBiz AI - Business Acronyms",
            cards=cards
        )
        
        print(f"✅ Added {len(note_ids)} cards to Anki!")
        
        # Trigger sync
        connector.sync()
        print("✅ Synced with AnkiWeb!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# Example 4: Get existing decks
def example_list_decks():
    """List all decks in Anki"""
    
    try:
        connector = AnkiConnect()
        decks = connector.get_deck_names()
        
        print("📚 Your Anki Decks:")
        for deck in decks:
            print(f"  - {deck}")
        
        return decks
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("PolyBiz AI - Anki Integration Examples")
    print("=" * 60)
    
    print("\n1️⃣ Creating standalone .apkg deck...")
    example_create_deck()
    
    print("\n2️⃣ Creating advanced deck with custom template...")
    example_advanced_deck()
    
    print("\n3️⃣ Syncing to Anki (requires AnkiConnect)...")
    example_sync_to_anki()
    
    print("\n4️⃣ Listing existing decks...")
    example_list_decks()
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)
