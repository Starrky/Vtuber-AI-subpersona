# Vtuber-AI-subpersona

## Speech to Text Component

This component listens for a wake word ("Cypher") using the default system microphone, then transcribes the following speech to text, and saves the transcribed text to a file for use by other components of the system.

### Features

- Uses the default system microphone for audio input
- Activates only when the wake word "Cypher" is detected (similar to voice assistants)
  - Recognizes common variations and similar-sounding words (like "cipher", "sipher", etc.)
  - Flexible matching for better wake word detection
- Transcribes speech using Google's Speech Recognition API
  - Falls back to offline recognition if Google API is unavailable
- Saves transcribed text with timestamps to a file
- Advanced error handling and recovery mechanisms
  - Automatically adjusts to ambient noise
  - Recovers from temporary network issues
  - Attempts system reset after consecutive failures

### Requirements

- Python 3.6 or higher
- SpeechRecognition library (`pip install SpeechRecognition`)
- PyAudio library (`pip install PyAudio`)

### Usage

Run the script with:

```
python SpeechToText.py
```

Once the script is running:

1. Say the wake word "Cypher" to activate speech recognition
   - The system will recognize variations like "cipher", "sipher", etc.
   - Speak clearly and at a normal volume for best recognition
   - The console will show "Wake word detected!" when successful
   
2. After the wake word is detected, speak your command or message
   - You'll have up to 20 seconds to speak your command
   - The system will adjust for ambient noise automatically
   
3. The transcribed speech will be saved to `transcribed_speech.txt` in the same directory
   - Check the console for confirmation of successful transcription
   - If recognition fails, the system will provide feedback and return to listening mode

Only speech that follows the wake word will be transcribed and saved.

### Troubleshooting

If the system doesn't recognize the wake word:
- Try speaking more clearly and slightly louder
- Reduce background noise if possible
- Try variations like "Cipher" if "Cypher" isn't being recognized
- Check that your microphone is working properly

If you encounter persistent issues:
- The system will attempt to reset itself after multiple failures
- Check the console for specific error messages
- Restart the script if necessary

### Output Format

The transcribed text is saved with timestamps in the following format:

```
[YYYY-MM-DD HH:MM:SS] Transcribed text here
```

Other scripts can read this file to access the transcribed speech data.