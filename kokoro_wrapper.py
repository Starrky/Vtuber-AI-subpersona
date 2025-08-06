#!/usr/bin/env python3
"""
Wrapper for Kokoro TTS 0.9.4 to provide compatibility with the KokoroTTS interface
used in the tts_loop.py script.
"""
import os
import wave
import torch
import numpy as np
from typing import Optional, Union
from kokoro import KModel, KPipeline

class KokoroTTS:
    """
    Wrapper class for Kokoro TTS 0.9.4 that provides a similar interface to what's
    expected in tts_loop.py.
    """
    def __init__(self, model: str = "Kokoro_Base", device: Optional[Union[str, torch.device]] = None):
        """
        Initialize the KokoroTTS wrapper.
        
        Args:
            model: The model name to use (default: "Kokoro_Base")
            device: The device to use for PyTorch operations (default: None)
        """
        self.model_name = model
        self.device = device if device is not None else (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        
        # Store the actual device the model is using (will be updated after verification)
        self.actual_device = self.device
        
        # Initialize the KModel
        print(f"Initializing KModel with model: {model}")
        self.kmodel = KModel()
        
        # Initialize the KPipeline for English (American)
        # We'll use American English as the default language
        self.pipeline = KPipeline(lang_code="a")
        
        # Add a 'model' attribute for compatibility with the checks in tts_loop.py
        self.model = self.kmodel
        
        # Try to move the model to the specified device
        self._move_model_to_device()
        
        print(f"KokoroTTS wrapper initialized with model: {model} on device: {self.device}")
        
    def _move_model_to_device(self):
        """
        Move the model to the specified device (GPU if available).
        """
        if self.device.type == 'cpu':
            print("Using CPU for model inference.")
            return
            
        print(f"Attempting to move model to {self.device}...")
        
        # Try different approaches to move the model to the device
        try:
            # Approach 1: Try to use the .to() method if available
            if hasattr(self.kmodel, 'to'):
                print("Moving model using .to() method...")
                self.kmodel.to(self.device)
                
            # Approach 2: Try to move model parameters if available
            elif hasattr(self.kmodel, 'parameters'):
                print("Moving model parameters...")
                for param in self.kmodel.parameters():
                    param.data = param.data.to(self.device)
                    
            # Approach 3: Check if there are any modules that can be moved
            elif hasattr(self.kmodel, 'modules'):
                print("Moving model modules...")
                for module in self.kmodel.modules():
                    if hasattr(module, 'to'):
                        module.to(self.device)
            
            # Approach 4: Try to access internal models if they exist
            if hasattr(self.kmodel, 'model'):
                print("Found internal model. Moving to device...")
                if hasattr(self.kmodel.model, 'to'):
                    self.kmodel.model.to(self.device)
                    
            # Verify that the model is on the correct device
            self._verify_model_device()
            
        except Exception as e:
            print(f"Warning: Could not move model to {self.device}: {e}")
            print("The model will run on CPU, which may be slower.")
            
    def _verify_model_device(self):
        """
        Verify that the model is on the correct device.
        """
        actual_device = None
        
        # Try different approaches to check the model's device
        try:
            # Approach 1: Check model parameters
            if hasattr(self.kmodel, 'parameters'):
                for param in self.kmodel.parameters():
                    actual_device = param.device
                    print(f"Model parameter device: {actual_device}")
                    break
                    
            # Approach 2: Check internal model if it exists
            elif hasattr(self.kmodel, 'model') and hasattr(self.kmodel.model, 'parameters'):
                for param in self.kmodel.model.parameters():
                    actual_device = param.device
                    print(f"Internal model parameter device: {actual_device}")
                    break
                    
            # Approach 3: Check modules
            elif hasattr(self.kmodel, 'modules'):
                for module in self.kmodel.modules():
                    if hasattr(module, 'parameters'):
                        for param in module.parameters():
                            actual_device = param.device
                            print(f"Module parameter device: {actual_device}")
                            break
                        if actual_device is not None:
                            break
            
            # Update the actual device if found
            if actual_device is not None:
                self.actual_device = actual_device
                if actual_device.type != self.device.type:
                    print(f"Warning: Model is on {actual_device}, but requested device is {self.device}")
                else:
                    print(f"Confirmed: Model is on {actual_device} as requested")
            else:
                print("Could not determine model device")
                
        except Exception as e:
            print(f"Error verifying model device: {e}")
    
    def get_device(self):
        """
        Return the device being used by the model.
        This method is added for compatibility with the checks in tts_loop.py.
        """
        return self.actual_device
    
    def generate_speech(
        self,
        reference_audio: str,
        reference_text: str,
        text: str,
        output_file: str
    ) -> None:
        """
        Generate speech using the Kokoro TTS engine.
        
        This method attempts to provide compatibility with the expected interface,
        but since Kokoro 0.9.4 doesn't support voice cloning from reference audio,
        it will use a default voice instead.
        
        Args:
            reference_audio: Path to reference audio file (not used in this version)
            reference_text: Text spoken in the reference audio (not used in this version)
            text: Text to convert to speech
            output_file: Path to save the generated audio
        """
        print(f"Warning: Kokoro 0.9.4 doesn't support voice cloning from reference audio.")
        print(f"Using default voice 'af_heart' instead.")
        
        # Use a default voice since we can't clone from reference audio
        voice = "af_heart"
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Generate the speech
        print(f"Generating speech for: '{text}'")
        
        # Ensure the model is on the correct device before inference
        self._ensure_model_on_device()
        
        # Open the output file
        with wave.open(output_file, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
            wav_file.setframerate(24000)  # Sample rate
            
            # Generate audio using the pipeline
            for result in self.pipeline(text, voice=voice, model=self.kmodel):
                if result.audio is None:
                    continue
                
                # Get the audio tensor and ensure it's on CPU for numpy conversion
                audio_tensor = result.audio
                if hasattr(audio_tensor, 'device') and audio_tensor.device.type != 'cpu':
                    audio_tensor = audio_tensor.cpu()
                
                # Convert the audio tensor to bytes and write to the file
                audio_bytes = (audio_tensor.numpy() * 32767).astype(np.int16).tobytes()
                wav_file.writeframes(audio_bytes)
        
        print(f"Speech generated successfully! Saved to {output_file}")
        
    def _ensure_model_on_device(self):
        """
        Ensure the model is on the correct device before inference.
        This is called before each inference to make sure the model is on the GPU.
        """
        # If the actual device is already the requested device, no need to do anything
        if hasattr(self, 'actual_device') and self.actual_device.type == self.device.type:
            return
            
        # Otherwise, try to move the model to the device again
        print("Model not on the requested device. Attempting to move it...")
        self._move_model_to_device()