#!/usr/bin/env python3
"""
Jarvis-style Text-to-Speech using Coqui TTS
Provides a sophisticated British AI assistant voice
"""

import subprocess
import os
from pathlib import Path

# Try Coqui TTS (better quality)
try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("⚠️  Coqui TTS not installed. Using macOS system voice.")


class JarvisVoice:
    """Jarvis-style voice synthesis"""
    
    def __init__(self, use_coqui=True):
        self.use_coqui = use_coqui and HAS_TTS
        self.tts = None
        
        if self.use_coqui:
            try:
                # Use VCTK model - has multiple British voices
                print("🎙️  Loading Jarvis voice model...")
                self.tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
                # Speaker p326 is a good British male voice
                self.speaker = "p227"  
                print("✅ Jarvis voice ready!")
            except Exception as e:
                print(f"⚠️  Could not load Coqui TTS: {e}")
                print("Falling back to macOS Daniel voice...")
                self.use_coqui = False
    
    def speak(self, text):
        """Speak text using Jarvis voice"""
        if self.use_coqui and self.tts:
            try:
                # Generate speech with Coqui TTS
                temp_file = "/tmp/jarvis_speech.wav"
                self.tts.tts_to_file(
                    text=text,
                    speaker=self.speaker,
                    file_path=temp_file
                )
                # Play the audio
                subprocess.run(["afplay", temp_file], check=True)
                # Clean up
                os.remove(temp_file)
            except Exception as e:
                print(f"❌ TTS error: {e}")
                # Fallback to system voice
                self._speak_system(text)
        else:
            self._speak_system(text)
    
    def _speak_system(self, text):
        """Fallback: Use macOS Daniel voice (British)"""
        try:
            # Daniel is the closest to Jarvis - British male
            subprocess.run([
                "say", 
                "-v", "Daniel",
                "-r", "190",  # Slightly slower for sophistication
                text
            ], check=True)
        except Exception as e:
            print(f"❌ System TTS error: {e}")


# Quick test
if __name__ == "__main__":
    jarvis = JarvisVoice()
    print("\n🤖 Testing Jarvis voice...\n")
    
    test_phrases = [
        "Good evening, Sir. All systems operational.",
        "I have completed the analysis you requested.",
        "Shall I activate the protocol?",
        "At your service, as always."
    ]
    
    for phrase in test_phrases:
        print(f"Speaking: {phrase}")
        jarvis.speak(phrase)
        print()
