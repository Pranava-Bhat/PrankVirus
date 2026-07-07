# sound_manager.py
import os
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class SoundManager:
    """Handles continuous playback of the chosen audio file."""
    
    def __init__(self, audio_path):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Ensure the path is absolute so Qt can find it easily
        abs_path = os.path.abspath(audio_path)
        self.player.setSource(QUrl.fromLocalFile(abs_path))
        
        # Loop infinitely
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.audio_output.setVolume(1.0)
        
    def start_playing(self):
        """Starts the audio looping."""
        self.player.play()
        
    def stop_playing(self):
        """Stops the audio immediately."""
        self.player.stop()
