#!/usr/bin/env python3
"""
Free Voice Virtual Assistant using Ollama (local AI) and system TTS
No API costs - runs completely locally!
"""

import os
import sys
import speech_recognition as sr
import subprocess
import requests
from jarvis_voice import JarvisVoice

# Conversation history
conversation_history = []

# Configuration
USE_JARVIS = True  # Set to False to use macOS system voice

# Initialize Jarvis voice
jarvis_tts = None
if USE_JARVIS:
    try:
        print("Initializing Jarvis voice...")
        jarvis_tts = JarvisVoice()
    except Exception as e:
        print(f"⚠️  Could not initialize Jarvis: {e}")
        print("Using macOS system voice instead.")


def check_ollama_installed():
    """Check if Ollama is installed and running"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False


def listen_to_microphone():
    """
    Capture audio from microphone and convert to text using Google Speech Recognition
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
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
    Get response from Ollama (local AI model)
    """
    try:
        # Build a concise prompt
        system_prompt = "You are a helpful voice assistant. Keep responses very brief (1-2 sentences max). Be friendly and direct."
        full_prompt = f"{system_prompt}\n\nUser: {user_input}\nAssistant:"
        
        # Call Ollama API with generate endpoint
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",  # Faster, newer model
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100,  # Limit response length
                    "top_p": 0.9
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result.get("response", "").strip()
            
            if not assistant_message:
                return "I'm thinking... try asking again."
                
            # Keep only first 2 sentences for brevity
            sentences = assistant_message.split('. ')
            if len(sentences) > 2:
                assistant_message = '. '.join(sentences[:2]) + '.'
            
            # Remove any "User:" or "Assistant:" labels from response
            assistant_message = assistant_message.replace("User:", "").replace("Assistant:", "").strip()
            
            conversation_history.append({"user": user_input, "assistant": assistant_message})
            return assistant_message
        else:
            print(f"API returned status code: {response.status_code}")
            return "Let me think about that differently. Can you rephrase?"
            
    except requests.exceptions.Timeout:
        return "Sorry, I'm thinking too slowly. Try again."
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "I encountered an error. Try asking something else."


def speak_with_system_tts(text):
    """
    Convert text to speech using Jarvis or macOS built-in voice
    """
    try:
        print(f"Assistant: {text}")
        
        # Use Jarvis voice if available
        if USE_JARVIS and jarvis_tts:
            jarvis_tts.speak(text)
        else:
            # Fallback: Use macOS 'say' command
            subprocess.run(["say", "-v", "Daniel", text], check=True)
    except Exception as e:
        print(f"Error with text-to-speech: {e}")


def main():
    """
    Main loop for the voice assistant
    """
    print("=== FREE Voice Virtual Assistant ===")
    print("Using: Ollama (local AI) + macOS TTS (free!)\n")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("⚠️  Ollama is not installed or not running!")
        print("\nTo install Ollama:")
        print("1. Visit: https://ollama.ai")
        print("2. Download and install")
        print("3. Run: ollama pull llama2")
        print("4. Ollama will run automatically\n")
        sys.exit(1)
    
    print("Commands:")
    print("- Say 'exit' or 'quit' to stop")
    print("- Press Ctrl+C to exit\n")
    
    try:
        while True:
            # Listen for user input
            user_input = listen_to_microphone()
            
            if user_input is None:
                continue
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "goodbye", "stop"]:
                speak_with_system_tts("Goodbye! Have a great day!")
                break
            
            # Get AI response
            ai_response = get_ai_response(user_input)
            
            # Speak the response
            speak_with_system_tts(ai_response)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
        speak_with_system_tts("Goodbye!")


if __name__ == "__main__":
    main()
