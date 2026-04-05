import pygame
import os


class MusicPlayer:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.playlist = []

        if os.path.exists(music_folder):
            self.playlist = [
                os.path.join(music_folder, file)
                for file in os.listdir(music_folder)
                if file.endswith(".wav") or file.endswith(".mp3")
            ]

        self.playlist.sort()
        self.current_index = 0
        self.is_playing = False

    def load_track(self):
        if self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_index])

    def play(self):
        if self.playlist:
            self.load_track()
            pygame.mixer.music.play()
            self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play()

    def previous_track(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play()

    def get_current_track_name(self):
        if self.playlist:
            name = os.path.basename(self.playlist[self.current_index])
            return name.replace("_", " ")
        return "No tracks found"

    def get_status(self):
        if self.is_playing:
            return "Playing"
        return "Stopped"

    def get_position_seconds(self):
        pos = pygame.mixer.music.get_pos()
        if pos == -1:
            return 0
        return pos // 1000