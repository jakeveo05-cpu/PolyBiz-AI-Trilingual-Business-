"""
Toucan TTS Integration - Text-to-Speech for 7000+ languages
https://github.com/DigitalPhonetics/IMS-Toucan
"""
import os
import tempfile
from pathlib import Path

# Toucan TTS will be imported dynamically to avoid import errors if not installed
TOUCAN_AVAILABLE = False

try:
    # These imports will work after Toucan is installed
    from InferenceInterfaces.ToucanTTSInterface import ToucanTTSInterface
    TOUCAN_AVAILABLE = True
except ImportError:
    pass


class ToucanTTS:
    """
    Wrapper for IMS Toucan TTS - Multilingual Text-to-Speech
    
    Supports 7000+ languages including Vietnamese, English, Chinese
    Free and self-hosted alternative to ElevenLabs
    """
    
    # Language codes mapping (ISO 639-3)
    LANGUAGE_CODES = {
        "en": "eng",  # English
        "zh": "cmn",  # Mandarin Chinese
        "vi": "vie",  # Vietnamese
        "ja": "jpn",  # Japanese
        "ko": "kor",  # Korean
        "fr": "fra",  # French
        "de": "deu",  # German
        "es": "spa",  # Spanish
    }
    
    def __init__(self, device: str = "cpu"):
        """
        Initialize Toucan TTS
        
        Args:
            device: "cpu" or "cuda" for GPU acceleration
        """
        self.device = device
        self.model = None
        self.current_language = None
        
        if not TOUCAN_AVAILABLE:
            print("⚠️ Toucan TTS not installed. Run: pip install -e IMS-Toucan")
    
    def _ensure_model_loaded(self):
        """Lazy load the model"""
        if self.model is None and TOUCAN_AVAILABLE:
            self.model = ToucanTTSInterface(device=self.device)
    
    def set_language(self, language: str):
        """
        Set the language for TTS
        
        Args:
            language: Language code (en, zh, vi, etc.)
        """
        self._ensure_model_loaded()
        
        lang_code = self.LANGUAGE_CODES.get(language, language)
        
        if self.model:
            self.model.set_language(lang_code)
            self.current_language = language
    
    def synthesize(
        self, 
        text: str, 
        output_path: str = None,
        language: str = None,
        duration_scaling: float = 1.0,
        pitch_variance: float = 1.0,
        energy_variance: float = 1.0
    ) -> str:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file (optional)
            language: Language code (optional, uses current if not set)
            duration_scaling: Speed control (< 1.0 = faster, > 1.0 = slower)
            pitch_variance: Pitch variation control
            energy_variance: Energy/volume variation control
            
        Returns:
            Path to the generated audio file
        """
        if not TOUCAN_AVAILABLE:
            raise RuntimeError(
                "Toucan TTS not installed. Please install it:\n"
                "git clone https://github.com/DigitalPhonetics/IMS-Toucan\n"
                "cd IMS-Toucan && pip install -e ."
            )
        
        self._ensure_model_loaded()
        
        # Set language if provided
        if language:
            self.set_language(language)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Synthesize
        self.model.read_to_file(
            text_list=[text],
            file_location=output_path,
            duration_scaling_factor=duration_scaling,
            pitch_variance_scale=pitch_variance,
            energy_variance_scale=energy_variance
        )
        
        return output_path
    
    def synthesize_dialogue(
        self,
        dialogue: list[dict],
        output_path: str,
        pause_duration: float = 0.5
    ) -> str:
        """
        Synthesize a dialogue with multiple speakers/languages
        
        Args:
            dialogue: List of {"text": str, "language": str, "speaker": str}
            output_path: Path to save combined audio
            pause_duration: Pause between utterances in seconds
            
        Returns:
            Path to the generated audio file
        """
        if not TOUCAN_AVAILABLE:
            raise RuntimeError("Toucan TTS not installed")
        
        import wave
        import struct
        
        temp_files = []
        
        # Generate each utterance
        for i, item in enumerate(dialogue):
            temp_path = tempfile.mktemp(suffix=f"_{i}.wav")
            self.synthesize(
                text=item["text"],
                output_path=temp_path,
                language=item.get("language", "en")
            )
            temp_files.append(temp_path)
        
        # Combine audio files (simple concatenation)
        # For production, use pydub or similar for better handling
        self._combine_wav_files(temp_files, output_path, pause_duration)
        
        # Cleanup temp files
        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass
        
        return output_path
    
    def _combine_wav_files(
        self, 
        input_files: list[str], 
        output_path: str,
        pause_duration: float = 0.5
    ):
        """Combine multiple WAV files into one"""
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            pause = AudioSegment.silent(duration=int(pause_duration * 1000))
            
            for f in input_files:
                audio = AudioSegment.from_wav(f)
                combined += audio + pause
            
            combined.export(output_path, format="wav")
            
        except ImportError:
            # Fallback: just use the first file
            import shutil
            if input_files:
                shutil.copy(input_files[0], output_path)


# Convenience function
def text_to_speech(
    text: str,
    language: str = "en",
    output_path: str = None,
    device: str = "cpu"
) -> str:
    """
    Quick function to convert text to speech
    
    Args:
        text: Text to synthesize
        language: Language code (en, zh, vi)
        output_path: Where to save the audio
        device: "cpu" or "cuda"
        
    Returns:
        Path to generated audio file
    """
    tts = ToucanTTS(device=device)
    return tts.synthesize(text, output_path, language)
