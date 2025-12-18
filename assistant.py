#!/usr/bin/env python3
"""
Voice Virtual Assistant using ElevenLabs and OpenAI
"""

import os
import sys
import speech_recognition as sr
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize API keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

if not ELEVENLABS_API_KEY or not OPENAI_API_KEY:
    print("Error: Missing API keys. Please set them in .env file.")
    sys.exit(1)

eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise and conversational."}
]


def listen_to_microphone():
    """
    Capture audio from microphone and convert to text using Google Speech Recognition
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000  # Adjust based on ambient noise
    recognizer.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("No speech detected. Speak louder or closer to the microphone.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio. Try speaking more clearly.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None


def get_ai_response(user_input):
    """
    Get response from OpenAI GPT model
    """
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            max_tokens=150,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "I'm sorry, I encountered an error processing your request."


def speak_with_elevenlabs(text):
    """
    Convert text to speech using ElevenLabs and play it
    """
    try:
        print(f"Assistant: {text}")
        audio = eleven_client.generate(
            text=text,
            voice=ELEVENLABS_VOICE_ID,
            model="eleven_monolingual_v1"
        )
        # Convert generator to bytes
        audio_bytes = b''.join(audio)
        # Play using a simple method
        import io
        from pydub import AudioSegment
        from pydub.playback import play
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        play(audio_segment)
    except Exception as e:
        print(f"Error with text-to-speech: {e}")


def list_available_voices():
    """
    List all available ElevenLabs voices
    """
    try:
        all_voices = eleven_client.voices.get_all()
        print("\nAvailable voices:")
        for voice in all_voices.voices:
            print(f"- {voice.name}: {voice.voice_id}")
    except Exception as e:
        print(f"Error listing voices: {e}")


def main():
    """
    Main loop for the voice assistant
    """
    print("=== Voice Virtual Assistant ===")
    print("Commands:")
    print("- Say 'exit' or 'quit' to stop")
    print("- Say 'list voices' to see available voices")
    print("- Press Ctrl+C to exit\n")
    
    try:
        while True:
            # Listen for user input
            user_input = listen_to_microphone()
            
            if user_input is None:
                continue
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "goodbye", "stop"]:
                speak_with_elevenlabs("Goodbye! Have a great day!")
                break
            
            # Check for list voices command
            if "list voices" in user_input.lower():
                list_available_voices()
                continue
            
            # Get AI response
            ai_response = get_ai_response(user_input)
            
            # Speak the response
            speak_with_elevenlabs(ai_response)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
        speak_with_elevenlabs("Goodbye!")


if __name__ == "__main__":
    main()
