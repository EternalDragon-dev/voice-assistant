# Voice Virtual Assistant

A Python-based voice assistant with two implementations:
1. **Free version** - Uses Ollama (local AI) + macOS Text-to-Speech (completely free!)
2. **Premium version** - Uses ElevenLabs (realistic voices) + OpenAI GPT (paid APIs)

## Features

- 🎤 Speech recognition using Google Speech Recognition
- 🤖 AI-powered conversational responses
- 🔊 Natural-sounding voice output
- 💬 Maintains conversation context
- 🎯 Simple voice commands
- 🆓 100% free option with local AI

## Quick Start (FREE Version)

The free version runs completely locally with no API costs!

### Prerequisites

- Python 3.8 or higher
- macOS (for built-in TTS)
- Microphone and speakers/headphones
- [Ollama](https://ollama.ai) for local AI

## Installation (Free Version)

1. **Install Python dependencies:**
   ```bash
   pip3 install SpeechRecognition requests
   ```

   **Note for macOS users:** If you encounter issues installing PyAudio:
   ```bash
   brew install portaudio
   pip3 install pyaudio
   ```

2. **Install Ollama (local AI):**
   ```bash
   brew install ollama
   ```

3. **Download AI model:**
   ```bash
   ollama pull llama2
   ```

4. **Start Ollama service:**
   ```bash
   brew services start ollama
   ```

## Installation (Premium Version with APIs)

**⚠️ WARNING: This version requires paid API services**

1. **Install all dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
   ```

   Get API keys:
   - ElevenLabs: https://elevenlabs.io/ (requires payment)
   - OpenAI: https://platform.openai.com/ (requires payment)

## Usage

### Free Version (Recommended)

Run the free assistant:
```bash
python3 assistant_free.py
```

### Premium Version

Run the premium assistant (requires API keys):
```bash
python3 assistant.py
```

### Voice Commands

- Speak naturally to ask questions or have conversations
- Say **"exit"**, **"quit"**, or **"goodbye"** to stop the assistant
- Say **"list voices"** to see available ElevenLabs voices (premium only)
- Press **Ctrl+C** to force exit

## Customization

### Free Version

**Change AI Model:**
Edit `assistant_free.py` line 68 to use a different model:
```python
"model": "llama3.2",  # Options: llama2, llama3.2, mistral, codellama, etc.
```

Install new models with:
```bash
ollama pull llama3.2
ollama pull mistral
```

**Adjust Voice:**
The free version uses macOS `say` command. Change the voice:
```bash
say -v "?"  # List available voices
```

Edit line 97 in `assistant_free.py`:
```python
subprocess.run(["say", "-v", "Samantha", text], check=True)
```

### Premium Version

**Change Voice:**
1. Run the assistant and say "list voices" to see available options
2. Copy the desired voice ID
3. Update `ELEVENLABS_VOICE_ID` in your `.env` file

**Adjust AI Model:**
Edit `assistant.py` line 71 to change the model:
```python
model="gpt-4o-mini",  # Options: gpt-4o-mini, gpt-4o, gpt-3.5-turbo, etc.
```

**Modify System Prompt:**
Edit the `conversation_history` initialization in `assistant.py` to change the assistant's personality:
```python
conversation_history = [
    {"role": "system", "content": "Your custom prompt here"}
]
```

## Troubleshooting

### Free Version

**"Ollama is not installed or not running":**
```bash
brew services start ollama
# Wait a few seconds, then try again
```

**"API returned status code: 404":**
The AI model isn't downloaded:
```bash
ollama pull llama2
```

**Slow AI responses:**
- First response is always slower (model loading)
- Use a smaller/faster model: `ollama pull llama3.2:1b`
- Upgrade your Mac's RAM or use a smaller model

### Both Versions

**Microphone Issues:**
- Ensure your microphone is connected and selected as the default input device
- Grant microphone permissions: System Settings → Privacy & Security → Microphone → Enable for Terminal
- Speak closer to the microphone
- Reduce background noise

**"Could not understand audio":**
- Speak more clearly and slowly
- Check that your microphone is working: `say "test"`
- Try adjusting `energy_threshold` in the code (line 39)

**Audio Playback Issues:**
- Ensure speakers/headphones are connected
- Check system audio settings
- Test with: `say "test"`

### Premium Version Only

**API Errors:**
- Verify your API keys are correct and have available credits
- Add payment method to OpenAI and ElevenLabs accounts
- Check your internet connection

## Cost Considerations

### Free Version
- ✅ **$0** - Completely free!
- Uses local AI (Ollama)
- Uses macOS built-in TTS
- Google Speech Recognition (free tier)

### Premium Version
- 💰 **OpenAI**: ~$0.01-0.03 per conversation (GPT-4o-mini)
- 💰 **ElevenLabs**: ~$0.01-0.05 per response (depends on length)
- ✅ **Google Speech Recognition**: Free for basic usage

**Estimated cost per 10-minute conversation:** $0.50-$2.00

## Future Improvements

- [ ] Add wake word detection ("Hey Assistant")
- [ ] Implement conversation memory across sessions
- [ ] Add web UI for configuration
- [ ] Support for other languages
- [ ] Integration with smart home devices
- [ ] Better formant preservation for voice responses
- [ ] Context-aware responses with RAG (Retrieval Augmented Generation)

## Comparison: Free vs Premium

| Feature | Free Version | Premium Version |
|---------|--------------|------------------|
| Cost | $0 | ~$0.50-$2/conversation |
| AI Quality | Good (Llama2) | Excellent (GPT-4o-mini) |
| Voice Quality | Natural (macOS TTS) | Highly realistic (ElevenLabs) |
| Response Speed | 2-5 seconds | 1-3 seconds |
| Privacy | 100% local | Data sent to APIs |
| Setup Complexity | Easy | Medium (API keys) |
| Internet Required | No (after model download) | Yes |

## License

MIT License - Feel free to modify and use for your projects!
