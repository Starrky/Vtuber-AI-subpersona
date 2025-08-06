#!/usr/bin/env python3
import os
import time
import argparse
import wave
import pyaudio
import warnings
import torch
from kokoro_wrapper import KokoroTTS  # Using our wrapper for Kokoro TTS 0.9.4

# Filter out warnings from PyTorch
warnings.filterwarnings("ignore", message="Torch was not compiled with flash attention")
warnings.filterwarnings("ignore", message="dropout option adds dropout after all but last recurrent layer")
warnings.filterwarnings("ignore", message="`torch.nn.utils.weight_norm` is deprecated")
print(torch.version.cuda)
def play_audio(file_path, volume=1.0, delete_after=False):
    if not os.path.exists(file_path):
        print(f"Error: Audio file not found: {file_path}")
        return

    # Validate volume level
    volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0

    try:
        # Open the wave file
        wf = wave.open(file_path, 'rb')

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Open a stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read data in chunks and play
        chunk_size = 1024
        data = wf.readframes(chunk_size)

        print(f"Playing audio at volume {volume:.1f}... Press Ctrl+C to stop.")
        while data:
            # Apply volume adjustment if needed
            if volume != 1.0 and wf.getsampwidth() == 2:  # 16-bit audio
                # Convert bytes to array of integers
                import array
                samples = array.array('h', data)
                # Apply volume
                for i in range(len(samples)):
                    samples[i] = int(samples[i] * volume)
                # Convert back to bytes
                data = samples.tobytes()

            stream.write(data)
            data = wf.readframes(chunk_size)

        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio playback completed.")

        # Delete the file if requested
        if delete_after and os.path.exists(file_path):
            try:
                print(f"Waiting 1 minute before deleting file to ensure it's not in use...")
                time.sleep(60)  # Sleep for 1 minute before attempting to delete
                os.remove(file_path)
                print(f"File deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
    except Exception as e:
        print(f"Error playing audio: {e}")
        print("Continuing with the script...")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Text-to-Speech Loop using Kokoro TTS')
    parser.add_argument('--ref-file', default='Audio/Reference/voice_preview_myrddin - magical narrator & wise mentor.mp3',
                        help='Path to reference audio file (default: Audio/Reference/voice_preview_myrddin - magical narrator & wise mentor.mp3)')
    parser.add_argument('--ref-text', default='Through the mists of time, I\'ve discovered that dragons are remarkably ticklish behind their ears. Though, I would not recommend testing this theory.',
                        help='Text spoken in the reference audio (default: "Through the mists of time, I\'ve discovered that dragons are remarkably ticklish behind their ears. Though, I would not recommend testing this theory.")')
    parser.add_argument('--model', default='Kokoro_Base',
                        help='Model to use (default: Kokoro_Base)')
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cuda',
                        help='Device to use for PyTorch operations (default: cuda if available, otherwise cpu)')
    parser.add_argument('--no-play', action='store_true',
                        help='Disable automatic audio playback')
    parser.add_argument('--volume', type=float, default=1.0,
                        help='Volume level for audio playback (0.0 to 1.0, default: 1.0)')
    args = parser.parse_args()
    
    # Set PyTorch to use the specified device
    device = torch.device(args.device)
    print(f"Using device: {device}")
    
    # Check if CUDA is available and being used
    if torch.cuda.is_available():
        print(f"CUDA is available. Found {torch.cuda.device_count()} CUDA device(s).")
        print(f"Current CUDA device: {torch.cuda.current_device()} - {torch.cuda.get_device_name(torch.cuda.current_device())}")
        
        # Force PyTorch to use CUDA for all operations if CUDA is requested
        if args.device.startswith('cuda'):
            torch.set_default_tensor_type('torch.cuda.FloatTensor')
            print("Set default tensor type to CUDA tensors.")
            
            # Verify that PyTorch is using CUDA
            test_tensor = torch.ones(1)
            print(f"Test tensor device: {test_tensor.device}")
            if test_tensor.device.type != 'cuda':
                print("Warning: PyTorch is not using CUDA for tensors despite configuration.")
    else:
        print("CUDA is not available. Using CPU.")
        
    if args.device.startswith('cuda') and not torch.cuda.is_available():
        print("Warning: CUDA is not available. Falling back to CPU.")
        device = torch.device('cpu')

    # Check if reference audio file exists
    ref_file = args.ref_file
    if not os.path.exists(ref_file):
        print(f"Warning: Default reference file not found: {ref_file}")
        ref_file = input("Enter path to reference audio file: ")
        while not os.path.exists(ref_file):
            print(f"File not found: {ref_file}")
            ref_file = input("Enter path to reference audio file: ")

    # Use the reference text for voice cloning
    # This text should match what is spoken in the reference audio file
    ref_text = args.ref_text

    # Initialize the TTS engine with specified model and device
    print("Initializing Kokoro TTS engine...")
    try:
        # Try to initialize with device parameter
        tts = KokoroTTS(model=args.model, device=device)
        print(f"Kokoro TTS engine initialized successfully with model: {args.model} on device: {device}!")
    except TypeError as e:
        # If device parameter is not supported, try without it
        if "unexpected keyword argument 'device'" in str(e):
            print("Warning: KokoroTTS does not support the 'device' parameter. Initializing without explicit device.")
            tts = KokoroTTS(model=args.model)
            print(f"Kokoro TTS engine initialized successfully with model: {args.model}!")
            print("Note: PyTorch should still use CUDA for operations due to the default tensor type setting.")
        else:
            # Re-raise if it's a different TypeError
            raise
            
    # Try to verify if the model is using CUDA
    try:
        # Check if the model has a 'model' attribute that might contain the PyTorch model
        if hasattr(tts, 'model') and hasattr(tts.model, 'parameters'):
            # Check the device of the first parameter
            for param in tts.model.parameters():
                print(f"Model parameter device: {param.device}")
                break
        # Alternative: check if there's a get_device method
        elif hasattr(tts, 'get_device'):
            print(f"Model device: {tts.get_device()}")
    except Exception as e:
        print(f"Note: Could not verify model device. {str(e)}")

    print("\nText-to-Speech Loop")
    print("Enter text to convert to speech. Type 'exit' to quit.")

    # Create output directory if it doesn't exist
    output_dir = "tts_output"
    os.makedirs(output_dir, exist_ok=True)

    while True:
        # Get user input
        user_input = input("\nEnter text: ")

        # Check if user wants to exit
        if user_input.lower() == 'exit':
            print("Exiting text-to-speech loop. Goodbye!")
            break

        # Skip empty input
        if not user_input.strip():
            print("Empty input. Please enter some text.")
            continue

        try:
            # Convert text to speech
            print(f"Converting: '{user_input}'")
            output_file = os.path.join(output_dir, f"output_{int(time.time())}.wav")
            tts.generate_speech(
                reference_audio=ref_file,
                reference_text=ref_text,
                text=user_input,
                output_file=output_file
            )
            print(f"Speech generated successfully! Saved to {output_file}")

            # Play the generated audio if not disabled
            if not args.no_play:
                play_audio(output_file, volume=args.volume, delete_after=True)
            else:
                print("Audio playback disabled. Audio file saved to disk.")
        except Exception as e:
            print(f"Error generating speech: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")