#!/usr/bin/env python3
"""
Enhanced FREE Voice Virtual Assistant
- Multiple voice options
- Conversation history
- Better error handling
- Configurable settings
"""

import os
import sys
import json
import speech_recognition as sr
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from jarvis_voice import JarvisVoice

# Configuration
CONFIG = {
    "voice": "Jarvis",  # Options: Jarvis, Samantha, Alex, Daniel, Karen, Moira, etc.
    "speech_rate": 200,   # Words per minute (default 200, range 90-720)
    "model": "qwen2.5:1.5b",    # Smaller, faster model for low-end Macs
    "save_history": True,
    "history_file": "conversation_history.json",
    "use_jarvis": True  # Use Jarvis voice (Coqui TTS)
}

# Conversation history
conversation_history = []


def check_ollama_installed():
    """Check if Ollama is installed and running"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False


def load_conversation_history():
    """Load previous conversation history"""
    history_path = Path(CONFIG["history_file"])
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_conversation_history():
    """Save conversation history to file"""
    if CONFIG["save_history"]:
        try:
            with open(CONFIG["history_file"], 'w') as f:
                json.dump(conversation_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")


def list_available_voices():
    """List all available macOS voices"""
    try:
        result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
        print("\n=== Available Voices ===")
        voices = []
        for line in result.stdout.split('\n')[:30]:  # Show first 30
            if line.strip():
                voice_name = line.split()[0]
                voices.append(voice_name)
                print(f"  - {voice_name}")
        return voices
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []


def test_voice(voice_name):
    """Test a specific voice"""
    try:
        subprocess.run(["say", "-v", voice_name, f"Hello! My name is {voice_name}"], check=True)
    except Exception as e:
        print(f"Error testing voice: {e}")


def listen_to_microphone():
    """
    Capture audio from microphone and convert to text using Google Speech Recognition
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    recognizer.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("\n🎤 Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("⏳ Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"💬 You: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⏱️  No speech detected.")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None


def get_ai_response(user_input):
    """
    Get response from Ollama (local AI model)
    """
    try:
        # Build context from recent history
        context = ""
        if len(conversation_history) > 0:
            recent = conversation_history[-6:]  # Last 3 exchanges
            for entry in recent:
                context += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
        
        # Build prompt
        system_prompt = "You are a helpful, friendly voice assistant. Keep responses brief (1-2 sentences) and conversational."
        full_prompt = f"{system_prompt}\n\n{context}User: {user_input}\nAssistant:"
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": CONFIG["model"],
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100,
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
            
            # Clean up response
            sentences = assistant_message.split('. ')
            if len(sentences) > 2:
                assistant_message = '. '.join(sentences[:2]) + '.'
            
            assistant_message = assistant_message.replace("User:", "").replace("Assistant:", "").strip()
            
            # Save to history
            conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": assistant_message
            })
            save_conversation_history()
            
            return assistant_message
        else:
            print(f"⚠️  API returned status code: {response.status_code}")
            return "Let me think about that differently. Can you rephrase?"
            
    except requests.exceptions.Timeout:
        return "Sorry, I'm thinking too slowly. Try again."
    except Exception as e:
        print(f"❌ Error getting AI response: {e}")
        return "I encountered an error. Try asking something else."


# Initialize Jarvis voice if enabled
jarvis_tts = None
if CONFIG.get("use_jarvis", False):
    try:
        jarvis_tts = JarvisVoice()
    except Exception as e:
        print(f"⚠️  Could not initialize Jarvis voice: {e}")

def speak_with_tts(text):
    """
    Convert text to speech using Jarvis or macOS system voice
    """
    try:
        print(f"🤖 Assistant: {text}")
        
        # Use Jarvis voice if enabled and available
        if CONFIG.get("use_jarvis", False) and jarvis_tts:
            jarvis_tts.speak(text)
        else:
            # Fallback to macOS system voice
            subprocess.run([
                "say", 
                "-v", CONFIG.get("voice", "Samantha"),
                "-r", str(CONFIG["speech_rate"]),
                text
            ], check=True)
    except Exception as e:
        print(f"❌ Error with text-to-speech: {e}")


