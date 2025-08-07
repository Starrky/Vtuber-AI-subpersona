# Vtuber-AI-subpersona

A project for creating AI-powered VTuber personas.

## Text-to-Speech Loop Script

This repository includes a text-to-speech script that runs in a loop waiting for input, using the Kokoro TTS library.

### Features

- Voice cloning capability using a reference audio file
- Continuous text-to-speech conversion in a loop
- Saves output audio files with timestamps
- Automatically plays generated audio after creation

### Requirements

- Python 3.13 or higher
- Kokoro TTS library and its dependencies
- A reference audio file and its corresponding text transcript

### Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Usage

1. Run the script:
   ```
   python tts_loop.py
   ```
   
   The script will use default reference audio and text from the repository.

2. Alternatively, you can specify custom reference audio and text:
   ```
   python tts_loop.py --ref-file "path/to/audio.wav" --ref-text "text in the audio"
   ```
   
   Examples:
   ```
   # Run with default settings
   python tts_loop.py
   
   # Use a custom reference audio and text
   python tts_loop.py --ref-file "my_voice.wav" --ref-text "This is my voice sample"
   
   # Disable audio playback (only save files)
   python tts_loop.py --no-play
   
   # Set a lower volume for playback
   python tts_loop.py --volume 0.5
   
   # Combine multiple options
   python tts_loop.py --ref-file "custom_voice.mp3" --model "Kokoro_Base" --volume 0.7
   ```

   Available command-line arguments:
   - `--ref-file`: Path to reference audio file (default: Audio/Reference/voice_preview_myrddin - magical narrator & wise mentor.mp3)
   - `--ref-text`: Text spoken in the reference audio (default: "Welcome to the realm of magic and wisdom") - Note: This text is only used for voice cloning and is not read aloud
   - `--model`: Model to use (default: Kokoro_Base)
   - `--no-play`: Disable automatic audio playback (files will still be saved)
   - `--volume`: Set volume level for audio playback (0.0 to 1.0, default: 1.0)

3. Enter text to convert to speech. The script will:
   - Convert your text to speech using the voice from the reference audio
   - Save the output as a WAV file in the `tts_output` directory
   - Automatically play the generated audio (unless disabled with --no-play)
   - Continue waiting for more input

4. Type 'exit' to quit the program

### Output

All generated speech files are saved in the `tts_output` directory with timestamps in their filenames.

### Notes

- The quality of voice cloning depends on the quality and length of the reference audio
- For best results, use a clear reference audio with minimal background noise
- The Kokoro TTS library requires significant computational resources, especially for the first inference
- The reference text is only used for voice cloning and is not read aloud in the generated speech
- Even though the reference text is not read aloud, it's still important to provide accurate text that matches the reference audio for optimal voice cloning results
=======
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

