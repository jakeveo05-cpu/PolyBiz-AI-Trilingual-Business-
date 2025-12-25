"""
PolyBiz Anki Sync - Import/Export flashcards with Anki
Supports: AnkiConnect API (local), File export (.txt, .csv, .apkg)
"""

import json
import csv
import os
import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class Flashcard:
    """Flashcard data structure"""
    front: str              # Chinese character/word
    back: str               # Pinyin + meaning
    pinyin: str = ""
    meaning: str = ""
    example: str = ""
    audio: str = ""         # Audio file path or TTS text
    image: str = ""         # Image path
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        
        # Auto-generate back if not provided
        if not self.back and (self.pinyin or self.meaning):
            parts = []
            if self.pinyin:
                parts.append(self.pinyin)
            if self.meaning:
                parts.append(self.meaning)
            self.back = " | ".join(parts)


class AnkiConnect:
    """
    AnkiConnect API client
    Requires Anki desktop app with AnkiConnect add-on installed
    Add-on code: 2055492159
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.url = f"http://{host}:{port}"
        self.version = 6
    
    async def _request(self, action: str, params: Dict = None) -> Any:
        """Send request to AnkiConnect"""
        payload = {
            "action": action,
            "version": self.version
        }
        if params:
            payload["params"] = params
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.url, json=payload)
            result = response.json()
            
            if result.get("error"):
                raise Exception(f"AnkiConnect error: {result['error']}")
            
            return result.get("result")
    
    async def is_available(self) -> bool:
        """Check if AnkiConnect is running"""
        try:
            version = await self._request("version")
            return version is not None
        except:
            return False
    
    async def get_decks(self) -> List[str]:
        """Get list of all decks"""
        return await self._request("deckNames")
    
    async def create_deck(self, name: str) -> int:
        """Create a new deck"""
        return await self._request("createDeck", {"deck": name})
    
    async def get_note_types(self) -> List[str]:
        """Get list of note types (models)"""
        return await self._request("modelNames")
    
    async def add_note(
        self,
        deck: str,
        front: str,
        back: str,
        tags: List[str] = None,
        model: str = "Basic",
        allow_duplicate: bool = False
    ) -> int:
        """Add a single note to Anki"""
        note = {
            "deckName": deck,
            "modelName": model,
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": tags or [],
            "options": {
                "allowDuplicate": allow_duplicate
            }
        }
        
        return await self._request("addNote", {"note": note})
    
    async def add_notes(
        self,
        deck: str,
        cards: List[Flashcard],
        model: str = "Basic"
    ) -> List[int]:
        """Add multiple notes to Anki"""
        notes = []
        for card in cards:
            notes.append({
                "deckName": deck,
                "modelName": model,
                "fields": {
                    "Front": card.front,
                    "Back": card.back
                },
                "tags": card.tags or ["polybiz"],
                "options": {
                    "allowDuplicate": False
                }
            })
        
        return await self._request("addNotes", {"notes": notes})
    
    async def find_notes(self, query: str) -> List[int]:
        """Find notes by query"""
        return await self._request("findNotes", {"query": query})
    
    async def get_notes_info(self, note_ids: List[int]) -> List[Dict]:
        """Get detailed info for notes"""
        return await self._request("notesInfo", {"notes": note_ids})
    
    async def sync(self):
        """Trigger Anki sync"""
        return await self._request("sync")


class AnkiFileExporter:
    """Export flashcards to various file formats"""
    
    @staticmethod
    def to_txt(cards: List[Flashcard], filepath: str, separator: str = "\t"):
        """
        Export to plain text (Anki import format)
        Format: front<tab>back<tab>tags
        """
        with open(filepath, "w", encoding="utf-8") as f:
            for card in cards:
                tags = " ".join(card.tags) if card.tags else ""
                line = f"{card.front}{separator}{card.back}"
                if tags:
                    line += f"{separator}{tags}"
                f.write(line + "\n")
        
        return filepath
    
    @staticmethod
    def to_csv(cards: List[Flashcard], filepath: str):
        """Export to CSV with all fields"""
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "front", "back", "pinyin", "meaning", "example", "tags"
            ])
            writer.writeheader()
            
            for card in cards:
                writer.writerow({
                    "front": card.front,
                    "back": card.back,
                    "pinyin": card.pinyin,
                    "meaning": card.meaning,
                    "example": card.example,
                    "tags": ";".join(card.tags) if card.tags else ""
                })
        
        return filepath
    
    @staticmethod
    def to_json(cards: List[Flashcard], filepath: str):
        """Export to JSON"""
        data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "source": "PolyBiz AI",
            "cards": [asdict(card) for card in cards]
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath


class AnkiFileImporter:
    """Import flashcards from various file formats"""
    
    @staticmethod
    def from_txt(filepath: str, separator: str = "\t") -> List[Flashcard]:
        """
        Import from plain text
        Expected format: front<tab>back or front<tab>back<tab>tags
        """
        cards = []
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split(separator)
                if len(parts) >= 2:
                    front = parts[0].strip()
                    back = parts[1].strip()
                    tags = parts[2].split() if len(parts) > 2 else []
                    
                    # Try to parse pinyin and meaning from back
                    pinyin, meaning = "", ""
                    if "|" in back:
                        p = back.split("|")
                        pinyin = p[0].strip()
                        meaning = p[1].strip() if len(p) > 1 else ""
                    
                    cards.append(Flashcard(
                        front=front,
                        back=back,
                        pinyin=pinyin,
                        meaning=meaning,
                        tags=tags
                    ))
        
        return cards
    
    @staticmethod
    def from_csv(filepath: str) -> List[Flashcard]:
        """Import from CSV"""
        cards = []
        
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Handle different column name variations
                front = row.get("front") or row.get("Front") or row.get("汉字") or row.get("word") or ""
                back = row.get("back") or row.get("Back") or ""
                pinyin = row.get("pinyin") or row.get("Pinyin") or row.get("拼音") or ""
                meaning = row.get("meaning") or row.get("Meaning") or row.get("意思") or row.get("definition") or ""
                example = row.get("example") or row.get("Example") or row.get("例句") or ""
                tags_str = row.get("tags") or row.get("Tags") or ""
                
                if front:
                    tags = [t.strip() for t in tags_str.split(";") if t.strip()]
                    
                    cards.append(Flashcard(
                        front=front,
                        back=back or f"{pinyin} | {meaning}",
                        pinyin=pinyin,
                        meaning=meaning,
                        example=example,
                        tags=tags
                    ))
        
        return cards
    
    @staticmethod
    def from_json(filepath: str) -> List[Flashcard]:
        """Import from JSON"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cards = []
        card_list = data.get("cards", data) if isinstance(data, dict) else data
        
        for item in card_list:
            if isinstance(item, dict):
                cards.append(Flashcard(
                    front=item.get("front", ""),
                    back=item.get("back", ""),
                    pinyin=item.get("pinyin", ""),
                    meaning=item.get("meaning", ""),
                    example=item.get("example", ""),
                    tags=item.get("tags", [])
                ))
        
        return cards
    
    @staticmethod
    def from_anki_export(filepath: str) -> List[Flashcard]:
        """
        Import from Anki text export
        Anki exports as: "front"<tab>"back" with HTML
        """
        cards = []
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Remove HTML tags
                import re
                line = re.sub(r'<[^>]+>', '', line)
                
                parts = line.split("\t")
                if len(parts) >= 2:
                    front = parts[0].strip().strip('"')
                    back = parts[1].strip().strip('"')
                    
                    cards.append(Flashcard(front=front, back=back))
        
        return cards


