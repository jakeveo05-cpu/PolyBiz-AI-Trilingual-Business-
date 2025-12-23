"""
Pronunciation Coach Agent - Đánh giá phát âm
"""
import os
from .base import BaseAgent

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class PronunciationCoach(BaseAgent):
    """AI agent for pronunciation assessment and feedback"""
    
    def __init__(self):
        super().__init__()
        self.azure_key = os.getenv("AZURE_SPEECH_KEY")
        self.azure_region = os.getenv("AZURE_SPEECH_REGION", "eastasia")
    
    def get_system_prompt(self) -> str:
        return """You are a pronunciation coach for business language learners.

When given pronunciation assessment results, provide:
1. Overall score interpretation
2. Specific sounds that need work
3. Practice tips for improvement
4. Encouragement

Focus on sounds that matter for business communication clarity.
Be specific about mouth position and tongue placement when helpful."""
    
    async def assess_pronunciation(
        self, 
        audio_path: str, 
        reference_text: str,
        language: str = "en-US"
    ) -> dict:
        """Assess pronunciation using Azure Speech API"""
        if not AZURE_AVAILABLE or not self.azure_key:
            return {
                "error": "Azure Speech not configured",
                "tip": "Set AZURE_SPEECH_KEY and install azure-cognitiveservices-speech"
            }
        
        speech_config = speechsdk.SpeechConfig(
            subscription=self.azure_key,
            region=self.azure_region
        )
        
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=reference_text,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme
        )
        
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            language=language,
            audio_config=audio_config
        )
        
        pronunciation_config.apply_to(recognizer)
        result = recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
            return {
                "accuracy_score": pronunciation_result.accuracy_score,
                "fluency_score": pronunciation_result.fluency_score,
                "completeness_score": pronunciation_result.completeness_score,
                "pronunciation_score": pronunciation_result.pronunciation_score,
                "recognized_text": result.text,
                "reference_text": reference_text
            }
        else:
            return {"error": f"Speech recognition failed: {result.reason}"}
    
    async def get_feedback(self, assessment_result: dict) -> str:
        """Generate human-friendly feedback from assessment results"""
        if "error" in assessment_result:
            return f"Could not assess pronunciation: {assessment_result['error']}"
        
        prompt = f"""Pronunciation Assessment Results:
- Accuracy: {assessment_result.get('accuracy_score', 'N/A')}%
- Fluency: {assessment_result.get('fluency_score', 'N/A')}%
- Completeness: {assessment_result.get('completeness_score', 'N/A')}%
- Overall: {assessment_result.get('pronunciation_score', 'N/A')}%

Reference text: {assessment_result.get('reference_text', '')}
Recognized as: {assessment_result.get('recognized_text', '')}

Please provide helpful feedback for the learner."""
        
        return await self.chat(prompt)
