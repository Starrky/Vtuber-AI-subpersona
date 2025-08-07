#!/usr/bin/env python3
"""
Speech to Text Script for Vtuber-AI-subpersona

This script listens for a wake word ("Cypher") using the default system microphone,
then transcribes the following speech to text using Google's Speech Recognition API,
and saves the transcribed text to a file for use by other scripts.
"""

import speech_recognition as sr
import time
import os
from datetime import datetime

# File to store the transcribed text
OUTPUT_FILE = "transcribed_speech.txt"

# Wake word that activates the speech recognition
WAKE_WORD = "cypher"

def listen_for_wake_word(recognizer, microphone):
    """
    Listen specifically for the wake word.
    
    Args:
        recognizer (Recognizer): Speech recognition object
        microphone (Microphone): Microphone object
    
    Returns:
        bool: True if wake word was detected, False otherwise
    """
    # Check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    
    # Listen for the wake word
    with microphone as source:
        print(f"Waiting for wake word '{WAKE_WORD.capitalize()}'...")
        # Adjust for ambient noise before each listening session
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Increased timeout and phrase time limit for better recognition
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return False
    
    # Try to recognize the wake word
    try:
        text = recognizer.recognize_google(audio).lower()
        print(f"Heard: {text}")
        
        # More flexible matching - check for variations of the wake word
        # 1. Exact match
        if WAKE_WORD in text:
            print(f"Wake word '{WAKE_WORD.capitalize()}' detected!")
            return True
            
        # 2. Check for common misspellings/misrecognitions
        common_variations = ["cipher", "sifer", "sipher", "cyfer", "psy fur", "sigh fur", "sci fur"]
        for variation in common_variations:
            if variation in text:
                print(f"Wake word variation '{variation}' detected, accepting as '{WAKE_WORD.capitalize()}'!")
                return True
                
        # 3. Check if any word in the text is similar to the wake word
        words = text.split()
        for word in words:
            # Simple similarity check - if the word starts with 's' or 'c' and has 'f' or 'ph' in it
            if (word.startswith('s') or word.startswith('c')) and ('f' in word or 'ph' in word):
                print(f"Possible wake word variation '{word}' detected, accepting as '{WAKE_WORD.capitalize()}'!")
                return True
                
        print("Wake word not detected in: " + text)
        return False
    except sr.RequestError:
        print("API unavailable")
        return False
    except sr.UnknownValueError:
        # Speech was unintelligible or no speech detected
        print("Could not understand audio")
        return False

def recognize_speech_from_mic(recognizer, microphone):
    """
    Transcribe speech from recorded microphone data.
    
    Args:
        recognizer (Recognizer): Speech recognition object
        microphone (Microphone): Microphone object
    
    Returns:
        dict: Response object with transcription results and error status
    """
    # Check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # Set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # Adjust the recognizer sensitivity to ambient noise and record audio
    with microphone as source:
        print("Adjusting for ambient noise... Please wait.")
        # Shorter duration for ambient noise adjustment to be more responsive
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Increase energy threshold for better noise filtering
        recognizer.energy_threshold = 300  # Default is usually around 300
        recognizer.dynamic_energy_threshold = True  # Automatically adjust based on ambient noise
        
        print("Listening for command... Speak now!")
        try:
            # Increased timeout for better user experience
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            response["success"] = False
            response["error"] = "Listening timed out"
            return response

    # Try to recognize the speech in the recording
    try:
        # Try with Google's speech recognition first (most accurate)
        response["transcription"] = recognizer.recognize_google(audio)
        print(f"Recognized: {response['transcription']}")
    except sr.RequestError:
        # API was unreachable or unresponsive
        print("Google API unavailable, trying alternative recognition method...")
        try:
            # Fall back to Sphinx (offline) if Google is unavailable
            response["transcription"] = recognizer.recognize_sphinx(audio)
            print(f"Recognized (using fallback): {response['transcription']}")
        except:
            response["success"] = False
            response["error"] = "All speech recognition services unavailable"
    except sr.UnknownValueError:
        # Speech was unintelligible
        print("Speech was unintelligible, please try speaking more clearly")
        response["success"] = False
        response["error"] = "Unable to recognize speech"

    return response

def save_transcription(text):
    """
    Save the transcribed text to a file with timestamp.
    
    Args:
        text (str): The transcribed text to save
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {text}\n")
    print(f"Saved: {text}")

def main():
    """
    Main function to run the speech recognition loop.
    """
    # Create a recognizer instance
    recognizer = sr.Recognizer()
    
    # Create a microphone instance using the default system microphone
    try:
        microphone = sr.Microphone()
        print("Successfully initialized microphone")
    except Exception as e:
        print(f"ERROR: Could not initialize microphone: {e}")
        print("Please check your microphone connection and try again.")
        return
    
    print(f"Speech to Text service started. Transcriptions will be saved to {OUTPUT_FILE}")
    print(f"Say '{WAKE_WORD.capitalize()}' to activate speech recognition.")
    
    # Ensure the output file exists
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write("# Speech Transcription Log\n\n")
    
    # Adjust for ambient noise once at startup
    try:
        with microphone as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Ambient noise adjustment complete")
    except Exception as e:
        print(f"WARNING: Could not adjust for ambient noise: {e}")
        print("Continuing without initial ambient noise adjustment.")
    
    # Track consecutive failures to detect potential system issues
    consecutive_failures = 0
    max_consecutive_failures = 5
    
    # Continuous recognition loop
    while True:
        try:
            # First stage: Listen for wake word
            wake_word_detected = listen_for_wake_word(recognizer, microphone)
            
            # Reset failure counter on successful operation
            if wake_word_detected:
                consecutive_failures = 0
                
                # Second stage: If wake word detected, listen for command
                result = recognize_speech_from_mic(recognizer, microphone)
                
                if result["success"] and result["transcription"]:
                    # Save the transcribed text
                    save_transcription(result["transcription"])
                    print("Ready to listen for wake word again...")
                elif result["error"]:
                    print(f"ERROR: {result['error']}")
                    print("Please try again.")
                else:
                    print("No speech detected after wake word. Try again.")
                
                # Small delay before returning to listening for wake word
                time.sleep(1)
            else:
                # Small delay before trying to detect wake word again
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nSpeech recognition service stopped by user.")
            break
        except sr.RequestError:
            print("Network error: Speech recognition service unavailable.")
            print("Will continue trying...")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            consecutive_failures += 1
            
            # If we have too many consecutive failures, try to reset the system
            if consecutive_failures >= max_consecutive_failures:
                print(f"Detected {consecutive_failures} consecutive failures. Attempting to reset...")
                try:
                    # Try to reinitialize the recognizer and microphone
                    recognizer = sr.Recognizer()
                    microphone = sr.Microphone()
                    print("System reset successful. Continuing...")
                    consecutive_failures = 0
                except Exception as reset_error:
                    print(f"Could not reset system: {reset_error}")
                    print("You may need to restart the application manually.")
                    
            time.sleep(2)  # Delay before retrying to prevent rapid error loops

if __name__ == "__main__":
    main()