def show_menu():
    """Show interactive menu"""
    print("\n" + "="*50)
    print("🎤 VOICE ASSISTANT - Enhanced Edition")
    print("="*50)
    print("\nCommands:")
    print("  • Speak naturally to chat")
    print("  • Say 'change voice' to pick a different voice")
    print("  • Say 'test voice' to hear current voice")
    print("  • Say 'show history' to see conversation")
    print("  • Say 'clear history' to reset")
    print("  • Say 'settings' to see configuration")
    print("  • Say 'exit' or 'quit' to stop")
    print("  • Press Ctrl+C to force exit")
    print(f"\nCurrent Voice: {CONFIG['voice']}")
    print(f"AI Model: {CONFIG['model']}")
    print("="*50 + "\n")


def show_settings():
    """Display current settings"""
    print("\n=== Current Settings ===")
    for key, value in CONFIG.items():
        print(f"  {key}: {value}")
    print()


def show_history():
    """Display conversation history"""
    if not conversation_history:
        print("\n📝 No conversation history yet.\n")
        return
    
    print("\n=== Conversation History ===")
    for i, entry in enumerate(conversation_history[-10:], 1):  # Last 10
        print(f"\n[{i}] {entry.get('timestamp', 'Unknown time')}")
        print(f"You: {entry['user']}")
        print(f"AI: {entry['assistant']}")
    print()


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    try:
        if Path(CONFIG["history_file"]).exists():
            os.remove(CONFIG["history_file"])
        print("✅ History cleared!")
    except Exception as e:
        print(f"⚠️  Could not clear history file: {e}")


def change_voice():
    """Interactive voice changing"""
    voices = list_available_voices()
    print("\nType a voice name to test it (or 'cancel' to keep current):")
    
    choice = input(f"Voice [{CONFIG['voice']}]: ").strip()
    
    if choice.lower() == 'cancel' or not choice:
        return
    
    if choice in voices or True:  # Allow any voice name
        CONFIG["voice"] = choice
        print(f"\n✅ Voice changed to: {choice}")
        test_voice(choice)
    else:
        print("⚠️  Voice not found, keeping current.")


def main():
    """
    Main loop for the voice assistant
    """
    # Check Ollama
    if not check_ollama_installed():
        print("⚠️  Ollama is not installed or not running!")
        print("\nTo start Ollama:")
        print("  brew services start ollama")
        print("  ollama pull llama2\n")
        sys.exit(1)
    
    # Load previous history
    global conversation_history
    conversation_history = load_conversation_history()
    if conversation_history:
        print(f"📚 Loaded {len(conversation_history)} previous messages")
    
    show_menu()
    
    try:
        while True:
            # Listen for user input
            user_input = listen_to_microphone()
            
            if user_input is None:
                continue
            
            user_lower = user_input.lower()
            
            # Check for commands
            if user_lower in ["exit", "quit", "goodbye", "stop"]:
                speak_with_tts("Goodbye! Have a great day!")
                break
            
            elif "change voice" in user_lower:
                change_voice()
                continue
            
            elif "test voice" in user_lower:
                test_voice(CONFIG["voice"])
                continue
            
            elif "show history" in user_lower:
                show_history()
                continue
            
            elif "clear history" in user_lower:
                clear_history()
                speak_with_tts("History cleared!")
                continue
            
            elif "settings" in user_lower:
                show_settings()
                continue
            
            # Get AI response
            ai_response = get_ai_response(user_input)
            
            # Speak the response
            speak_with_tts(ai_response)
            
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        speak_with_tts("Goodbye!")
    finally:
        save_conversation_history()


if __name__ == "__main__":
    main()
