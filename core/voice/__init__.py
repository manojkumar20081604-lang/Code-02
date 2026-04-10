"""
============================================================
VOICE MODULE - Voice Interaction
============================================================
Speech recognition and synthesis
"""

import asyncio
import threading
from typing import Optional, Callable
import logging

logger = logging.getLogger("Voice")


class VoiceEngine:
    """
    Voice interaction engine
    - Speech recognition
    - Text-to-speech
    - Voice activity detection
    """
    
    def __init__(self):
        self.is_listening = False
        self.is_speaking = False
        self.voice_callback: Optional[Callable] = None
        self.current_voice = "en-US-JennyNeural"
    
    async def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen for voice input"""
        
        if self.is_listening:
            return None
        
        self.is_listening = True
        
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                logger.info("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=timeout)
            
            # Recognize speech
            text = recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
            return None
        finally:
            self.is_listening = False
    
    async def speak(self, text: str, voice: str = None) -> bool:
        """Speak text using TTS"""
        
        if self.is_speaking:
            return False
        
        self.is_speaking = True
        
        try:
            voice_to_use = voice or self.current_voice
            
            # Try edge-tts first (better quality)
            try:
                await self._speak_edge(text, voice_to_use)
            except ImportError:
                # Fallback to pyttsx3
                self._speak_pyttsx3(text)
            
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
        finally:
            self.is_speaking = False
    
    async def _speak_edge(self, text: str, voice: str) -> None:
        """Speak using Microsoft Edge TTS"""
        
        import tempfile
        import os
        from edge_tts import Communicate
        
        mp3_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        mp3_file.close()
        
        try:
            communicate = Communicate(text=text, voice=voice, rate='+10%', pitch='+5Hz')
            await communicate.save(mp3_file.name)
            
            # Play the audio
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(mp3_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            
        finally:
            try:
                os.unlink(mp3_file.name)
            except:
                pass
    
    def _speak_pyttsx3(self, text: str) -> None:
        """Speak using pyttsx3 (offline fallback)"""
        
        import pyttsx3
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    
    def set_voice(self, voice: str) -> None:
        """Set the TTS voice"""
        self.current_voice = voice
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        return [
            {"id": "en-US-JennyNeural", "name": "Jenny (Female)", "gender": "Female"},
            {"id": "en-US-AriaNeural", "name": "Aria (Female)", "gender": "Female"},
            {"id": "en-US-GuyNeural", "name": "Guy (Male)", "gender": "Male"},
            {"id": "en-GB-LibbyNeural", "name": "Libby (UK Female)", "gender": "Female"},
            {"id": "en-AU-NatashaNeural", "name": "Natasha (AU Female)", "gender": "Female"},
            {"id": "en-IN-NeerjaExpressiveNeural", "name": "Neerja (IN Female)", "gender": "Female"}
        ]
    
    def start_continuous_listening(self, callback: Callable) -> None:
        """Start continuous voice listening in background"""
        
        self.voice_callback = callback
        
        def listen_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.voice_callback:
                try:
                    text = loop.run_until_complete(self.listen(timeout=5))
                    if text and self.voice_callback:
                        self.voice_callback(text)
                except Exception as e:
                    logger.error(f"Continuous listening error: {e}")
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
    
    def stop_continuous_listening(self) -> None:
        """Stop continuous listening"""
        self.voice_callback = None