class AnkiSync:
    """
    Main Anki Sync class - unified interface for import/export
    
    Usage:
        sync = AnkiSync()
        
        # Check if Anki is running
        if await sync.is_anki_available():
            # Export to Anki directly
            await sync.export_to_anki(cards, deck="Chinese")
            
            # Import from Anki
            cards = await sync.import_from_anki(deck="Chinese")
        
        # File-based export/import (no Anki needed)
        sync.export_to_file(cards, "vocab.txt")
        cards = sync.import_from_file("vocab.csv")
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.anki = AnkiConnect(
            host=self.config.get("host", "localhost"),
            port=self.config.get("port", 8765)
        )
        self.exporter = AnkiFileExporter()
        self.importer = AnkiFileImporter()
        
        self.default_deck = self.config.get("deck_name", "PolyBiz Chinese")
        self.default_model = self.config.get("note_type", "Basic")
    
    async def is_anki_available(self) -> bool:
        """Check if Anki with AnkiConnect is running"""
        return await self.anki.is_available()
    
    # ============ EXPORT ============
    
    async def export_to_anki(
        self,
        cards: List[Flashcard],
        deck: str = None,
        model: str = None
    ) -> Dict[str, Any]:
        """Export cards directly to Anki via AnkiConnect"""
        deck = deck or self.default_deck
        model = model or self.default_model
        
        # Ensure deck exists
        await self.anki.create_deck(deck)
        
        # Add notes
        result_ids = await self.anki.add_notes(deck, cards, model)
        
        # Count successes
        added = sum(1 for id in result_ids if id is not None)
        failed = len(result_ids) - added
        
        return {
            "success": True,
            "deck": deck,
            "added": added,
            "failed": failed,
            "note_ids": [id for id in result_ids if id is not None]
        }
    
    def export_to_file(
        self,
        cards: List[Flashcard],
        filepath: str,
        format: str = None
    ) -> str:
        """
        Export cards to file
        
        Args:
            cards: List of Flashcard objects
            filepath: Output file path
            format: 'txt', 'csv', or 'json' (auto-detected from extension if not provided)
        """
        if not format:
            ext = Path(filepath).suffix.lower()
            format = ext[1:] if ext else "txt"
        
        if format == "txt":
            return self.exporter.to_txt(cards, filepath)
        elif format == "csv":
            return self.exporter.to_csv(cards, filepath)
        elif format == "json":
            return self.exporter.to_json(cards, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    # ============ IMPORT ============
    
    async def import_from_anki(
        self,
        deck: str = None,
        query: str = None,
        limit: int = None
    ) -> List[Flashcard]:
        """Import cards from Anki via AnkiConnect"""
        if query:
            search = query
        elif deck:
            search = f"deck:{deck}"
        else:
            search = f"deck:{self.default_deck}"
        
        # Find notes
        note_ids = await self.anki.find_notes(search)
        
        if limit:
            note_ids = note_ids[:limit]
        
        if not note_ids:
            return []
        
        # Get note details
        notes_info = await self.anki.get_notes_info(note_ids)
        
        cards = []
        for note in notes_info:
            fields = note.get("fields", {})
            front = fields.get("Front", {}).get("value", "")
            back = fields.get("Back", {}).get("value", "")
            tags = note.get("tags", [])
            
            # Clean HTML
            import re
            front = re.sub(r'<[^>]+>', '', front)
            back = re.sub(r'<[^>]+>', '', back)
            
            cards.append(Flashcard(
                front=front,
                back=back,
                tags=tags
            ))
        
        return cards
    
    def import_from_file(self, filepath: str, format: str = None) -> List[Flashcard]:
        """
        Import cards from file
        
        Args:
            filepath: Input file path
            format: 'txt', 'csv', 'json', or 'anki' (auto-detected if not provided)
        """
        if not format:
            ext = Path(filepath).suffix.lower()
            format = ext[1:] if ext else "txt"
        
        if format == "txt":
            return self.importer.from_txt(filepath)
        elif format == "csv":
            return self.importer.from_csv(filepath)
        elif format == "json":
            return self.importer.from_json(filepath)
        elif format == "anki":
            return self.importer.from_anki_export(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    # ============ SYNC ============
    
    async def sync_anki(self):
        """Trigger Anki cloud sync"""
        return await self.anki.sync()
    
    async def get_decks(self) -> List[str]:
        """Get list of Anki decks"""
        return await self.anki.get_decks()


# ============ SAMPLE DATA ============

def get_sample_cards() -> List[Flashcard]:
    """Get sample flashcards for testing"""
    return [
        Flashcard(
            front="好",
            pinyin="hǎo",
            meaning="Tốt, Thích",
            example="你好 (nǐ hǎo) - Xin chào",
            tags=["HSK1", "greeting"]
        ),
        Flashcard(
            front="你",
            pinyin="nǐ",
            meaning="Bạn",
            example="你好吗？(nǐ hǎo ma?) - Bạn khỏe không?",
            tags=["HSK1", "pronoun"]
        ),
        Flashcard(
            front="我",
            pinyin="wǒ",
            meaning="Tôi",
            example="我是学生 (wǒ shì xuéshēng) - Tôi là học sinh",
            tags=["HSK1", "pronoun"]
        ),
        Flashcard(
            front="是",
            pinyin="shì",
            meaning="Là",
            example="他是老师 (tā shì lǎoshī) - Anh ấy là giáo viên",
            tags=["HSK1", "verb"]
        ),
        Flashcard(
            front="中国",
            pinyin="zhōngguó",
            meaning="Trung Quốc",
            example="我去中国 (wǒ qù zhōngguó) - Tôi đi Trung Quốc",
            tags=["HSK1", "country"]
        ),
    ]


# ============ CLI ============

async def main():
    """Test Anki Sync"""
    import asyncio
    
    print("🃏 PolyBiz Anki Sync Test\n")
    
    sync = AnkiSync()
    
    # Check Anki
    print("🔍 Checking AnkiConnect...")
    available = await sync.is_anki_available()
    print(f"   Anki available: {'✅ Yes' if available else '❌ No'}")
    
    if available:
        decks = await sync.get_decks()
        print(f"   Decks: {decks[:5]}...")
    
    # Test file export
    print("\n📤 Testing file export...")
    cards = get_sample_cards()
    
    os.makedirs("data/anki_export", exist_ok=True)
    
    txt_path = sync.export_to_file(cards, "data/anki_export/vocab.txt")
    print(f"   ✅ Exported to {txt_path}")
    
    csv_path = sync.export_to_file(cards, "data/anki_export/vocab.csv")
    print(f"   ✅ Exported to {csv_path}")
    
    json_path = sync.export_to_file(cards, "data/anki_export/vocab.json")
    print(f"   ✅ Exported to {json_path}")
    
    # Test file import
    print("\n📥 Testing file import...")
    
    imported_txt = sync.import_from_file(txt_path)
    print(f"   ✅ Imported {len(imported_txt)} cards from TXT")
    
    imported_csv = sync.import_from_file(csv_path)
    print(f"   ✅ Imported {len(imported_csv)} cards from CSV")
    
    imported_json = sync.import_from_file(json_path)
    print(f"   ✅ Imported {len(imported_json)} cards from JSON")
    
    # Test Anki export if available
    if available:
        print("\n📤 Testing Anki export...")
        result = await sync.export_to_anki(cards[:2], deck="PolyBiz Test")
        print(f"   ✅ Added {result['added']} cards to Anki")
    
    print("\n✨ Done!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
