import speech_recognition as sr
import threading
import time

class VoiceRecognition:
    def __init__(self):
        # Initialize the recognizer and microphone
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_recording = False
        self.audio_data = None
        self.recording_thread = None
        
        # Adjust for ambient noise once during initialization
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def start_recording(self):
        """Start recording audio - call this when button is pressed"""
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.audio_data = None
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        return True
    
    def _record_audio(self):
        """Internal method to record audio"""
        with self.microphone as source:
            try:
                self.audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=None)
            except sr.WaitTimeoutError:
                pass
    
    def stop_recording(self):
        """Stop recording audio - call this when button is released"""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        # Give a moment for the audio thread to complete
        time.sleep(0.3)
        
        if self.recording_thread and self.recording_thread.is_alive():
            # Wait for the recording thread to finish
            self.recording_thread.join(timeout=1.0)
        
        # Process the audio if available
        if self.audio_data:
            return self.process_audio()
        
        return None
    
    def process_audio(self):
        """Process the recorded audio and return the recognized text"""
        if not self.audio_data:
            return None
        
        try:
            # Using Google's speech recognition service by default
            text = self.recognizer.recognize_google(self.audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return None
    
    def is_currently_recording(self):
        """Check if recording is in progress"""
        return self.is_recording

# Example usage for testing the backend
if __name__ == "__main__":
    # Create the backend engine
    voice_engine = VoiceRecognition()
    
    print("Press Enter to simulate button press (start recording)")
    input()
    voice_engine.start_recording()
    print("Recording... Press Enter to simulate button release (stop recording)")
    
    input()
    text = voice_engine.stop_recording()
    
    if text:
        print(f"Recognized text: {text}")
    else:
        print("No speech recognized")